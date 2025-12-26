"""
Debug script to check retrieval and scoring
"""

from pipeline.embedder import get_embedding
from pipeline.vector_store import search_vectors
from pipeline.entity_extractor import extract_entities
import json

print("=" * 80)
print("DEBUG: Testing Retrieval System")
print("=" * 80)

# Test query
query = "Aşı Enstitüsü ne zaman kuruldu?"
print(f"\nTest Query: {query}")

# Step 1: Extract entities from query
print("\n1. Extracting entities from query...")
query_entities = extract_entities(query)
print("Query entities:")
for entity_type, values in query_entities.items():
    if values:
        print(f"  - {entity_type}: {values}")

# Step 2: Get embedding
print("\n2. Getting query embedding...")
query_embedding = get_embedding(query)
if query_embedding:
    print(f"✅ Embedding generated ({len(query_embedding)} dimensions)")
else:
    print("❌ Failed to generate embedding")
    exit(1)

# Step 3: Search vectors
print("\n3. Searching vector database...")
try:
    results = search_vectors(query_embedding, limit=5)
    print(f"✅ Found {len(results)} results")
    
    if not results:
        print("\n❌ NO RESULTS RETURNED!")
        print("Possible reasons:")
        print("  1. Database is empty")
        print("  2. Embedding dimension mismatch")
        print("  3. Search threshold too high")
    else:
        print("\nTop results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Source: {result.get('source', 'N/A')}")
            print(f"Distance: {result.get('_distance', 'N/A'):.4f}")
            
            # Check metadata
            metadata_str = result.get('metadata', '{}')
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
                if metadata:
                    print("Entities in chunk:")
                    for entity_type, values in metadata.items():
                        if values:
                            print(f"  - {entity_type}: {values}")
            except Exception as e:
                print(f"  Metadata parse error: {e}")
            
            # Show text preview
            text = result.get('text', '')
            print(f"Text preview: {text[:150]}...")
            
except Exception as e:
    print(f"❌ Search failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
