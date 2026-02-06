# RAG PIPELINE - KNOWLEDGE BASE

## OVERVIEW

Core RAG (Retrieval-Augmented Generation) pipeline for sacred text search. 29 Python modules handling embeddings, search, chunking, morphological analysis, and multi-agent answer generation. Includes Bible morphology (Hebrew/Greek), circuit breaker, and Redis-backed caching.

## STRUCTURE

```
src/
├── ultimate_rag.py             # Main orchestrator (1447 lines)
├── comparative_rag.py          # Cross-scripture analysis (1414 lines)
├── bible_morphology.py         # Bible morphological search - Hebrew/Greek (1900 lines)
├── multi_agent_answer_generator.py  # 5-agent essay system (805 lines)
├── search.py                   # Qdrant hybrid search (880 lines)
├── verse_parser.py             # Verse reference parsing (792 lines)
├── query_enhancer.py           # LLM query expansion (729 lines)
├── indexer.py                  # Collection management (644 lines)
├── semantic_chunker.py         # Quran verse grouping (638 lines)
├── query_translator.py         # Cross-language translation (613 lines)
├── quran_morphology.py         # Arabic root-based search (607 lines)
├── embeddings.py               # Dense + sparse encoders (570 lines)
├── greek_normalizer.py         # Greek text normalization (509 lines)
├── answer_generator.py         # Single-source LLM answers (500 lines)
├── bible_semantic_chunker.py   # Bible verse grouping (499 lines)
├── comparative_answer_generator.py  # Essay generation (488 lines)
├── hebrew_normalizer.py        # Hebrew text normalization (428 lines)
├── llm_cache.py                # LLM response caching (395 lines)
├── confidence_scorer.py        # Two-phase sigmoid scoring (376 lines)
├── bible_loader.py             # Bible KJVA loader (282 lines)
├── lemmatizer.py               # Turkish text normalization (194 lines)
├── turkish_utils.py            # Turkish-specific utilities (191 lines)
├── data_loader.py              # Quran JSON loader (188 lines)
├── circuit_breaker.py          # External service resilience (142 lines)
├── citation_sanitizer.py       # Citation format validation (126 lines)
├── arabic_normalizer.py        # Arabic normalization + Buckwalter (87 lines)
├── semantic_cache.py           # Semantic cache wrapper (38 lines)
├── graph_rag.py                # Graph RAG placeholder (41 lines)
├── multi_query.py              # Multi-query wrapper (23 lines)
└── __init__.py                 # Package exports
```

## DATA FLOW

```
                    UltimateRAG.search() / ask()
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   QueryEnhancer         Multi-Query            LLMCache
   (LLM expand)          (3-5 variants)         (check hit)
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Parallel Search │
                    │   (4 collections) │
                    └─────────┬─────────┘
                              │
            ┌────────┬────────┼────────┬────────┐
            │        │        │        │        │
         quran_tr bible_ot bible_nt bible_apoc
            │        │        │        │        │
            └────────┴────────┼────────┴────────┘
                              │
                         RRF Fusion
                         (k=60)
                              │
                    AnswerGenerator / MultiAgentAnswerGenerator
```

## KEYWORD SEARCH DATA FLOW

```
                    Morphological Keyword Search
                              │
        ┌─────────────────────┼─────────────────────┐
        │                                           │
   Quran (Arabic)                           Bible (Hebrew/Greek)
   quran_morphology.py                      bible_morphology.py
        │                                           │
   Arabic Input (كتب)                        Hebrew/Greek Input
   or Buckwalter (ktb)                       or Strongs Number
        │                                           │
   Root Extraction                           Root/Lemma Lookup
        │                                           │
   Derived Words                             Cross-reference
        │                                           │
   Verse Lookup                              Verse Lookup
        │                                           │
   Surah Distribution                        Book Distribution
```

## WHERE TO LOOK

| Task | File | Key Method |
|------|------|------------|
| Add search feature | `ultimate_rag.py` | `UltimateRAG.search_quran()` |
| Modify embedding | `embeddings.py` | `DenseEncoder.encode()` |
| Change fusion logic | `search.py` | `rrf_fusion()` |
| Add new agent | `multi_agent_answer_generator.py` | Create new `*Agent` class |
| Modify chunking | `semantic_chunker.py` | `SemanticVerseChunker.chunk()` |
| Add collection | `indexer.py` | `QuranIndexer.create_collection()` |
| Cache tuning | `llm_cache.py` | `SemanticCache` (theta=0.95) |
| Parse verse refs | `verse_parser.py` | `VerseParser.parse()` |
| Arabic morphology | `quran_morphology.py` | `QuranMorphologyService` |
| Bible morphology | `bible_morphology.py` | `BibleMorphologyService` |
| Hebrew normalization | `hebrew_normalizer.py` | `HebrewNormalizer` |
| Greek normalization | `greek_normalizer.py` | `GreekNormalizer` |
| Cross-language query | `query_translator.py` | `QueryTranslator.translate()` |
| Circuit breaker | `circuit_breaker.py` | `CircuitBreaker` decorator |
| Citation validation | `citation_sanitizer.py` | `CitationSanitizer.sanitize()` |
| Confidence scoring | `confidence_scorer.py` | `ConfidenceScorer.score()` |

