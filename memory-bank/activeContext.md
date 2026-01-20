# Active Context

## Current Work Focus

**Date**: 2026-01-20

**4-Testament Collection Architecture** implemented for balanced multi-agent search.

## Recent Changes

### Testament-Based Collections (2026-01-20)

**Architecture Update**: Bible split into 3 separate Qdrant collections:

| Collection | Points | Agent |
|------------|--------|-------|
| `quran_tr` | 6,236 | QuranAgent |
| `bible_ot` | 23,145 | OldTestamentAgent |
| `bible_nt` | 7,957 | NewTestamentAgent |
| `bible_apocrypha` | 5,717 | ApocryphaAgent |
| SummaryAgent | 4 yorumu sentezler | Karşılaştırmalı |

**New Files**:
- `src/multi_agent_answer_generator.py` - 5 agent + orchestrator

**Modified Files**:
- `src/comparative_rag.py` - Added `compare_multi_agent()` method

**Test Results** (query: "Sabır hakkında..."):

| Agent | Verses (Before) | Verses (Now) |
|-------|-----------------|-------------|
| OT | 3 | **20** ✅ |
| NT | 11 | **20** ✅ |
| Apocrypha | 6 | **20** ✅ |
| Quran | 40 | **20** ✅ |

| Metric | Value |
|--------|-------|
| Total | 80 verses |
| Confidence | 96% |
| Latency | ~40s |

### Retrieval Accuracy Test (2026-01-20)

**10-Question Sample (5 Quran + 5 Bible)**:
- **Overall F1**: 57.3%
- **Quran Recall**: 80%
- **Bible Recall**: 100%
- **Fix**: Re-indexed `quran_tr` and `bible_kjva` collections.

### Previous Features

1. **Semantic LLM Cache** - `src/llm_cache.py` (active)
2. **Comparative RAG Pipeline** - 4 parallel searches
3. **Multi-Query RAG** - Query expansion with RRF fusion (Active by default)
4. **Query Enhancement** - Turkish/English aware expansion
5. **Multi-Agent Answers** - 5-paragraph structured output (NEW)

## Next Steps

1. ✅ ~~Multi-agent answer generation~~
2. **Find multilingual reranker** - BAAI/bge-reranker-v2-m3 or similar
3. **Web UI** - Consider frontend for the RAG system
4. **Old Testament coverage** - Current search returns mostly NT

## Active Decisions

- **Answer Mode**: Two options available:
  - `compare()` → Single essay (faster)
  - `compare_multi_agent()` → 5 paragraphs (better quality)
- **Search Strategy**: Multi-Query + RRF Fusion (Enabled by default for max accuracy)
- **Reranker**: REMOVED from codebase
- **Priority**: Accuracy > Cost > Speed

## Learnings

1. **Tradition-specific prompts** improve theological accuracy
2. **Parallel agent execution** keeps latency manageable (8s for 4 agents)
3. **Testament split works** - Bible data has testament field (OT/NT/Apocrypha)
4. **Gemini Flash** handles all 5 agents well at 0.3 temperature

