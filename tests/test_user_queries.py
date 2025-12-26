"""
Test script to query the enhanced Hybrid RAG system
"""

from pipeline.rag_engine import generate_answer

# Test queries from user
test_queries = [
    "Aşı Enstitüsü ne zaman kuruldu?",
    "HÜNİTEK hangi araştırmaları yapıyor?",
    "Yapay Zeka Mühendisliği Programı hangi fakültede?"
]

print("=" * 80)
print("ENHANCED HYBRID RAG TEST - User Queries")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"SORU {i}: {query}")
    print("=" * 80)
    
    try:
        answer = generate_answer(query)
        print(f"\nYANIT:\n{answer}")
    except Exception as e:
        print(f"\nHATA: {e}")
    
    print("\n" + "=" * 80)

print("\n✅ Test tamamlandı!")
