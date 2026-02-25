# Multi-Agent RAG Architecture for Comparative Theological Analysis

## Abstract

This document describes the multi-agent Retrieval-Augmented Generation (RAG) architecture used in Clarus for comparative theological analysis across four sacred text collections: the Quran (Turkish translations), the Old Testament, the New Testament, and the Apocrypha. The system employs five specialized LLM agents operating in a structured pipeline: four collection-specific agents run in parallel to generate independent commentaries, and a fifth synthesis agent combines their outputs into a structured comparative essay. This architecture addresses the fundamental limitation of single-agent approaches when analyzing texts from distinct theological traditions, where a single model context window and a single prompt cannot adequately represent the interpretive nuances of each tradition. The pipeline achieves approximately $0.013 per query with semantic caching enabled, compared to $0.03 or more without caching.

---

## 1. Introduction

### The Challenge of Multi-Source Comparative Analysis

Comparative theological analysis across sacred texts presents a problem that standard RAG pipelines are not designed to solve. A query such as "What do the scriptures say about forgiveness?" requires retrieving relevant passages from four distinct corpora, each with its own linguistic register, theological vocabulary, and interpretive tradition. The Quran is in Turkish translation; the Bible collections are in English (KJVA). The Old Testament draws on Hebrew Bible scholarship; the New Testament on Pauline and Gospel theology; the Apocrypha on deuterocanonical literature.

A naive approach, feeding all retrieved passages into a single LLM prompt, produces answers that blend traditions without distinguishing them. The model has no mechanism to signal which claims originate from which tradition, and the resulting essay lacks the scholarly precision that comparative theology requires.

### Why a Single-Agent Approach Fails

Single-agent RAG has three specific failure modes for this domain:

1. **Context dilution.** With 80 verses from four traditions in one prompt, the model's attention is spread across all of them. High-relevance passages from a minority tradition (e.g., Apocrypha) are systematically underweighted relative to the larger Bible collections.

2. **Tradition conflation.** Without explicit role separation, the model tends to synthesize rather than compare. It produces a unified narrative rather than four distinct perspectives followed by a synthesis.

3. **Citation ambiguity.** Inline citations become unreliable when the model must simultaneously track references from Bakara:45, Genesis 1:1, John 3:16, and Sirach 2:4 within a single generation pass.

The five-agent architecture solves all three problems by assigning each tradition to a dedicated agent with its own context, system prompt, and generation pass.

---

## 2. System Overview

### 2.1 The RAG Pipeline (End-to-End Flow)

The complete pipeline from user query to final essay proceeds through six stages:

```
User Query
    |
    v
[1] Query Translation (if non-Turkish/English input)
    |
    v
[2] Query Enhancement (LLM-powered expansion)
    |
    v
[3] Multi-Query Generation (3-5 semantic variants)
    |
    v
[4] Parallel Collection Search (4 collections simultaneously)
         quran_tr  |  bible_ot  |  bible_nt  |  bible_apocrypha
    |
    v
[5] RRF Fusion (k=60, per-collection)
    |
    v
[6] Multi-Agent Generation
    |-- OldTestamentAgent  --> OT commentary
    |-- NewTestamentAgent  --> NT commentary
    |-- ApocryphaAgent     --> Apocrypha commentary
    |-- QuranAgent         --> Quran commentary
    |         (all 4 run in parallel via ThreadPoolExecutor)
    |
    v
[7] SummaryAgent (sequential, depends on all 4 outputs)
    |
    v
MultiAgentAnswer (5-paragraph essay + citations + confidence)
```

### 2.2 Two Modes: Single-Source vs. Multi-Agent

Clarus supports two answer generation modes depending on the query type:

**Single-Source Mode** (`UltimateRAG` + `AnswerGenerator`): Used for `search` and `ask` commands targeting one corpus. Retrieves from a single collection, generates one answer paragraph with inline citations. Faster and cheaper, appropriate when the user is not requesting cross-tradition comparison.

**Multi-Agent Mode** (`ComparativeRAG` + `MultiAgentOrchestrator`): Used for `compare` commands. Retrieves from all four collections, runs five agents, and produces a structured essay. This is the focus of this document.

