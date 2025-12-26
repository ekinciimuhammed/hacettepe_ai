"""
Cache Test Script
Test query-answer caching functionality
"""

from pipeline.cache import QueryCache
import time

print("=" * 80)
print("CACHE TEST")
print("=" * 80)

# Create cache instance
cache = QueryCache(cache_dir="test_cache", max_age_hours=1)

# Test 1: Basic cache operations
print("\n1️⃣ Basic Cache Operations")
print("-" * 80)

query1 = "Hacettepe ne zaman kuruldu?"
answer1 = "Hacettepe Üniversitesi 1967 yılında kurulmuştur."

# Set cache
cache.set(query1, answer1, metadata={"source": "test"})

# Get cache (should hit)
result = cache.get(query1)
assert result == answer1, "Cache miss!"
print(f"✅ Cache HIT: {query1}")

# Test 2: Case insensitive
print("\n2️⃣ Case Insensitive Test")
print("-" * 80)

query2_upper = "HACETTEPE NE ZAMAN KURULDU?"
result = cache.get(query2_upper)
assert result == answer1, "Case insensitive failed!"
print(f"✅ Case insensitive works: {query2_upper}")

# Test 3: Whitespace normalization
print("\n3️⃣ Whitespace Normalization Test")
print("-" * 80)

query3_spaces = "  Hacettepe   ne  zaman   kuruldu?  "
result = cache.get(query3_spaces)
assert result == answer1, "Whitespace normalization failed!"
print(f"✅ Whitespace normalization works")

# Test 4: Cache miss
print("\n4️⃣ Cache Miss Test")
print("-" * 80)

query4 = "Tıp Fakültesi nerede?"
result = cache.get(query4)
assert result is None, "Should be cache miss!"
print(f"✅ Cache MISS (expected): {query4}")

# Test 5: Multiple entries
print("\n5️⃣ Multiple Entries Test")
print("-" * 80)

queries = [
    ("Soru 1", "Cevap 1"),
    ("Soru 2", "Cevap 2"),
    ("Soru 3", "Cevap 3"),
]

for q, a in queries:
    cache.set(q, a)

for q, a in queries:
    result = cache.get(q)
    assert result == a, f"Failed for {q}"
    print(f"✅ {q} → {a}")

# Test 6: Cache stats
print("\n6️⃣ Cache Statistics")
print("-" * 80)

stats = cache.stats()
print(f"Memory entries: {stats['memory_entries']}")
print(f"Disk entries: {stats['disk_entries']}")
print(f"Total entries: {stats['total_entries']}")

# Test 7: Performance test
print("\n7️⃣ Performance Test")
print("-" * 80)

# First call (cache miss)
start = time.time()
result = cache.get("Performance test query")
miss_time = time.time() - start
print(f"Cache MISS time: {miss_time*1000:.2f}ms")

# Set cache
cache.set("Performance test query", "Performance test answer")

# Second call (cache hit - memory)
start = time.time()
result = cache.get("Performance test query")
hit_time = time.time() - start
print(f"Cache HIT time (memory): {hit_time*1000:.2f}ms")

speedup = miss_time / hit_time if hit_time > 0 else float('inf')
print(f"Speedup: {speedup:.0f}x faster")

# Test 8: Clear cache
print("\n8️⃣ Clear Cache Test")
print("-" * 80)

cache.clear()
result = cache.get(query1)
assert result is None, "Cache should be empty!"
print(f"✅ Cache cleared successfully")

print("\n" + "=" * 80)
print("✅ All tests passed!")
print("=" * 80)

# Cleanup
import shutil
shutil.rmtree("test_cache", ignore_errors=True)
