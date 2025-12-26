"""
Simple check: Is Hybrid RAG PDF in database?
"""

import lancedb

db = lancedb.connect("lancedb_data")
table = db.open_table("vectors")
df = table.to_pandas()

sources = df['source'].unique()

print("=" * 80)
print(f"Total indexed files: {len(sources)}")
print("=" * 80)

for source in sorted(sources):
    count = len(df[df['source'] == source])
    print(f"  - {source} ({count} chunks)")

print("\n" + "=" * 80)
print("Checking for Hybrid RAG PDF...")
print("=" * 80)

hybrid_found = False
for source in sources:
    if 'Hibrit' in source or 'hibrit' in source.lower() or 'Hybrid' in source:
        print(f"✅ FOUND: {source}")
        hybrid_found = True

if not hybrid_found:
    print("❌ Hybrid RAG PDF NOT FOUND in database!")
    print("\nThis PDF contains information about:")
    print("  - Aşı Enstitüsü")
    print("  - HÜNİTEK")
    print("  - Research centers")
    print("  - Academic programs")