---

## 3. Query Processing Layer

### 3.1 Query Enhancement

Before any vector search occurs, the raw user query is expanded using an LLM. The `QueryEnhancer` class in `src/query_enhancer.py` sends the query to the OpenRouter API and receives a structured JSON response containing synonyms, related theological concepts, and alternative phrasings.

```python
class QueryEnhancer:
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "google/gemini-2.5-flash"

    def __init__(self, model: str | None = None, api_key: str | None = None, locale: str = "tr"):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        ...
```

The enhancer operates in two distinct corpus modes:

- **Bible mode**: Automatically translates Turkish input to English, then expands with KJV-appropriate theological vocabulary.
- **Quran mode**: Keeps Turkish, adds Islamic synonyms and related Quranic concepts.

This separation is critical. A query about "sabir" (patience) in Quran mode should expand to related Islamic concepts like "tevekkul" (reliance on God) and "şükür" (gratitude). The same query in Bible mode should translate to "patience" and expand to "endurance," "perseverance," and "long-suffering" in the KJV register.

The enhancement response is a structured `EnhanceResponse` Pydantic model containing a list of `KeywordSuggestion` objects, each with a confidence score and language tag.

### 3.2 Multi-Query Generation

After enhancement, the pipeline generates 3 to 5 query variants, each capturing a different semantic angle on the original question. This is the multi-query step that drives the RRF fusion in the search layer.

For a query about "forgiveness," the multi-query generator might produce:

- "forgiveness and reconciliation in scripture"
- "divine pardon and mercy in religious texts"
- "repentance and atonement across traditions"

Each variant is searched independently against the vector collections. The results are then fused using Reciprocal Rank Fusion, which rewards passages that appear highly ranked across multiple query variants.

### 3.3 Cross-Language Translation

The `QueryTranslator` in `src/query_translator.py` handles automatic language detection and translation. Eight languages are supported: Turkish (TR), English (EN), Spanish (ES), French (FR), Italian (IT), Portuguese (PT), Arabic (AR), and German (DE).

Translation uses Gemini 2.5 Flash Lite via OpenRouter, chosen for its low latency on simple translation tasks. The detected source language is stored in `search_stats` and propagated through the pipeline so that response generation can match the user's input language.

The comparative pipeline maintains two separate translated queries: one optimized for the Quran corpus (Turkish) and one for the Bible corpus (English). These are generated in parallel:

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    quran_future = executor.submit(gen_quran)
    bible_future = executor.submit(gen_bible)
    quran_queries = quran_future.result()
    bible_queries = bible_future.result()
```

---

## 4. Parallel Search Architecture

### 4.1 Collection-Level Parallelism

The `ComparativeRAG` class searches all four collections simultaneously using `ThreadPoolExecutor`. Each collection runs its own search function in a separate thread:

```python
with ThreadPoolExecutor(max_workers=len(active_keys)) as executor:
    futures = {executor.submit(search_funcs[key]): key for key in active_keys}
    results = {"quran": [], "ot": [], "nt": [], "apocrypha": []}
    for future in as_completed(futures):
        key = futures[future]
        results[key] = future.result()
