"""In-memory TTL cache plus persistent query result cache."""

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import settings

@dataclass
class CacheItem:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self):
        self._items: dict[str, CacheItem] = {}

    def get(self, key: str) -> Any | None:
        item = self._items.get(key)
        if not item:
            return None
        if item.expires_at < time.time():
            self._items.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._items[key] = CacheItem(value=value, expires_at=time.time() + ttl_seconds)


class QueryCache:
    """Persistent exact-match query cache backed by diskcache when available."""

    def __init__(self, cache_dir: str | None = None, ttl_seconds: int | None = None, max_size_mb: int | None = None):
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds or settings.cache_ttl_seconds
        self._fallback = TTLCache()
        try:
            from diskcache import Cache

            self.cache = Cache(str(self.cache_dir), size_limit=(max_size_mb or settings.cache_max_size_mb) * 1024 * 1024)
        except Exception:
            self.cache = None

    def get(self, query: str) -> dict | None:
        if not settings.cache_enabled:
            return None
        key = self._hash_query(query)
        value = self.cache.get(key) if self.cache is not None else self._fallback.get(key)
        if value is None:
            return None
        if isinstance(value, str):
            return json.loads(value)
        return value

    def set(self, query: str, result: dict) -> None:
        if not settings.cache_enabled:
            return
        key = self._hash_query(query)
        payload = json.dumps(result, default=str)
        if self.cache is not None:
            self.cache.set(key, payload, expire=self.ttl_seconds)
        else:
            self._fallback.set(key, result, ttl_seconds=self.ttl_seconds)

    def invalidate_all(self) -> None:
        if self.cache is not None:
            self.cache.clear()
        self._fallback = TTLCache()

    def stats(self) -> dict:
        if self.cache is None:
            return {"backend": "memory", "entries": len(self._fallback._items)}
        return {"backend": "diskcache", "entries": len(self.cache), "directory": str(self.cache_dir)}

    def _hash_query(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()
