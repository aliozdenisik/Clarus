"""Multi-query generation and parallel keyword search helpers.

Stub module — planned feature. Referenced by:
  - QuranSearcher.multi_query_search (search.py)
  - QuranSearcher.parallel_keyword_search (search.py)
"""


class MultiQueryGenerator:
    """Generates multiple query variations for improved recall.

    Not yet implemented.
    """

    def generate(self, query: str, n: int = 3) -> list[str]:
        raise NotImplementedError(
            "MultiQueryGenerator is not yet implemented. Use UltimateRAG multi-query pipeline instead."
        )
