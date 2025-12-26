"""
Test specific queries with updated config
"""

from pipeline.rag_engine import generate_answer

test_queries = [
    "Aşı Enstitüsü ne zaman kuruldu?",
    "HÜNİTEK hangi araştırmaları yapıyor?",
    "Yapay Zeka Mühendisliği Programı hangi fakültede?"
]

print("=" * 80)
print("TESTING SPECIFIC QUERIES WITH UPDATED CONFIG")
print("=" * 80)
print("\nConfig changes:")
print("  - TOP_K: 5 → 10 (more chunks for re-ranking)")
print("  - MIN_SCORE_THRESHOLD: 0.35 → 0.0 (accept all results)")
print("  - VECTOR_WEIGHT: 0.7 → 0.6")
print("  - ENTITY_WEIGHT: 0.3 → 0.4 (more importance to entity matching)")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"QUERY {i}: {query}")
    print("=" * 80)
    
    try:
        answer = generate_answer(query)
        
        # Check if answer contains "belge bulunamadığı" or "yanıt veremiyorum"
        if "belge bulunamadığı" in answer.lower() or "yanıt veremiyorum" in answer.lower():
            print("❌ FAILED: Still returning 'no document found'")
            print(f"\nAnswer:\n{answer[:300]}...")
        else:
            print("✅ SUCCESS: Got a real answer!")
            print(f"\nAnswer ({len(answer)} chars):\n{answer[:500]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

print("=" * 80)
print("Test completed!")
print("=" * 80)
