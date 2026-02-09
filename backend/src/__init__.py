# Clarus - Hybrid Search Package
from .data_loader import QuranDataLoader
from .embeddings import AsyncDenseEncoder, DenseEncoder
from .indexer import QuranIndexer, SemanticChunkIndexer
from .query_enhancer import QueryEnhancer
from .search import BibleSearcher, QuranSearcher, SemanticChunkSearcher
from .semantic_chunker import SemanticChunk, SemanticVerseChunker

# GraphRAG (optional - requires neo4j)
try:
    from .graph_rag import GraphRAGBuilder
except ImportError:
    GraphRAGBuilder = None  # neo4j not installed

__all__ = [
    "QuranDataLoader",
    "AsyncDenseEncoder",
    "DenseEncoder",
    "QuranIndexer",
    "SemanticChunkIndexer",
    "QueryEnhancer",
    "BibleSearcher",
    "QuranSearcher",
    "SemanticChunkSearcher",
    "SemanticChunk",
    "SemanticVerseChunker",
    "GraphRAGBuilder",
]
