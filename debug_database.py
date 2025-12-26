"""
Debug script to check if Hybrid RAG PDF was processed and contains institute information
"""

import lancedb
import json

# Connect to database
db = lancedb.connect("lancedb_data")
table = db.open_table("vectors")

# Search for chunks containing "Aşı Enstitüsü"
print("=" * 80)
print("Searching for 'Aşı Enstitüsü' in database...")
print("=" * 80)

results = table.search("Aşı Enstitüsü").limit(5).to_list()

if not results:
    print("\n❌ NO RESULTS FOUND for 'Aşı Enstitüsü'")
else:
    print(f"\n✅ Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {result.get('source', 'N/A')}")
        print(f"Distance: {result.get('_distance', 'N/A')}")
        
        # Check metadata for entities
        metadata_str = result.get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
            print(f"Entities in metadata:")
            for entity_type, values in metadata.items():
                if values:
                    print(f"  - {entity_type}: {values}")
        except:
            print(f"  Metadata: {metadata_str}")
        
        # Show text preview
        text = result.get('text', '')
        print(f"\nText preview (first 200 chars):")
        print(text[:200] + "...")

print("\n" + "=" * 80)
print("Checking if 'Hacettepe Bölümleri ve Hibrit RAG.pdf' was indexed...")
print("=" * 80)

# Check for the hybrid RAG PDF
all_sources = table.to_pandas()['source'].unique()
print(f"\nAll indexed sources ({len(all_sources)}):")
for source in sorted(all_sources):
    print(f"  - {source}")

hybrid_pdf_found = any("Hibrit RAG" in source or "hibrit" in source.lower() for source in all_sources)
print(f"\n{'✅' if hybrid_pdf_found else '❌'} Hybrid RAG PDF {'found' if hybrid_pdf_found else 'NOT FOUND'}")