## KEY CLASSES

| Class | Purpose | Critical Methods |
|-------|---------|------------------|
| `UltimateRAG` | Main pipeline orchestrator | `search_quran()`, `ask_quran()`, `search_bible()` |
| `ComparativeRAG` | Cross-scripture search | `compare()`, `compare_multi_agent()` |
| `MultiAgentAnswerGenerator` | 5-agent essay system | `generate()` returns `MultiAgentAnswer` |
| `QuranSearcher` | Qdrant hybrid search | `search()` with dense+sparse |
| `DenseEncoder` | OpenAI embeddings | `encode()` → 3072-dim vector |
| `SparseEncoder` | BM25 via FastEmbed | `encode()` → sparse vector |
| `QueryEnhancer` | LLM query expansion | `enhance()` → expanded query string |
| `BibleMorphologyService` | Bible keyword search | Hebrew/Greek root + Strongs mapping |
| `QuranMorphologyService` | Quran keyword search | Arabic root extraction + derived words |
| `VerseParser` | Verse reference parsing | `parse()` → normalized reference |
| `QueryTranslator` | Cross-language translation | `translate()` → translated query |
| `ConfidenceScorer` | Two-phase scoring | `score()` → calibrated confidence |
| `CircuitBreaker` | Service resilience | Decorator for external calls |
| `HebrewNormalizer` | Hebrew text processing | Normalization + transliteration |
| `GreekNormalizer` | Greek text processing | Normalization + transliteration |

## CONVENTIONS (THIS MODULE)

- **All I/O is async** - Use `async/await` for Qdrant, LLM, and Redis calls
- **Type hints required** - Every function signature must have types
- **Logging**: Use `logging.getLogger(__name__)` not print
- **Error handling**: Catch specific exceptions, never bare `except:`
- **Collections**: Access via constants `QURAN_COLLECTION`, `BIBLE_OT_COLLECTION`, etc.
- **Redis**: Fail-open pattern — Redis failures logged but never crash the app

## ANTI-PATTERNS

- **Never call OpenAI synchronously** - Use async client
- **Never hardcode collection names** - Use constants from `indexer.py`
- **Never skip cache check** - Always check `LLMCache` before LLM call
- **Never return raw Qdrant response** - Wrap in domain objects
- **Never bypass circuit breaker** - Use decorator for external service calls

## 5-AGENT SYSTEM DETAILS

```python
# Agent responsibilities (multi_agent_answer_generator.py)
QuranAgent          → Searches quran_tr, generates Quranic perspective
OldTestamentAgent   → Searches bible_ot, Hebrew Bible perspective  
NewTestamentAgent   → Searches bible_nt, Gospel perspective
ApocryphaAgent      → Searches bible_apocrypha, Deuterocanonical perspective
SummaryAgent        → Synthesizes 4 perspectives into 5-paragraph essay
```

**Output structure**:
```python
MultiAgentAnswer:
    topic: str
    commentaries: List[AgentCommentary]  # 4 agents
    summary: str                          # SummaryAgent output
    citations: Dict[str, List[str]]       # Grouped by source
    confidence: float
    to_essay() -> str                     # Full markdown essay
```

## TESTING

**NOT pytest** - Uses custom accuracy benchmark:
```bash
python tests/run_retrieval_accuracy_test.py
```

Measures:
- Precision: Did we find relevant verses?
- Recall: Did we miss relevant verses?
- F1 Score: Combined metric (target: 84%+ Quran, 75%+ Bible)

Ground truth: `tests/test_data.json`

## NOTES

- **Embedding dimension**: 3072 (OpenAI text-embedding-3-large)
- **Sparse encoder**: Qdrant BM25 via FastEmbed
- **RRF k-parameter**: 60 (tuned for this corpus)
- **Cache threshold**: 0.95 cosine similarity
- **Rate limits**: Built into QueryEnhancer for OpenRouter
- **Bible morphology DB**: Strongs numbers for Hebrew (OT) and Greek (NT) cross-referencing
- **Circuit breaker**: 5 failures → open state → 60s timeout → half-open retry

## CONFIDENCE SCORING

We use a **Two-Phase Sigmoid-Calibrated** system (see `docs/CONFIDENCE_SCORING.md`) instead of a simple weighted average.

**Phase 1: Retrieval Confidence** (Search Quality)
- `Score Quality`: Median RRF score of top-5 results (Sigmoid calibrated)
- `Score Separation`: Ratio of Top-1 to Top-5 score (Clear winner detection)
- `Result Coverage`: Actual vs Expected results ratio

**Phase 2: Answer Quality** (Generation Quality)
- `Citation Density`: Citations per paragraph (context-aware)
- `Top-K Usage`: How many citations come from the top search results
- `Substance`: Word count validation

**Fusion**:
geometric_mean(retrieval^0.6, answer^0.4) blended with arithmetic mean, then final sigmoid calibration. 
Range: **40-95%** (Structural ceiling of 72% removed).

**Removed Signals**:
- `llm_confidence`: Removed (Dead signal, models always confident)
- `citation_coverage`: Removed (Penalized concise answers)
