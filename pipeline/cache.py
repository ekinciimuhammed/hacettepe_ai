"""
Simple Query-Answer Cache for RAG System
Stores query-answer pairs to avoid reprocessing identical questions
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

class QueryCache:
    """Simple disk-based cache for query-answer pairs"""
    
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory to store cache files
            max_age_hours: Maximum age of cache entries in hours (default: 24)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age_seconds = max_age_hours * 3600
        
        # In-memory cache for faster access
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()
        # Generate hash
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, query: str) -> Optional[str]:
        """
        Get cached answer for query
        
        Args:
            query: User query
            
        Returns:
            Cached answer if found and not expired, None otherwise
        """
        cache_key = self._get_cache_key(query)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if self._is_valid(entry):
                print(f"💾 Cache HIT (memory): {query[:50]}...")
                return entry['answer']
            else:
                # Expired, remove from memory
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if self._is_valid(entry):
                    # Load into memory cache
                    self.memory_cache[cache_key] = entry
                    print(f"💾 Cache HIT (disk): {query[:50]}...")
                    return entry['answer']
                else:
                    # Expired, delete file
                    cache_path.unlink()
                    print(f"🗑️ Cache EXPIRED: {query[:50]}...")
            except Exception as e:
                print(f"⚠️ Cache read error: {e}")
        
        print(f"❌ Cache MISS: {query[:50]}...")
        return None
    
    def set(self, query: str, answer: str, metadata: Optional[Dict] = None):
        """
        Cache query-answer pair
        
        Args:
            query: User query
            answer: Generated answer
            metadata: Optional metadata (sources, chunks, etc.)
        """
        cache_key = self._get_cache_key(query)
        
        entry = {
            'query': query,
            'answer': answer,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        # Save to memory cache
        self.memory_cache[cache_key] = entry
        
        # Save to disk cache
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
            print(f"💾 Cached: {query[:50]}...")
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")
    
    def _is_valid(self, entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        age = time.time() - entry['timestamp']
        return age < self.max_age_seconds
    
    def clear(self):
        """Clear all cache (memory and disk)"""
        # Clear memory
        self.memory_cache.clear()
        
        # Clear disk
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        
        print("🗑️ Cache cleared")
    
    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        disk_count = len(list(self.cache_dir.glob("*.json")))
        memory_count = len(self.memory_cache)
        
        return {
            'memory_entries': memory_count,
            'disk_entries': disk_count,
            'total_entries': disk_count
        }

# Global cache instance
_cache_instance = None

def get_cache() -> QueryCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = QueryCache()
    return _cache_instance
