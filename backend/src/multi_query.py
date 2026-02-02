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


class ParallelKeywordParser:
    """Splits a query into individual keywords for parallel BM25 search.

    Not yet implemented.
    """

    def parse(self, query: str) -> List[str]:
        raise NotImplementedError("ParallelKeywordParser is not yet implemented.")


def create_multi_query_prefetches(
    queries: List[str],
    sparse_encoder: Any,
    dense_encoder: Any,
    limit_per_query: int = 20,
) -> List[Prefetch]:
    """Create Qdrant prefetch objects for multi-query search."""
    raise NotImplementedError


def create_parallel_keyword_prefetches(
    keywords: List[str],
    sparse_encoder: Any,
    limit_per_keyword: int = 20,
) -> List[Prefetch]:
    """Create Qdrant prefetch objects for parallel keyword search."""
    raise NotImplementedError