```

The `active_keys` list is computed from the user's selected collections, so the system only searches collections the user has enabled. This allows single-tradition queries to skip irrelevant collections entirely.

### 4.2 Per-Collection Dense Search

Each collection is searched using dense semantic embeddings (OpenAI `text-embedding-3-large`, 3072 dimensions). The `QuranSearcher` and `BibleSearcher` classes in `src/search.py` wrap the Qdrant client and handle the vector query.

In multi-query mode, each collection is searched with all query variants (3 to 5 queries), producing multiple ranked result lists per collection. The target is 20 verses per collection, yielding up to 80 verses total across all four collections.

### 4.3 Cross-Collection RRF Fusion

Reciprocal Rank Fusion combines the multiple result lists from multi-query search into a single ranked list per collection. The formula is:

```
RRF_score(d) = sum(1 / (k + rank(d, q_i))) for each query variant q_i
```

where `k=60` is the smoothing parameter tuned for this corpus. A passage that ranks highly across multiple query variants receives a higher fused score than one that ranks highly for only one variant.

After fusion, the top 20 results per collection are selected. The collection statistics (RRF scores, result counts) are stored for downstream confidence scoring:

```python
self._last_collection_stats = {
    "collection_results": collection_results,
    "collections_with_results": collections_with_results,
    "total_collections": 4,
    "total_verses": total_verses,
    "all_rrf_scores": all_rrf_scores,
    "num_queries": len(quran_queries),
}
```

---

## 5. The Five-Agent System

### 5.1 Agent Specialization

Each of the five agents is a subclass of `BaseSpecialistAgent` in `src/multi_agent_answer_generator.py`. The four collection agents are specialized by their corpus; the summary agent synthesizes across all four.

| Agent | Collection | Domain Expertise |
|-------|------------|-----------------|
| `OldTestamentAgent` | `bible_ot` | Hebrew Bible, Torah, Prophets, Writings |
| `NewTestamentAgent` | `bible_nt` | Gospels, Epistles, Pauline theology |
| `ApocryphaAgent` | `bible_apocrypha` | Deuterocanonical texts, intertestamental literature |
| `QuranAgent` | `quran_tr_*` | Islamic theology, Quranic Arabic context |
| `SummaryAgent` | all four | Cross-tradition synthesis, comparative theology |

All agents share the same base class and LLM infrastructure but receive different system prompts loaded from the `PromptManager`. The prompts are locale-aware: agents can generate commentary in Turkish or English depending on the user's detected language.

### 5.2 Agent Prompt Engineering

Each agent receives a two-part system prompt: a usage-purpose template (e.g., "personal study" vs. "academic research") prepended to a corpus-specific instruction. The user message contains the query and the formatted verse context.

The `_build_system_prompt` method assembles this:

```python
def _build_system_prompt(self, prompt_key: str, usage_purpose: str | None = None, language: str = "tr") -> str:
    selected_language = language if language in {"tr", "en"} else self.locale
    template = get_prompt_template(usage_purpose or "personal", selected_language)
    base_system_prompt = self._prompt_manager.get_prompt("multi_agent", prompt_key, selected_language)
    return f"{template}\n\n{base_system_prompt}"
```

The user message for the Old Testament agent in Turkish mode:

```
SORU: {query}

ESKİ AHİT AYETLERİ:
[1] Genesis 1:1 - In the beginning God created the heaven and the earth. (skor: 0.87)
[2] Psalms 103:12 - As far as the east is from the west, so far hath he removed our transgressions from us. (skor: 0.82)
...
```

Verses are formatted with their reference, text (truncated to 400 characters), and RRF score. The score ordering signals to the model which passages are most relevant.

All agents request JSON-structured output with `"response_format": {"type": "json_object"}` to ensure reliable parsing. The expected response schema is:

```json
{
  "commentary": "...",
  "citations": ["Genesis 1:1", "Psalms 103:12"],
  "confidence": 0.85
}
```

### 5.3 Parallel Agent Execution

The four collection agents run in parallel using `ThreadPoolExecutor` with `max_workers=4`. Each agent is wrapped in a Sentry performance span for observability:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(run_ot),
        executor.submit(run_nt),
        executor.submit(run_apocrypha),
        executor.submit(run_quran),
    ]

    completed_count = 0
    for future in as_completed(futures):
        key, result = future.result()
        results[key] = result
        if key in active_agents:
            completed_count += 1
            _emit("agent_completed",
                  f"{agent_labels.get(key, key)} agent completed ({completed_count}/{agent_count})")
```

The `_emit` callback fires progress events that are forwarded to the client via Server-Sent Events, allowing the frontend to display real-time progress ("Old Testament agent completed (1/4)").

Agents that receive no verses for their collection return immediately with an empty commentary:

```python
def generate(self, query: str, verses: list, ...) -> dict[str, Any]:
    if not verses:
        return {"commentary": "", "citations": [], "confidence": 0.0}
```

