"""Semantic cache for LLM responses using embedding similarity."""

import time
import hashlib
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from openai import OpenAI
import numpy as np
import os

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached response with metadata."""

    query: str
    response: str
    embedding: List[float]
    timestamp: float
    expires_at: float
    hit_count: int = 0


class SemanticCache:
    """Semantic cache using embedding similarity to find similar queries."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        similarity_threshold: float = 0.85,
        max_cache_size: int = 1000,
        ttl: int = 3600,
        embedding_model: str = "text-embedding-3-small",
        cache_file: Optional[str] = None,
    ):
        """
        Initialize semantic cache.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            similarity_threshold: Minimum cosine similarity to consider queries similar (0.0-1.0)
            max_cache_size: Maximum number of cached responses
            ttl: Time-to-live in seconds (default: 1 hour)
            embedding_model: OpenAI embedding model to use
            cache_file: Path to JSON file for persistence (default: semantic_cache.json in project root)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for semantic cache")

        self.client = OpenAI(api_key=self.api_key)
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self.ttl = ttl

        if cache_file:
            self.cache_file = Path(cache_file)
        else:
            project_root = Path(__file__).parent.parent.parent
            self.cache_file = project_root / "semantic_cache.json"

        self._cache: Dict[str, CachedResponse] = {}
        self._embeddings: List[np.ndarray] = []
        self._cache_keys: List[str] = []

        self._load_from_file()
        self._ensure_cache_file_exists()

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model, input=[text]
            )
            embedding = response.data[0].embedding
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            raise RuntimeError(f"Failed to get embedding: {e}") from e

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))

    def _find_similar_query(
        self, query_embedding: np.ndarray
    ) -> Optional[Tuple[str, CachedResponse, float]]:
        """Find most similar cached query."""
        if not self._embeddings:
            return None

        best_similarity = 0.0
        best_key = None

        for i, cached_embedding in enumerate(self._embeddings):
            similarity = self._cosine_similarity(query_embedding, cached_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_key = self._cache_keys[i]

        if best_similarity >= self.similarity_threshold:
            return (best_key, self._cache[best_key], best_similarity)

        return None

    def _is_expired(self, cached_response: CachedResponse) -> bool:
        """Check if cached response is expired."""
        current_time = time.time()
        return current_time >= cached_response.expires_at

    def _evict_oldest(self) -> None:
        """Evict oldest cache entry if at max size."""
        if len(self._cache) < self.max_cache_size:
            return

        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].timestamp)
        self._remove(oldest_key)

    def _remove(self, key: str) -> None:
        """Remove entry from cache."""
        if key in self._cache:
            index = self._cache_keys.index(key)
            del self._cache[key]
            del self._cache_keys[index]
            del self._embeddings[index]

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        expired_keys = [
            key for key, cached in self._cache.items() if self._is_expired(cached)
        ]
        for key in expired_keys:
            self._remove(key)

    def get(self, query: str) -> Optional[str]:
        """Get cached response for similar query."""
        self._cleanup_expired()

        if not self._cache:
            return None

        try:
            query_embedding = self._get_embedding(query)
            match = self._find_similar_query(query_embedding)

            if match:
                cache_key, cached_response, _ = match

                if self._is_expired(cached_response):
                    logger.debug("Cached response expired, removing from cache")
                    self._remove(cache_key)
                    return None

                cached_response.hit_count += 1
                return cached_response.response
        except Exception:
            pass

        return None

    def _is_valid_response(self, response: str) -> bool:
        """Check if response is valid and should be cached."""
        if not response or not response.strip():
            return False

        response_lower = response.lower()

        error_patterns = [
            "i encountered an error",
            "i apologize, but i couldn't generate",
            "api error",
            "rate limit exceeded",
            "could not find cryptocurrency",
            "error in",
            "an unexpected error occurred",
            "please try again",
            "please wait",
            "temporarily unavailable",
            "failed to",
            "unable to",
            "couldn't",
            "could not",
            "error occurred",
            "encountered an error",
        ]

        for pattern in error_patterns:
            if pattern in response_lower:
                return False

        if len(response.strip()) < 20:
            return False

        return True

    def set(self, query: str, response: str) -> None:
        """Cache a query-response pair."""
        if not self._is_valid_response(response):
            return

        self._cleanup_expired()
        self._evict_oldest()

        try:
            query_embedding = self._get_embedding(query)
            cache_key = hashlib.md5(query.encode()).hexdigest()
            current_time = time.time()

            cached_response = CachedResponse(
                query=query,
                response=response,
                embedding=query_embedding.tolist(),
                timestamp=current_time,
                expires_at=current_time + self.ttl,
            )

            self._cache[cache_key] = cached_response
            self._cache_keys.append(cache_key)
            self._embeddings.append(query_embedding)

            self._save_to_file()
            logger.debug(f"Cached query-response pair: {query[:50]}...")
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}", exc_info=True)

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()
        self._embeddings.clear()
        self._cache_keys.clear()
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
            except Exception:
                pass

    def _load_from_file(self) -> None:
        """Load cache from JSON file."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "entries" not in data:
                return

            current_time = time.time()
            for entry in data.get("entries", []):
                timestamp = entry.get("timestamp", 0)
                expires_at = entry.get("expires_at")

                if not expires_at:
                    expires_at = timestamp + self.ttl

                if current_time >= expires_at:
                    continue

                cache_key = entry.get("key")
                if not cache_key:
                    continue

                cached_response = CachedResponse(
                    query=entry.get("query", ""),
                    response=entry.get("response", ""),
                    embedding=entry.get("embedding", []),
                    timestamp=entry.get("timestamp", current_time),
                    expires_at=expires_at,
                    hit_count=entry.get("hit_count", 0),
                )

                self._cache[cache_key] = cached_response
                self._cache_keys.append(cache_key)
                self._embeddings.append(
                    np.array(cached_response.embedding, dtype=np.float32)
                )

        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            pass

    def _ensure_cache_file_exists(self) -> None:
        """Ensure cache file exists with empty structure."""
        if not self.cache_file.exists():
            try:
                data = {
                    "version": "1.0",
                    "entries": [],
                    "metadata": {
                        "similarity_threshold": self.similarity_threshold,
                        "max_cache_size": self.max_cache_size,
                        "ttl": self.ttl,
                        "embedding_model": self.embedding_model,
                    },
                }
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except (OSError, ValueError, TypeError):
                pass

    def _save_to_file(self) -> None:
        """Save cache to JSON file."""
        try:
            entries = [
                {
                    "key": key,
                    "query": cached.query,
                    "response": cached.response,
                    "embedding": cached.embedding,
                    "timestamp": cached.timestamp,
                    "expires_at": cached.expires_at,
                    "hit_count": cached.hit_count,
                }
                for key, cached in self._cache.items()
            ]

            data = {
                "version": "1.0",
                "entries": entries,
                "metadata": {
                    "similarity_threshold": self.similarity_threshold,
                    "max_cache_size": self.max_cache_size,
                    "ttl": self.ttl,
                    "embedding_model": self.embedding_model,
                },
            }

            temp_file = self.cache_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            temp_file.replace(self.cache_file)
            logger.debug(
                f"Cache saved to {self.cache_file} with {len(entries)} entries"
            )
        except (OSError, ValueError, TypeError) as e:
            logger.warning(f"Failed to save cache file: {e}", exc_info=True)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired()

        total_hits = sum(cached.hit_count for cached in self._cache.values())
        avg_hits = total_hits / len(self._cache) if self._cache else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_cache_size,
            "total_hits": total_hits,
            "average_hits_per_entry": avg_hits,
            "similarity_threshold": self.similarity_threshold,
            "ttl_seconds": self.ttl,
        }
