"""
Full RAG pipeline test
"""

from pipeline.rag_engine import retrieve_context, generate_answer

print("=" * 80)
print("FULL RAG PIPELINE TEST")
print("=" * 80)

query = "Aşı Enstitüsü ne zaman kuruldu?"
print(f"\nQuery: {query}\n")

# Step 1: Test retrieval
print("Step 1: Testing retrieve_context()...")
print("-" * 80)

context_items = retrieve_context(query)

print(f"\nRetrieved {len(context_items)} context items")

if not context_items:
    print("❌ NO CONTEXT RETRIEVED!")
    print("\nThis means:")
    print("  1. Vector search returned no results, OR")
    print("  2. All results were filtered out, OR")
    print("  3. Scores were too low")
else:
    print("✅ Context retrieved successfully\n")
    for i, item in enumerate(context_items, 1):
        print(f"Context {i}:")
        print(f"  Source: {item.get('source', 'N/A')}")
        print(f"  Score: {item.get('score', 'N/A')}")
        print(f"  Text: {item.get('text', '')[:150]}...")
        print()

# Step 2: Test full answer generation
print("\n" + "=" * 80)
print("Step 2: Testing generate_answer()...")
print("-" * 80)

answer = generate_answer(query)

print(f"\nAnswer ({len(answer)} chars):")
print(answer)

print("\n" + "=" * 80)
