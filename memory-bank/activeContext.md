# Active Context

## Current Work Focus

- **Gospels Testing**: Running `test_gospels.py` with 26 queries specific to the four Gospels (Matthew, Mark, Luke, John)
- **Memory Bank Setup**: Initializing documentation system for session continuity

## Recent Changes (December 2024)

1. **Ultimate RAG Pipeline Simplification**
   - Removed all other search methods, keeping only Ultimate RAG
   - Unified pipeline for both Quran and Bible searches

2. **Semantic Chunking Integration**
   - Percentile-based thresholding (25th percentile)
   - 1779 semantic chunks for Quran
   - Fixed lazy loading issue with `QuranDataLoader`

3. **GraphRAG Implementation**
   - `build-graph` command for knowledge graph construction
   - Checkpoint/resume support for large datasets

4. **Documentation Updates**
   - README.md and user_guide.md updated
   - Added Turkish descriptions

## Next Steps

1. Complete Gospels testing and validate Bible search accuracy
2. Evaluate GraphRAG methodology on Quran content
3. Address any remaining cache-related errors
4. Consider expanding to additional Bible translations

## Active Decisions

- **Search Mode**: Semantic-only performs best for Turkish (vs hybrid)
- **Rerank Pool**: Limited to top-50 for performance
- **RRF k-parameter**: Set to 60 for optimal fusion
- **Threshold Type**: Percentile preferred over fixed threshold

## Important Patterns & Preferences

- Lazy loading for expensive resources (reranker, enhancer)
- Turkish lemmatization via Zeyrek for BM25
- Verbose mode (`-v`) for debugging pipeline stages
- Parallel search on verses + semantic chunks

## Learnings & Insights

- Fixed-threshold chunking creates inconsistent chunk sizes
- Semantic search outperforms hybrid for Turkish queries
- Query enhancement critical for recall improvement
- Cache errors often due to Qdrant connection issues
