"""Semantic cache for RAG query results.

Stub module — planned feature. Referenced by CLI commands:
  - cmd_cache_info (main.py)
  - cmd_cache_clear (main.py)
"""

from dataclasses import dataclass


@dataclass
class CacheStats:
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    avg_similarity: float = 0.0
    oldest_entry_hours: float = 0.0


class SemanticCache:
    """Qdrant-backed semantic cache with cosine similarity lookup.

    Not yet implemented. See llm_cache.py for the existing
    simpler caching layer.
    """

    def __init__(self, qdrant_url: str = "localhost:6333") -> None:
        raise NotImplementedError("SemanticCache is not yet implemented. Use llm_cache.py for basic caching.")

    def get_stats(self) -> CacheStats:
        raise NotImplementedError

    def clear(self, older_than_hours: float | None = None) -> int:
        raise NotImplementedError
