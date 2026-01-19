# Active Context

## Current Work Focus

**Date**: 2026-01-05

Project migrated from Windows to Ubuntu. Ready for VPS deployment preparation.

## Recent Changes

### Completed Features

1. **Comparative RAG Pipeline** - 4 parallel searches across scriptures
2. **Multi-Query RAG** - Query expansion with RRF fusion
3. **LLM Answer Generation** - Gemini-powered cited responses
4. **Bible Semantic Chunks** - Thematic grouping for Bible verses
5. **Query Enhancement** - Turkish/English aware query expansion
6. **Project Cleanup** - Moved unused test scripts to `tests/archive/`

### Latest Evaluation Results

- Single-Query: 16.1s avg latency, 95% confidence
- Multi-Query: 23.5s avg latency, 98% confidence
- Cost: ~$0.013 per query
- GT Recall: 1% (needs investigation)

## Next Steps

1. **GT Recall Investigation**: Reference matching logic may need adjustment
2. **Citation Balance**: ~60% Quran vs ~40% Bible - consider prompt tuning
3. **Retry Logic**: Add for outlier latency spikes (one 85s query observed)
4. **Documentation**: Memory Bank created, keep updated

## Active Decisions and Considerations

### Query Enhancement

- **Query Enhancer Model**: Gemini 2.5 Flash Lite (faster models can be tested)
- **Essay Synthesis Model**: Gemini 3.0 Flash (combines queries and generates final text)
- Turkish queries use Turkish-only output for Quran
- Bible queries get translated to English for search
- Aggressive prompt constraints prevent English leakage in Quran queries

### Search Balance

- 20 verses per search type (80 total for comparative)
- Near-perfect Quran/Bible balance (99-100%)
- Priority by reranker score for LLM input

### Performance Trade-offs

- Multi-Query: +46% latency for +2% confidence
- Recommendation: Single-Query for production unless max accuracy needed

## Important Patterns and Preferences

1. **Lazy Loading**: Components initialized on first use
2. **Parallel Execution**: ThreadPoolExecutor for API calls
3. **Caching**: Embeddings cached to disk to reduce costs
4. **Verbose Mode**: Rich console output for debugging

## Learnings and Project Insights

1. **RRF k=60 works well** for fusing diverse result sets
2. **Semantic chunks improve recall** for thematic queries
3. **Cross-lingual reranking** requires translated rerank queries
4. **Gemini Flash** balances cost/quality well for generation
