import time
import threading
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class SimpleTTLCache:
    """
    A simple in-memory cache with Time-To-Live (TTL) support.
    Thread-safe implementation using Lock for concurrent access protection.
    """
    def __init__(self):
        # Dictionary to hold the data: key -> value
        self.cache: Dict[str, Any] = {}
        # Dictionary to hold expiration times: key -> expiration_timestamp
        self.expirations: Dict[str, float] = {}
        # Thread lock for safe concurrent access
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        Returns None if key is missing or expired.
        """
        with self._lock:
            if key in self.cache:
                if time.time() < self.expirations[key]:
                    # Cache hit
                    logger.debug(f"Cache HIT for key: {key}")
                    return self.cache[key]
                else:
                    # Cache expired
                    logger.debug(f"Cache EXPIRED for key: {key}")
                    self._delete_unsafe(key)
            else:
                logger.debug(f"Cache MISS for key: {key}")
                
        return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """
        Set a value in the cache with a specified TTL in seconds.
        """
        with self._lock:
            self.cache[key] = value
            self.expirations[key] = time.time() + ttl_seconds
            logger.debug(f"Cache SET for key: {key} with TTL: {ttl_seconds}s")

    def _delete_unsafe(self, key: str):
        """Internal helper to remove item (must be called with lock held)."""
        if key in self.cache:
            del self.cache[key]
        if key in self.expirations:
            del self.expirations[key]

    def clear(self):
        """Clear all cached items."""
        with self._lock:
            self.cache.clear()
            self.expirations.clear()
            logger.debug("Cache CLEARED")

# Global cache instance
# We can create specific instances if needed, but a global one is often useful for app-level caching.
global_cache = SimpleTTLCache()