This means the system gracefully handles queries where one or more collections return no relevant results.

### 5.4 The SummaryAgent: Cross-Tradition Synthesis

The `SummaryAgent` runs after all four collection agents complete. It receives the four commentaries as context and generates a synthesis paragraph that identifies common themes, key differences, and cross-tradition insights.

The summary agent's user message is assembled from the available commentaries:

```python
parts = []
if ot_commentary:
    parts.append(f"ESKİ AHİT YORUMU:\n{ot_commentary}")
if nt_commentary:
    parts.append(f"YENİ AHİT YORUMU:\n{nt_commentary}")
if apocrypha_commentary:
    parts.append(f"APOKRİFA YORUMU:\n{apocrypha_commentary}")
if quran_commentary:
    parts.append(f"KURAN YORUMU:\n{quran_commentary}")

context = "\n\n".join(parts)
```

The summary agent uses `max_tokens=800` (compared to 1000 for collection agents) because its task is synthesis rather than detailed exegesis. It returns a JSON object with `synthesis`, `common_themes`, and `key_differences` fields.

---

## 6. Answer Generation

### 6.1 Single-Source Answers (`answer_generator.py`)

For non-comparative queries, the `AnswerGenerator` class generates a single answer paragraph from one collection's search results. It uses the same OpenRouter infrastructure as the multi-agent system but with a simpler prompt structure.

The `AnswerResult` dataclass captures the output:

```python
@dataclass
class AnswerResult:
    text: str           # Full answer text with inline citations
    citations: list[str]  # List of cited references
    confidence: float   # 0.0 - 1.0 confidence score
    source: str         # quran_tr, bible_kjva, etc.
    query: str          # Original query
    context_used: int   # Number of verses used as context
    confidence_breakdown: dict | None = None
```

### 6.2 Comparative Essays (`comparative_answer_generator.py`)

The `ComparativeAnswerGenerator` handles the older two-collection comparison mode (Quran + Bible as a whole, without per-testament separation). It formats up to 80 verses across four search result sets and generates a single essay with inline citations.

This mode is used when the user requests a comparison without the full five-agent breakdown. The `ComparativeAnswer` dataclass separates Quran and Bible references:

```python
@dataclass
class ComparativeAnswer:
    essay: str                    # Full essay with inline citations
    quran_references: list[str]   # Used Quran verse references
    bible_references: list[str]   # Used Bible verse references
    all_references: list[str]     # Numbered list of all refs (in order of use)
    confidence: float
    query: str
    verses_provided: int          # Total verses given to LLM (up to 80)
    confidence_breakdown: dict | None = None
```

### 6.3 Citation Handling

Inline citations use bracket notation: `[Bakara:45]` for Quran, `[John 3:16]` for Bible. The `CitationSanitizer` in `src/citation_sanitizer.py` validates citation format consistency after generation, normalizing variations like "John 3.16" or "Jn 3:16" to the canonical form.

Citations are extracted from the LLM's JSON response and stored separately from the essay text, enabling the frontend to render hover cards with the full verse text when a user mouses over a citation.

---

## 7. Output Structure

### 7.1 `MultiAgentAnswer` Dataclass

The `MultiAgentOrchestrator.generate()` method returns a `MultiAgentAnswer` instance:

```python
@dataclass
class MultiAgentAnswer:
    old_testament_commentary: str
    new_testament_commentary: str
    apocrypha_commentary: str
    quran_commentary: str
    synthesis: str

    citations: dict[str, list[str]] = field(default_factory=dict)
    confidence: float = 0.0
    confidence_breakdown: dict | None = None
    query: str = ""
    verses_provided: dict[str, int] = field(default_factory=dict)
    locale: str = "tr"

    def to_essay(self) -> str:
        """Format as markdown essay with locale-specific section headers"""
        pm = PromptManager()
        headers = pm.get_section_headers(self.locale)
        sections = []

        if self.old_testament_commentary:
            sections.append(f"{headers['old_testament']}\n\n{self.old_testament_commentary}")
        if self.new_testament_commentary:
            sections.append(f"{headers['new_testament']}\n\n{self.new_testament_commentary}")
        if self.apocrypha_commentary:
            sections.append(f"{headers['apocrypha']}\n\n{self.apocrypha_commentary}")
        if self.quran_commentary:
            sections.append(f"{headers['quran']}\n\n{self.quran_commentary}")
        if self.synthesis:
            sections.append(f"{headers['synthesis']}\n\n{self.synthesis}")

        return "\n\n---\n\n".join(sections)
```

