"""
Quick test to verify database and RAG system after rebuild
"""

import os
import sys

print("=" * 80)
print("CHECKING SYSTEM STATUS")
print("=" * 80)

# Check if database exists
db_exists = os.path.exists("lancedb_data")
print(f"\n1. Database exists: {'✅ YES' if db_exists else '❌ NO (needs rebuild)'}")

# Check if cache exists  
cache_exists = os.path.exists("cache")
print(f"2. Cache exists: {'✅ YES' if cache_exists else '❌ NO (cleared)'}")

# Check PDF count
pdf_count = len([f for f in os.listdir("belgeler") if f.endswith('.pdf')])
print(f"3. PDFs in belgeler/: {pdf_count}")

if not db_exists:
    print("\n" + "=" * 80)
    print("⚠️  DATABASE NEEDS TO BE REBUILT")
    print("=" * 80)
    print("\nRun: python main.py")
    print("This will:")
    print("  1. Process all 14 PDFs")
    print("  2. Extract entities (including new types)")
    print("  3. Create fresh database")
    print("  4. Start Q&A interface")
    sys.exit(0)

# If database exists, try a simple query
print("\n" + "=" * 80)
print("TESTING RAG QUERY")
print("=" * 80)

try:
    from pipeline.rag_engine import generate_answer
    
    test_query = "Hacettepe Üniversitesi hakkında bilgi ver"
    print(f"\nTest Query: {test_query}")
    print("\nGenerating answer...")
    
    answer = generate_answer(test_query)
    print(f"\n✅ SUCCESS! Answer received ({len(answer)} chars)")
    print(f"\nAnswer preview:\n{answer[:300]}...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
