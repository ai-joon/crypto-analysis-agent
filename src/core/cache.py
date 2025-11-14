"""Caching utilities."""

import time
from typing import Any, Callable, Optional, Dict, Tuple


class Cache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 300 = 5 minutes)
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str, allow_stale: bool = False) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key
            allow_stale: If True, return cached value even if expired (useful during rate limits)

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        age = time.time() - timestamp
        
        if age >= self.default_ttl:
            if allow_stale:
                # Return stale data if requested (e.g., during rate limits)
                return value
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.time())

    def get_or_fetch(
        self, key: str, fetch_func: Callable[[], Any], ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or fetch and cache the result.

        Args:
            key: Cache key
            fetch_func: Function to fetch data if not cached
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            Cached or freshly fetched value
        """
        cached = self.get(key)
        if cached is not None:
            return cached

        value = fetch_func()
        self.set(key, value, ttl)
        return value

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def invalidate(self, key: str) -> None:
        """
        Remove a specific key from cache.

        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
