import hashlib
import logging
import threading

from cachetools import TTLCache
from starlette.concurrency import run_in_threadpool

from .best_hash import BestHash
from .config import settings

logger = logging.getLogger(__name__)


class CacheBase:
    """Thread-safe response cache with TTL support."""

    def __init__(self, maxsize: int = None, ttl: int = None):
        maxsize = maxsize or settings.cache_maxsize
        ttl = ttl or settings.cache_ttl
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = threading.Lock()
        self.selected_algo = BestHash.select_best_hash(settings.hash_algorithm)
        if settings.hash_algorithm == "auto":
            logger.info(
                f"Cache key hash algorithm auto-selection complete. Can store it on .env file 'HASH_ALGORITHM={self.selected_algo}' for skip autodetection next time."
            )
        else:
            logger.info("Cache key hash algorithm selected: %s", self.selected_algo)

    def body_hash_hex_digest(self, body: bytes) -> str:
        h = hashlib.new(self.selected_algo)
        h.update(body)
        return h.hexdigest()

    def build_cache_key(self, path: str, method: str, body: bytes = None) -> str:
        """Build a cache key from a path, method, and optional body."""
        if body:
            body_hash = self.body_hash_hex_digest(body)
            return f"{path}:{method}:{body_hash}".lower()
        return f"{path}:{method}".lower()

    async def async_build_cache_key(self, path: str, method: str, body: bytes = None) -> str:
        return await run_in_threadpool(self.build_cache_key, path, method, body)

    async def set_cache(
        self,
        path: str,
        content: bytes,
        cache_key: str = None,
        method: str = None,
        body: bytes = None,
        headers: dict = None,
        status_code: int = None,
    ):
        if cache_key is not None or self.is_cached(path):
            cache_key = cache_key or await self.async_build_cache_key(path, method, body)
            with self._lock:
                if cache_key not in self._cache:
                    self._cache[cache_key] = {
                        "content": content,
                        "status_code": status_code or 200,
                        "headers": headers or {},
                    }
                    logger.debug(f"Cache set for key: {cache_key[:25]}...")

    async def get_cache(self, path: str, cache_key: str = None, method: str = None, body: bytes = None) -> dict | None:
        if cache_key is not None or self.is_cached(path):
            cache_key = cache_key or await self.async_build_cache_key(path, method, body)
            with self._lock:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit for key: {cache_key[:25]}...")
                return cached
        return None

    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
