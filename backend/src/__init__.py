# Clarus - Hybrid Search Package
from .data_loader import QuranDataLoader as QuranDataLoader
from .embeddings import AsyncDenseEncoder as AsyncDenseEncoder
from .embeddings import DenseEncoder as DenseEncoder
from .indexer import QuranIndexer as QuranIndexer
from .indexer import SemanticChunkIndexer as SemanticChunkIndexer
from .query_enhancer import QueryEnhancer as QueryEnhancer
from .search import BibleSearcher as BibleSearcher
from .search import QuranSearcher as QuranSearcher
from .search import SemanticChunkSearcher as SemanticChunkSearcher
from .semantic_chunker import SemanticChunk as SemanticChunk
from .semantic_chunker import SemanticVerseChunker as SemanticVerseChunker

# GraphRAG (optional - requires neo4j)
try:
    from .graph_rag import GraphRAGBuilder as GraphRAGBuilder
except ImportError:
    GraphRAGBuilder = None

__all__ = [
    "QuranDataLoader",
    "DenseEncoder",
    "AsyncDenseEncoder",
    "QuranIndexer",
    "SemanticChunkIndexer",
    "QuranSearcher",
    "BibleSearcher",
    "SemanticChunkSearcher",
    "QueryEnhancer",
    "SemanticChunk",
    "SemanticVerseChunker",
    "GraphRAGBuilder",
]
