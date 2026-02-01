# RAG PIPELINE - KNOWLEDGE BASE

## OVERVIEW

Core RAG (Retrieval-Augmented Generation) pipeline for sacred text search. 17 Python modules handling embeddings, search, chunking, and multi-agent answer generation.

## STRUCTURE

```
src/
├── ultimate_rag.py             # Main orchestrator (593 lines)
├── comparative_rag.py          # Cross-scripture analysis (776 lines)
├── multi_agent_answer_generator.py  # 5-agent essay system (530 lines)
├── search.py                   # Qdrant hybrid search (974 lines)
├── embeddings.py               # Dense + sparse encoders (653 lines)
├── indexer.py                  # Collection management (722 lines)
├── query_enhancer.py           # LLM query expansion
├── llm_cache.py                # Semantic response caching
├── answer_generator.py         # Single-source LLM answers
├── comparative_answer_generator.py  # Essay generation
├── semantic_chunker.py         # Quran verse grouping
├── bible_semantic_chunker.py   # Bible verse grouping
├── data_loader.py              # Quran JSON loader
├── bible_loader.py             # Bible KJVA loader
├── lemmatizer.py               # Turkish text normalization
├── turkish_utils.py            # Turkish-specific utilities
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

## CONVENTIONS (THIS MODULE)

- **All I/O is async** - Use `async/await` for Qdrant and LLM calls
- **Type hints required** - Every function signature must have types
- **Logging**: Use `logging.getLogger(__name__)` not print
- **Error handling**: Catch specific exceptions, never bare `except:`
- **Collections**: Access via constants `QURAN_COLLECTION`, `BIBLE_OT_COLLECTION`, etc.

## ANTI-PATTERNS

- **Never call OpenAI synchronously** - Use async client
- **Never hardcode collection names** - Use constants from `indexer.py`
- **Never skip cache check** - Always check `LLMCache` before LLM call
- **Never return raw Qdrant response** - Wrap in domain objects

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
