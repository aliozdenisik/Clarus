# Active Context

## Current Work Focus

**Date**: 2026-01-19 (evening)

**Multi-Agent Answer Generation** system implemented for comparative scripture analysis.

## Recent Changes

### Multi-Agent Architecture (2026-01-19)

**New Feature**: 5-agent theological answer generation system:

| Agent | Scope | Perspective |
|-------|-------|-------------|
| OldTestamentAgent | Tevrat, Zebur, Peygamberler | Yahudi-Hristiyan tefsir |
| NewTestamentAgent | İnciller, Mektuplar, Vahiy | Kristolojik perspektif |
| ApocryphaAgent | Tobit, Sirach, Makkabiler, vb. | Katolik/Ortodoks tefsir |
| QuranAgent | Kuran | İslami tefsir geleneği |
| SummaryAgent | 4 yorumu sentezler | Karşılaştırmalı |

**New Files**:
- `src/multi_agent_answer_generator.py` - 5 agent + orchestrator

**Modified Files**:
- `src/comparative_rag.py` - Added `compare_multi_agent()` method

**Test Results** (query: "Sabır hakkında..."):

| Metric | Single Query | Multi-Query + RRF |
|--------|--------------|-------------------|
| OT Verses | 0 | 1 |
| Apocrypha | 5 | 6 |
| Confidence | 96% | 98% |

| Latency | ~21s | ~37s |

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