The `citations` dictionary groups references by source:

```python
citations={
    "old_testament": ot_result.get("citations", []),
    "new_testament": nt_result.get("citations", []),
    "apocrypha": apoc_result.get("citations", []),
    "quran": quran_result.get("citations", []),
}
```

The `verses_provided` dictionary records how many verses each agent received, which feeds into the confidence scoring system.

### 7.2 Confidence Scoring

After all five agents complete, the `ConfidenceScorer` computes a calibrated confidence score using a two-phase sigmoid system. Phase 1 evaluates retrieval quality (RRF score distribution, result coverage across collections). Phase 2 evaluates answer quality (citation density, synthesis length, top-K usage). The two phases are combined using a geometric mean weighted 60/40 toward retrieval quality.

The confidence score ranges from 40% to 95%, with a structural ceiling removed in a recent update to allow high-quality answers to reach their natural score.

### 7.3 Streaming via SSE

The multi-agent pipeline supports real-time progress streaming via Server-Sent Events. The `progress_callback` parameter accepts a `Callable[[str, str], None]` that fires at each pipeline stage:

| Step ID | Message Example |
|---------|----------------|
| `agents_starting` | "Running 4 specialist agents in parallel (Old Testament, New Testament, Apocrypha, Quran)..." |
| `agent_completed` | "Old Testament agent completed (1/4)" |
| `summary_starting` | "Synthesizing all perspectives into comparative essay..." |
| `summary_completed` | "Comparative synthesis complete" |
| `scoring_confidence` | "Calculating confidence score..." |

The SSE endpoint in `backend/app/api/stream.py` wraps the orchestrator and forwards these events to the client as `data:` lines in the SSE stream.

---

## 8. LLM Configuration

All LLM calls route through the OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`). The model assignments reflect a deliberate cost-latency tradeoff:

| Purpose | Model | Provider | Notes |
|---------|-------|----------|-------|
| Query Enhancement | `google/gemini-2.5-flash` | OpenRouter | Fast, low-cost for simple JSON extraction |
| Answer Generation (all agents) | `google/gemini-3-flash-preview` | OpenRouter | Balanced quality and cost for essay generation |
| Translation | `google/gemini-2.5-flash` | OpenRouter | Low latency for translation tasks |

All agents use `temperature=0.3` for commentary generation (low temperature for factual accuracy) and `"response_format": {"type": "json_object"}` for structured output. The comparative essay generator uses `temperature=0.4` and `max_tokens=4000` to allow longer, more nuanced essays.

Retry logic uses the `tenacity` library with exponential backoff:

```python
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)
def _call_llm(self, messages: list[dict], max_tokens: int = 1000) -> dict:
    ...
```

Network errors and timeouts trigger retries; JSON parse errors and circuit breaker open states do not (they fail fast and return empty commentary).

**Cost estimate**: With semantic caching achieving 60-80% hit rates, the effective cost per query is approximately $0.013. Without caching, the cost rises to $0.03 or more depending on query complexity and the number of active agents.

---

## 9. References

- Lewis, P., Perez, E., Piktus, A., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *Advances in Neural Information Processing Systems*, 33.

- Wang, X., Wei, J., Schuurmans, D., et al. (2023). "Self-Consistency Improves Chain of Thought Reasoning in Language Models." *International Conference on Learning Representations*.

- Park, J. S., O'Brien, J. C., Cai, C. J., et al. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." *ACM Symposium on User Interface Software and Technology*.

- Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods." *ACM SIGIR Conference on Research and Development in Information Retrieval*.

- Qdrant Documentation. "Vector Search." https://qdrant.tech/documentation/concepts/search/
