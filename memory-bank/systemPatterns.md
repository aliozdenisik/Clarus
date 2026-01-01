# System Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI (main.py)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │  UltimateRAG    │    │        ComparativeRAG               │ │
│  │  (Single Text)  │    │     (Multi-Scripture)               │ │
│  └────────┬────────┘    └─────────────┬───────────────────────┘ │
│           │                           │                         │
├───────────┴───────────────────────────┴─────────────────────────┤
│                      Shared Components                          │
│  ┌──────────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────┐  │
│  │QueryEnhancer │ │ Reranker  │ │Embeddings│ │AnswerGenerator│  │
│  └──────────────┘ └───────────┘ └──────────┘ └───────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       Search Layer                              │
│  ┌──────────────┐ ┌─────────────┐ ┌────────────────────────────┐│
│  │QuranSearcher │ │BibleSearcher│ │SemanticChunkSearcher       ││
│  └──────────────┘ └─────────────┘ └────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                       Data Layer                                │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────────────────┐  │
│  │   Indexer    │ │ DataLoader  │ │   SemanticChunker        │  │
│  └──────────────┘ └─────────────┘ └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     Qdrant Vector DB                            │
│  ┌─────────────┐ ┌─────────────────┐ ┌─────────────────────────┐│
│  │  quran_tr   │ │  bible_kjva     │ │  semantic_chunks_*      ││
│  └─────────────┘ └─────────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Key Technical Decisions

### 1. Hybrid Search (Dense + Sparse)

- **Dense**: OpenAI text-embedding-3-large (3072 dim) for semantic similarity
- **Sparse**: Qdrant BM25 via FastEmbed for keyword matching
- **Fusion**: Hybrid search with configurable alpha weighting

### 2. Lazy Loading Pattern

All expensive components use `@property` lazy loading:

```python
@property
def enhancer(self):
    if self._enhancer is None:
        self._enhancer = QueryEnhancer()
    return self._enhancer
```

### 3. Parallel Execution

- ThreadPoolExecutor for concurrent API calls
- 4 parallel searches in ComparativeRAG
- Query enhancement for both scriptures runs in parallel

### 4. RRF Fusion (Reciprocal Rank Fusion)

- Combines multiple ranked result lists
- Formula: `score = sum(1 / (k + rank))` where k=60
- Boosts items appearing in multiple lists

### 5. Embedding Caching

- SQLite-backed DiskCache for embedding persistence
- Avoids repeated API calls for same texts
- Configurable cache directory

## Component Relationships

| Component | Dependencies | Purpose |
|-----------|--------------|---------|
| `UltimateRAG` | All components | Main single-scripture pipeline |
| `ComparativeRAG` | All components | Multi-scripture pipeline |
| `QueryEnhancer` | OpenRouter API | Expand queries with LLM |
| `AnswerGenerator` | OpenRouter API | Generate cited answers |
| `Reranker` | SiliconFlow API | Cross-encoder scoring |
| `Embeddings` | OpenRouter API | Dense + Sparse encoding |
| `*Searcher` | Qdrant, Embeddings | Vector similarity search |
| `Indexer` | Qdrant, Embeddings | Data ingestion |

## Critical Implementation Paths

### Search Flow

1. `QueryEnhancer.enhance()` → expanded query
2. `Embeddings.encode()` → dense + sparse vectors
3. `Searcher.hybrid_search()` → raw results
4. `RRF Fusion` → merged results
5. `Reranker.rerank()` → scored results
6. `AnswerGenerator.generate()` → cited answer

### Indexing Flow

1. `DataLoader.load()` → raw JSON
2. `SemanticChunker.chunk()` → grouped verses
3. `Embeddings.encode_batch()` → vectors
4. `Indexer.index()` → Qdrant upsert
