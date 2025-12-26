"""
RAG Debug Script
Sorunun neden "Belge bulunmadığı için yanıt veremiyorum" döndüğünü analiz eder
"""

from pipeline.embedder import get_embedding
from pipeline.vector_store import search_vectors
from pipeline.entity_extractor import extract_entities
from config import TOP_K

print("=" * 80)
print("RAG DEBUG - Context Retrieval Analysis")
print("=" * 80)

# Test sorusu
query = "Hacettepe Üniversitesi ne zaman kuruldu?"
print(f"\nSoru: {query}")

# 1. Embedding oluştur
print("\n1️⃣ Embedding Oluşturma")
print("-" * 80)
query_embedding = get_embedding(query)
if query_embedding:
    print(f"✅ Embedding oluşturuldu (boyut: {len(query_embedding)})")
else:
    print("❌ Embedding oluşturulamadı!")
    exit(1)

# 2. Vector search
print("\n2️⃣ Vector Search")
print("-" * 80)
results = search_vectors(query_embedding, limit=TOP_K * 2)
print(f"Bulunan sonuç sayısı: {len(results)}")

if not results:
    print("❌ Hiç sonuç bulunamadı!")
    print("\nOlası nedenler:")
    print("  1. Veritabanı boş")
    print("  2. Embedding boyutu uyumsuz")
    print("  3. LanceDB bağlantı hatası")
    exit(1)

# 3. Distance analizi
print("\n3️⃣ Distance Analizi")
print("-" * 80)
for i, r in enumerate(results[:5], 1):
    distance = r.get('_distance', 'N/A')
    source = r.get('source', 'Unknown')
    text_preview = r.get('text', '')[:80]
    print(f"\n[{i}] Distance: {distance}")
    print(f"    Source: {source}")
    print(f"    Text: {text_preview}...")

# 4. Entity extraction
print("\n4️⃣ Entity Extraction")
print("-" * 80)
query_entities = extract_entities(query)
print(f"Query entities:")
for entity_type, values in query_entities.items():
    if values:
        print(f"  - {entity_type}: {values}")

# 5. Hybrid scoring simulation
print("\n5️⃣ Hybrid Scoring Simulation")
print("-" * 80)

from pipeline.entity_extractor import calculate_entity_overlap
import json

for i, r in enumerate(results[:5], 1):
    distance = r.get('_distance', 2.0)
    metadata_str = r.get('metadata', '{}')
    
    try:
        chunk_entities = json.loads(metadata_str) if metadata_str else {}
    except:
        chunk_entities = {}
    
    # Vector score
    vector_score = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
    
    # Entity score
    entity_score = calculate_entity_overlap(query_entities, chunk_entities)
    
    # Final score
    final_score = (0.7 * vector_score) + (0.3 * entity_score)
    
    print(f"\n[{i}] Final Score: {final_score:.3f}")
    print(f"    Vector: {vector_score:.3f} (distance: {distance})")
    print(f"    Entity: {entity_score:.3f}")
    print(f"    Source: {r.get('source', 'Unknown')}")

# 6. Sonuç
print("\n" + "=" * 80)
print("SONUÇ")
print("=" * 80)

if results:
    best_score = max([
        (0.7 * max(0.0, min(1.0, 1.0 - (r.get('_distance', 2.0) / 2.0)))) + 
        (0.3 * calculate_entity_overlap(query_entities, json.loads(r.get('metadata', '{}')) if r.get('metadata') else {}))
        for r in results[:5]
    ])
    
    print(f"En iyi skor: {best_score:.3f}")
    
    if best_score < 0.3:
        print("⚠️ SORUN: Tüm skorlar çok düşük!")
        print("\nOlası nedenler:")
        print("  1. Belgede bu bilgi yok")
        print("  2. Embedding modeli soruyu iyi anlamıyor")
        print("  3. Chunk'lar çok kısa/uzun")
    elif best_score < 0.5:
        print("⚠️ UYARI: Skorlar orta seviyede")
        print("  - Yanıt verilebilir ama kaliteli olmayabilir")
    else:
        print("✅ İYİ: Skorlar yeterli")
        print("  - Sistem doğru yanıt vermeli")
else:
    print("❌ HATA: Hiç sonuç bulunamadı!")

print("\n" + "=" * 80)
