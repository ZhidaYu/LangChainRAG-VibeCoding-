"""LRU cache for query results."""
import hashlib
import json
from collections import OrderedDict
from threading import Lock
from app.config import settings


class LRUCache:
    """Thread-safe LRU cache for storing query → answer mappings."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict[str, dict] = OrderedDict()
        self.lock = Lock()

    def _normalize(self, query: str) -> str:
        """Normalize query for cache key."""
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]

    def get(self, query: str) -> dict | None:
        key = self._normalize(query)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
        return None

    def set(self, query: str, value: dict):
        key = self._normalize(query)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)


# Global cache instances
query_cache = LRUCache(max_size=200)
embed_cache: dict[str, list] = {}
