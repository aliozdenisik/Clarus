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
│  │  +LLMCache   │ │+MMRRerank │ │          │ │               │  │
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

## Design Principles

A good system design should incorporate the following core quality attributes:

- **Scalability**: The system should handle increasing workloads gracefully, whether scaling vertically (more resources) or horizontally (more instances).
- **Reliability**: The system should function correctly and consistently, handling failures gracefully with proper error handling and recovery mechanisms.
- **Maintainability**: The codebase should be easy to understand, modify, and extend. This includes clear code organization, documentation, and modular architecture.
- **Efficiency**: The system should optimize resource usage (CPU, memory, network, API calls) to minimize latency and operational costs.

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

### 6. Semantic LLM Caching (NEW 2026-01-19)

- Caches LLM responses (query enhancement, multi-query)
- Semantic similarity matching (threshold: 0.95)
- 7-day TTL, disk-persistent
- 60-80% reduction in LLM API calls

### 7. MMR Diversity Reranking (NEW 2026-01-19)

- Two-stage reranking: Cross-encoder → MMR
- Balances relevance (70%) with diversity (30%)
- Prevents redundant/similar results in top positions

## Component Relationships

| Component | Dependencies | Purpose |
|-----------|--------------|---------|
| `UltimateRAG` | All components | Main single-scripture pipeline |
| `ComparativeRAG` | All components | Multi-scripture pipeline |
| `QueryEnhancer` | OpenRouter API, LLMCache | Expand queries with LLM |
| `AnswerGenerator` | OpenRouter API | Generate cited answers |
| `Reranker` | SiliconFlow API | Cross-encoder scoring |
| `MMRReranker` | - | Diversity reranking (λ=0.7) |
| `SemanticLLMCache` | Embeddings | LLM response cache (θ=0.95) |
| `Embeddings` | OpenRouter API | Dense + Sparse encoding |
| `*Searcher` | Qdrant, Embeddings | Vector similarity search |
| `Indexer` | Qdrant, Embeddings | Data ingestion |

## Critical Implementation Paths

### Search Flow (Updated 2026-01-19)

1. `SemanticLLMCache.get()` → check cache for enhanced query
2. `QueryEnhancer.enhance()` → expanded query (if cache miss)
3. `SemanticLLMCache.set()` → cache the result
4. `Embeddings.encode()` → dense + sparse vectors
5. `Searcher.hybrid_search()` → raw results
6. `RRF Fusion` → merged results
7. `Reranker.rerank()` → cross-encoder scored results (2× top_k)
8. `MMRReranker.rerank()` → diversity-aware final results (top_k)
9. `AnswerGenerator.generate()` → cited answer

### Indexing Flow

1. `DataLoader.load()` → raw JSON
2. `SemanticChunker.chunk()` → grouped verses
3. `Embeddings.encode_batch()` → vectors
4. `Indexer.index()` → Qdrant upsert
