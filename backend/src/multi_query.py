"""Multi-query generation and parallel keyword search helpers.

Stub module — planned feature. Referenced by:
  - QuranSearcher.multi_query_search (search.py)
  - QuranSearcher.parallel_keyword_search (search.py)
"""

from typing import Any, List

from qdrant_client.models import Prefetch


class MultiQueryGenerator:
    """Generates multiple query variations for improved recall.

    Not yet implemented.
    """

    def generate(self, query: str, n: int = 3) -> List[str]:
        raise NotImplementedError(
            "MultiQueryGenerator is not yet implemented. "
            "Use UltimateRAG multi-query pipeline instead."
        )


def create_multi_query_prefetches(
    queries: List[str],
    dense_encoder: Any,
    limit_per_query: int = 20,
) -> List[Prefetch]:
    """Create Qdrant prefetch objects for multi-query search."""
    raise NotImplementedError
