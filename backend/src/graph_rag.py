"""Knowledge graph builder for Graph RAG.

Stub module — planned feature. Referenced by CLI commands:
  - cmd_build_graph (main.py)
  - cmd_graph_info (main.py)

Requires: neo4j (pip install neo4j)
"""

from typing import Any, Dict, List, Tuple


class GraphRAGBuilder:
    """Builds a Neo4j knowledge graph from indexed Qdrant collections.

    Not yet implemented.
    """

    def __init__(self, qdrant_url: str = "localhost:6333") -> None:
        raise NotImplementedError(
            "GraphRAGBuilder is not yet implemented. "
            "Install neo4j and configure NEO4J_PASSWORD to use."
        )

    def clear_graph(self) -> None:
        raise NotImplementedError

    def build_from_collection(
        self,
        collection_name: str,
        limit: int = 0,
        batch_size: int = 50,
        show_progress: bool = True,
        workers: int = 1,
        resume: bool = False,
        checkpoint_interval: int = 100,
    ) -> Tuple[List[Any], List[Any]]:
        raise NotImplementedError

    def get_graph_stats(self) -> Dict[str, Any]:
        raise NotImplementedError
