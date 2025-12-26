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

def retrieve_context(query):
    """
    Retrieves relevant chunks from LanceDB based on query.
    Supports Hybrid RAG with entity-based re-ranking.
    
    1. Embed query
    2. Search vector DB
    3. (Hybrid) Extract entities from query and chunks
    4. (Hybrid) Re-rank based on vector + entity scores
    """
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
    
    # Vector search - get more results for re-ranking
    search_limit = TOP_K * 2 if ENABLE_HYBRID_RAG else TOP_K
    results = search_vectors(query_embedding, limit=search_limit)
    
    if not results:
        return []
    
    # Hybrid RAG: Entity-based re-ranking
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
            
            # Vector similarity score (distance -> similarity)
            # LanceDB returns _distance (lower is better)
            # For L2 distance, typical range is 0-2 (0 = identical)
            # For cosine distance, range is 0-2 (0 = identical, 2 = opposite)
            distance = r.get('_distance', None)
            
            if distance is None:
                # Fallback: try to get score directly
                vector_score = r.get('_score', 0.5)
            else:
                # Convert distance to similarity
                # Normalize: assume max distance of 2.0
                # similarity = 1 - (distance / 2.0)
                vector_score = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
            
            # Entity overlap score
            entity_score = calculate_entity_overlap(query_entities, chunk_entities)
            
            # Combined score
            final_score = (VECTOR_WEIGHT * vector_score) + (ENTITY_WEIGHT * entity_score)
            
            scored_results.append({
                "text": text,
                "source": source,
                "score": final_score,
                "vector_score": vector_score,
                "entity_score": entity_score,
                "_distance": distance  # Debug için
            })
        
        # Sort by final score (descending)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top K
        context_items = scored_results[:TOP_K]
        
        # Debug info
        print(f"\n🔍 Hybrid RAG Search Results:")
        print(f"   Query entities: {list(query_entities.keys())}")
        for i, item in enumerate(context_items[:3], 1):
            dist_str = f"{item['_distance']:.4f}" if item['_distance'] is not None else "N/A"
            print(f"  [{i}] Score: {item['score']:.3f} (V:{item['vector_score']:.3f} + E:{item['entity_score']:.3f})")
            print(f"      Distance: {dist_str} | Source: {item['source']}")
            print(f"      Text preview: {item['text'][:80]}...")
        
    else:
        # Standard Vector RAG
        context_items = []
        for r in results:
            text = r.get("text") or r["text"]
            source = r.get("source") or r["source"]
            
            context_items.append({
                "text": text,
                "source": source
            })
        
    return context_items

def generate_answer(query):
    """
    RAG Pipeline with Caching:
    0. Check cache
    1. Retrieve context
    2. Build Prompt
    3. Call LLM
    4. Cache result
    """
    # Check cache first
    if ENABLE_CACHE:
        cached_answer = _query_cache.get(query)
        if cached_answer:
            return cached_answer
    
    context_chunks = retrieve_context(query)
    
    if not context_chunks:
        # Fallback if no context found (or empty DB)
        context_text = "No relevant context found in documents."
        sources_text = "None"
    else:
        context_text = "\n\n".join([f"--- Chunk from {c['source']} ---\n{c['text']}" for c in context_chunks])
        sources_text = ", ".join(set([c['source'] for c in context_chunks]))

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
            "temperature": 0.1  # Strict adherence to facts
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        final_answer = response.json()["response"]
        
        # Append sources to the final answer
        if sources_text and sources_text != "None":
            # Append Sources and also the actual text chunks
            sources_section = f"\n\n**Kaynaklar:**\n{sources_text}"
            
            # Format chunks nicely
            chunks_section = "\n\n**Kullanılan Chunklar:**\n"
            for i, chunk_data in enumerate(context_chunks):
                full_text = chunk_data['text']
                # Showing full text as requested
                chunks_section += f"\n[{i+1}] ({chunk_data['source']}):\n{full_text}\n"
            
            final_result = f"{final_answer}{sources_section}{chunks_section}"
            
            # Cache the result
            if ENABLE_CACHE:
                _query_cache.set(query, final_result, metadata={
                    "sources": sources_text,
                    "num_chunks": len(context_chunks)
                })
            
            return final_result
        
        # Cache simple answer too
        if ENABLE_CACHE:
            _query_cache.set(query, final_answer)
        
        return final_answer
    except Exception as e:
        error_msg = f"Error generating response: {e}"
        return error_msg
