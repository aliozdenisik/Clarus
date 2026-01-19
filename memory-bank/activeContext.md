# Active Context

## Current Work Focus

**Date**: 2026-01-19

Cross-encoder reranker has been **COMPLETELY REMOVED** from the codebase based on retrieval accuracy test results.

## Recent Changes

### Code Cleanup (2026-01-19)

**Reranker Code Removed** - All reranker-related code has been deleted from the project:

**Reason**: Test analysis showed reranker was actively removing correct verses found by Search:
- Q-15 (Ebabil): Search found 105:3, 105:4 at top → Reranker dropped them
- B-02 (Fruit of Spirit): Search found Gal 5:22, 5:23 at top → Reranker dropped them
- Q-08 (Hatemül Enbiya): Search found 33:40 at rank 3 → Reranker dropped it

**Test Results Comparison**:
| Metric | With Reranker | Without Reranker |
|--------|---------------|------------------|
| Recall | 83.9% | **94.6%** (+11%) |
| F1 | 49.4% | **53.6%** (+4%) |
| Latency | 17.6s | **11.0s** (-37%) |
| Kuran Recall | 71.9% | **90.6%** (+19%) |

**TODO**: Re-enable with multilingual cross-encoder model (current Qwen3-Reranker-8B struggles with Turkish)

### Deleted Files
- `src/reranker.py` - Cross-encoder reranker module
- `src/mmr_reranker.py` - MMR diversity reranker module
- `tests/archive/test_reranker_module.py` - Obsolete test
- `tests/run_no_reranker_test.py` - Legacy comparison test
- `tests/test_results_no_reranker.json` - Old test results
- `tests/test_output.log`, `tests/test_results_mmr_only.log` - Log files
- Stale `__pycache__/*.pyc` files for removed modules

### Code Refactored
- `src/comparative_rag.py` - Removed `reranker` property and `_rerank_each()` method, replaced with `_select_top_results()`
- `src/ultimate_rag.py` - Already simplified in previous session

### Previous Features

1. **Semantic LLM Cache** - `src/llm_cache.py` (active)
2. **Comparative RAG Pipeline** - 4 parallel searches
3. **Multi-Query RAG** - Query expansion with RRF fusion
4. **Query Enhancement** - Turkish/English aware expansion

## Next Steps

1. ✅ ~~Retrieval accuracy test with reranker disabled~~
2. **Find multilingual reranker** - BAAI/bge-reranker-v2-m3 or similar
3. **Web UI** - Consider frontend for the RAG system

## Active Decisions

- **Reranker**: REMOVED from codebase (Qwen3 dropped correct results)
- **Search Strategy**: RRF fusion with multi-query expansion
- **Priority**: Accuracy > Cost > Speed
- **LLM Cache**: Active (0.95 threshold, 7-day TTL)

## Learnings

1. **Reranker can hurt accuracy** - Cross-encoder models need language-matching training
2. **RRF k=60 works well** for fusing diverse result sets
3. **Semantic chunks improve recall** for thematic queries
4. **Gemini Flash** balances cost/quality well for generation
