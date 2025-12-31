# System Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py (CLI)                           │
├─────────────────────────────────────────────────────────────────┤
│                       UltimateRAG Pipeline                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │   Query     │→ │  Multi-     │→ │  Parallel   │→ │Reranker ││
│  │  Enhancer   │  │  Query Gen  │  │  Search     │  │         ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘│
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│ │   Embeddings    │  │     Search      │  │  Semantic       │  │
│ │ (Dense+Sparse)  │  │ (Hybrid+RRF)    │  │  Chunker        │  │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     Qdrant Vector Database                       │
│  ┌──────────────┐  ┌──────────────────────┐  ┌───────────────┐ │
│  │   quran_tr   │  │ quran_semantic_chunks│  │ bible_turhadi │ │
│  └──────────────┘  └──────────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Technical Decisions

### 1. Dual-Collection Strategy

- **Single-verse collection** (`quran_tr`): Precise verse retrieval
- **Semantic chunks collection** (`quran_semantic_chunks`): Thematic groupings
- Parallel search on both, merged via RRF

### 2. Hybrid Search (Dense + Sparse)

- **Dense**: OpenAI `text-embedding-3-large` (3072 dim)
- **Sparse**: BM25 via FastEmbed with Turkish lemmatization
- Combined score improves both recall and precision

### 3. Multi-Query RAG

- LLM generates 3-5 query variations
- Each variation searched independently
- Results fused to capture different perspectives

### 4. Lazy Loading Pattern

- Expensive resources (Reranker, Enhancer) loaded on first use
- Improves CLI startup time for non-search commands

### 5. Caching Strategy

- **Embedding cache**: DiskCache with 7-day TTL
- **Rate limiting**: 20 RPM for API calls
- **Semantic cache**: Query-level result caching

## Design Patterns in Use

| Pattern | Usage |
|---------|-------|
| **Lazy Loading** | Reranker, Query Enhancer, Searchers |
| **Strategy** | Multiple search modes (semantic, hybrid, keyword) |
| **Factory** | Searcher creation based on source type |
| **Facade** | UltimateRAG wraps complex pipeline |
| **Singleton** | Shared Qdrant client, embedding models |

## Component Relationships

```
UltimateRAG
├── QueryEnhancer (Gemini Flash via OpenRouter)
├── Reranker (Qwen3-Reranker)
├── QuranSearcher / BibleSearcher
│   ├── DenseEncoder (OpenAI)
│   ├── SparseEncoder (FastEmbed BM25)
│   └── QdrantClient
└── SemanticChunkSearcher
```

## Critical Implementation Paths

### Search Flow

1. `cmd_search()` → `UltimateRAG.search_quran()`
2. `_enhance_query()` → LLM enhancement
3. `_generate_multi_queries()` → Query variations
4. `_search_all_queries()` → Parallel hybrid search + RRF fusion
5. `_rerank_results()` → Cross-encoder final ordering

### Indexing Flow

1. `cmd_index()` → `QuranIndexer.index()`
2. Load data via `QuranDataLoader`
3. Generate embeddings (Dense + Sparse)
4. Upsert to Qdrant with payload indexing
