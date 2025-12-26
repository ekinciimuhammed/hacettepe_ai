import requests
import json
from pipeline.vector_store import search_vectors
from pipeline.embedder import get_embedding
from config import TOP_K, OLLAMA_BASE_URL, LLM_MODEL, MIN_SCORE_THRESHOLD, SYSTEM_PROMPT
from config import ENABLE_HYBRID_RAG, VECTOR_WEIGHT, ENTITY_WEIGHT
from config import ENABLE_CACHE, CACHE_DIR, CACHE_MAX_AGE_HOURS

# Hybrid RAG için entity extractor
if ENABLE_HYBRID_RAG:
    from pipeline.entity_extractor import extract_entities, calculate_entity_overlap

# Cache
if ENABLE_CACHE:
    from pipeline.cache import QueryCache
    _query_cache = QueryCache(cache_dir=CACHE_DIR, max_age_hours=CACHE_MAX_AGE_HOURS)

def get_document_priority(filename, query=""):
    from config import DOCUMENT_PRIORITIES, DYNAMIC_BOOSTS
    
    filename_upper = filename.upper()
    query_lower = query.lower() if query else ""
    
    # 1. Base Static Priority
    priority = 1.0
    for key, multiplier in DOCUMENT_PRIORITIES.items():
        if key in filename_upper:
            priority = multiplier
            break
            
    # 2. Dynamic Context Boost
    # If the user asks about "Ranking", boost "SIRALAMASI" docs significantly
    for doc_key, keywords in DYNAMIC_BOOSTS.items():
        if doc_key in filename_upper:
            # Check if query matches this topic
            for keyword in keywords:
                if keyword in query_lower:
                    # Apply Turbo Boost (e.g. 1.5x on top of static)
                    # This ensures the specific directive overrides the general constitution
                    return priority * 1.5
                    
    return priority

def retrieve_context(query):
    """
    Retrieves relevant chunks from LanceDB based on query.
    Supports Hybrid RAG with entity-based re-ranking + Document Authority.
    """
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
    
    # Vector search - get more results for re-ranking
    search_limit = TOP_K * 2 if ENABLE_HYBRID_RAG else TOP_K
    results = search_vectors(query_embedding, limit=search_limit)
    
    if not results:
        return []
    
    # Hybrid RAG: Entity-based re-ranking + Doc Importance
    if ENABLE_HYBRID_RAG:
        # Extract entities from query
        query_entities = extract_entities(query)
        
        # Score each result
        scored_results = []
        for r in results:
            text = r.get("text") or r["text"]
            source = r.get("source") or r["source"]
            metadata_str = r.get("metadata", "{}")
            
            # Parse metadata
            try:
                chunk_entities = json.loads(metadata_str) if metadata_str else {}
            except Exception as e:
                chunk_entities = {}
            
            # 1. Vector Score
            distance = r.get('_distance', None)
            if distance is None:
                vector_score = r.get('_score', 0.5)
            else:
                vector_score = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
            
            # 2. Entity Score
            entity_score = calculate_entity_overlap(query_entities, chunk_entities)
            
            # 3. Base Score
            base_score = (VECTOR_WEIGHT * vector_score) + (ENTITY_WEIGHT * entity_score)
            
            # 4. Authority Boost
            priority_multiplier = get_document_priority(source, query)
            final_score = base_score * priority_multiplier
            
            scored_results.append({
                "text": text,
                "source": source,
                "score": final_score,
                "vector_score": vector_score,
                "entity_score": entity_score,
                "priority_boost": priority_multiplier,
                "_distance": distance
            })
        
        # Sort by final score (descending)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top K
        context_items = scored_results[:TOP_K]
        
        # Debug info
        print(f"\n🔍 Hybrid + Authority Search Results:")
        for i, item in enumerate(context_items[:3], 1):
            print(f"  [{i}] Final: {item['score']:.3f} | Base: {(item['score']/item['priority_boost']):.3f} x Boost: {item['priority_boost']}")
            print(f"      Source: {item['source']}")
        
    else:
        # Fallback for non-hybrid (should typically be enabled)
        context_items = []
        for r in results:
            context_items.append({
                "text": r.get("text"),
                "source": r.get("source")
            })
        
    return context_items

def generate_answer_enhanced(query):
    """
    Returns a dictionary:
    {
        "answer": str,
        "sources": list of str (filenames),
        "chunks": list of dicts {text, source, score},
        "intent": str
    }
    """
    # Check cache first
    if ENABLE_CACHE:
        cached_result = _query_cache.get(query)
        if cached_result:
            # If the cached result is a string (legacy), we might need to wrap it?
            # Ideally, we clear old cache, but for now assuming it handles dicts if we saved dicts.
            # If it's a dict, return it directly. 
            if isinstance(cached_result, dict):
                 return cached_result
            # If it's a string, it's legacy cache, let's ignore or wrap it.
            # Choosing to ignore legacy string cache for this enhanced function to avoid format errors
            pass 
            
    # --- 0. VERIFIED FAQ LAYER ---
    from pipeline.faq_manager import FAQManager
    faq_manager = FAQManager()
    faq_match = faq_manager.find_match(query)
    if faq_match:
        print(f"🛡️ FAQ HIT: {query}")
        return faq_match

    # --- INTENT GATING ---
    from pipeline.intent_router import IntentRouter, Intent
    
    router = IntentRouter()
    intent, suggestion = router.route(query)
    
    # 1. Handle Non-RAG Intents
    if intent != Intent.ACADEMIC_READY:
        return {
            "answer": suggestion if suggestion else "İsteğinizi anlayamadım.",
            "sources": [],
            "chunks": [],
            "intent": intent.value
        }
        
    # 2. Handle Academic RAG
    context_chunks = retrieve_context(query)
    
    if not context_chunks:
        return {
            "answer": "Bu konu hakkında elimdeki akademik belgelerde yeterli bilgi bulunmamaktadır.",
            "sources": [],
            "chunks": [],
            "intent": intent.value
        }

    context_text = "\n\n".join([f"--- Chunk from {c['source']} ---\n{c['text']}" for c in context_chunks])
    unique_sources = sorted(list(set([c['source'] for c in context_chunks])))

    prompt = f"""
    {SYSTEM_PROMPT}

    **CONTEXT (BAĞLAM):**
    {context_text}
    
    **SORU:**
    {query}
    
    **YANIT:**
    """
    
    # Call Generate API
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        final_answer = response.json()["response"]
        
        result = {
            "answer": final_answer,
            "sources": unique_sources,
            "chunks": context_chunks,
            "intent": intent.value
        }
        
        # Cache the result ONLY if we found valid sources (Academic Context)
        if ENABLE_CACHE and unique_sources:
            _query_cache.set(query, result)
            
        return result

    except Exception as e:
        return {
            "answer": f"Bir hata oluştu: {str(e)}",
            "sources": [],
            "chunks": [],
            "intent": "ERROR"
        }

def generate_answer(query):
    """
    Legacy wrapper that returns a string (for terminal/streamlit apps).
    """
    result = generate_answer_enhanced(query)
    text = result["answer"]
    
    if result["sources"]:
        text += f"\n\n**Kaynaklar:**\n" + ", ".join(result["sources"])
        
    if result["chunks"]:
        text += "\n\n**Kullanılan Chunklar:**\n"
        for i, c in enumerate(result["chunks"]):
            text += f"\n[{i+1}] ({c['source']}):\n{c['text']}\n"
            
    return text
