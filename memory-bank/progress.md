# Progress

## What Works ✅

### Core Pipeline

- [x] Quran indexing and search (Turkish)
- [x] Bible indexing and search (KJVA English)
- [x] Hybrid search (Dense + Sparse)
- [x] Query enhancement with LLM
- [x] Embedding caching (DiskCache)
- [x] **LLM Response Caching** (Semantic cache with 0.95 threshold, 7-day TTL)

### Advanced Features

- [x] Semantic chunking (Quran + Bible)
- [x] Multi-Query RAG with RRF fusion
- [x] Comparative RAG (4 parallel searches)
- [x] LLM answer generation with citations
- [x] Comparative essay generation
- [x] **Semantic LLM Cache** (60-80% API cost reduction)

### CLI Commands

- [x] `setup` - Full indexing setup
- [x] `search` / `search-bible` - Basic search
- [x] `search-semantic` / `search-bible-semantic` - Chunk search
- [x] `ask` / `ask-bible` - Q&A with citations
- [x] `compare` - Comparative analysis
- [x] `info` / `cache-info` / `cache-clear` - Utilities

## What's Left to Build 🚧

### Optimization

- [x] ~~Investigate low GT Recall (1%)~~ (Reference matching adjusted)
- [x] ~~Add retry logic for API timeouts~~ (Handled in embeddings.py)
- [ ] Tune essay prompt for citation balance
- [ ] Test faster models for Query Enhancer (currently Gemini 3)
- [ ] Migrate caching system to Redis (if feasible)
- [x] ~~MMR Diversity Reranking~~ - Removed (reranker code deleted)
- [x] **Semantic LLM Caching** - Implemented (`src/llm_cache.py`)

### Potential Enhancements

- [ ] Cloud Qdrant deployment option
- [ ] Streaming answer generation
- [ ] Web UI interface
- [ ] Multi-language Bible support
- [ ] GraphRAG integration (partially implemented)

### Security

- [ ] Implement prompt injection attack prevention
  - User input sanitization and validation
  - Hardened LLM system prompts with role boundaries
  - Input/output validation layers

## Current Status

| Area | Status | Notes |
|------|--------|-------|
| Core Search | ✅ Complete | 84%+ Quran, 75%+ Bible accuracy |
| Answer Generation | ✅ Complete | Gemini 2.5 Flash |
| Comparative RAG | ✅ Complete | Evaluated with 50 queries |
| Multi-Query | ✅ Complete | +2% confidence, +46% latency |
| Documentation | ✅ Complete | Memory Bank created |
| Testing | ⚠️ Partial | Evaluation scripts exist |
| **Ubuntu Migration** | ✅ Complete | Python 3.12, Docker native (2026-01-05) |

## Known Issues

1. **Low GT Recall (1%)**: Ground truth matching may have reference format issues
2. **Citation Imbalance**: ~60% Quran vs ~40% Bible in comparative essays
3. **Latency Spikes**: Occasional 85s+ queries (network/API issues)
4. **Large Cache File**: `cache/embeddings/cache.db` can exceed GitHub limits

## Evolution of Project Decisions

### Query Enhancement

- **v1**: Direct search with user query
- **v2**: Added LLM query enhancement
- **v3**: Multi-Query with 3-5 perspectives
- **Current**: Aggressive Turkish-only constraints for Quran

### Search Strategy

- **v1**: Single verse search only
- **v2**: Added semantic chunking for thematic grouping
- **v3**: Parallel verse + chunk search
- **Current**: 4 quadrant search for comparative analysis

### Reranking

- **v1**: No reranking
- **v2**: Local cross-encoder model
- **v3**: Migrated to Qwen3-Reranker-8B via SiliconFlow
- **v4**: Two-stage reranking (Cross-encoder + MMR diversity)
- **v5**: Reranker DISABLED (hurt accuracy, dropped correct verses)
- **Current**: Reranker code REMOVED from codebase (2026-01-19)

### LLM Provider

- **v1**: Local models considered
- **v2**: OpenRouter integration
- **Current**:
  - Query Enhancer: Gemini 2.5 Flash Lite (faster models can be tested)
  - Essay Synthesis: Gemini 3.0 Flash (combines queries and generates final text)
