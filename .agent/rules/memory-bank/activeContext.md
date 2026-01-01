# Active Context

## Current Work Focus

- **Documentation Maintenance**: Updating the memory bank to reflect the latest system state.
- **Verification**: Ensuring Bible semantic search and answer generation work correctly.
- **Refinement**: Polishing the CLI experience and improving error handling.

## Recent Changes (January 2025)

1. **Answer Generation Implementation**
   - Implemented `AnswerGenerator` using Gemini 2.5 Flash Lite.
   - Added `ask` and `ask-bible` commands for direct Question-Answering.
   - Pipeline: Retrieve Top Verses -> Generate Synthesized Answer -> Provide Citations.

2. **Comparative RAG & Essay Generation**
   - **Comparative RAG**: Implemented multi-scripture analysis pipeline.
   - **Essay Generation**: `ComparativeAnswerGenerator` creates detailed theological essays.
   - **Command**: `compare` CLI command for detailed cross-analysis.

3. **Token Analysis & Optimization**
   - Enhanced `token_analysis.py` to break down token usage by search type (Quran/Bible x Semantic/Normal).
   - Confirmed 8x/30x cost efficiency of Flash Lite models.

4. **Bible Semantic Verification**
   - Verified `build-bible-semantic-chunks` and `search-bible-semantic`.
   - Fixed large file git errors (`cache.db`).
   - Debugged test suites for Bible RAG.

5. **Infrastructure Improvements**
   - **Async Indexing**: Fully consolidated async indexing for maximum throughput.
   - **Strict Prompting**: Enforced Turkish output strictly in `QueryEnhancer`.
   - **Unified Setup**: Created `setup` command for one-shot initialization.

## Next Steps

1. **GraphRAG Evaluation**: Execute the evaluation plan for GraphRAG on Quran content.
2. **Gospels Testing**: Complete `test_gospels.py` validation.
3. **Performance Tuning**: Continue monitoring cache performance and Qdrant connection stability.
4. **Final Polish**: Ensure all CLI commands have consistent output and error handling.

## Active Decisions

- **Answer Generation Model**: Using **Gemini 2.5 Flash Lite** for `ask` (speed/cost) and **Gemini 2.5 Flash** for `compare` (reasoning depth).
- **Comparative Strategy**: Independent reranking of each source (Quran/Bible x Semantic/Chunk) preserves diversity before essay generation.
- **Search Mode**: Semantic-only performs best for Turkish (vs hybrid).
- **Indexing Strategy**: Async/Parallel is now the standard; synchronous methods removed.
- **Rerank Pool**: Limited to top-50 for performance.

## Important Patterns & Preferences

- **Strict Mode**: Prompts must explicitly forbid unwanted behaviors (e.g., "NO English").
- **Lazy Loading**: Essential for CLI responsiveness.
- **Async First**: Prefer asynchronous operations for I/O heavy tasks.
- **Verbose Logging**: Keep -v flag support for debugging.

## Learnings & Insights

- **Model Selection**: Flash Lite is incredibly efficient for RAG synthesis, while standard Flash is better for complex comparative reasoning.
- **Prompt Engineering**: "Negative constraints" are crucial for language enforcement.
- **Async Efficiency**: Parallel processing is non-negotiable for indexing large datasets like Semantic Chunks.
- **Git Hygiene**: Aggressive `.gitignore` rules for caches are essential.
