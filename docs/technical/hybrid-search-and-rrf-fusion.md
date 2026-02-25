# Hybrid Search and Reciprocal Rank Fusion in Clarus

## Abstract

Clarus retrieves verses from a 43,055-vector corpus spanning four sacred text collections using a multi-stage pipeline that combines dense semantic embeddings with sparse BM25 keyword matching, then fuses results from multiple query variants via Reciprocal Rank Fusion (RRF). This document describes the mathematical foundations of each stage, the implementation choices made for this specific corpus, and the performance characteristics observed in production.

---

## 1. Introduction

Retrieval-Augmented Generation systems live or die by recall. A system that fails to surface the most relevant passage cannot produce a grounded answer, regardless of how capable the generation model is. For sacred text search, this problem is acute: the same concept appears across thousands of verses in multiple languages, and users phrase queries in ways that may share no lexical overlap with the target text.

Clarus addresses this with a three-layer retrieval strategy:

1. **Hybrid search** combines dense semantic vectors with sparse BM25 vectors, capturing both conceptual similarity and exact keyword relevance.
2. **Multi-query expansion** generates 3-5 query variants per user query, broadening the recall surface.
3. **RRF fusion** merges all ranked lists into a single coherent ranking without requiring score normalization.

The corpus consists of four Qdrant collections: `quran_tr_*` (6,236 verses per translation, 8 translations), `bible_ot` (23,145 verses), `bible_nt` (7,957 verses), and `bible_apocrypha` (5,717 verses).

---

## 2. Dense Vector Search

### 2.1 Embedding Model

All dense vectors are produced by **OpenAI `text-embedding-3-large`** via the OpenRouter API. The model produces 3,072-dimensional embeddings with strong multilingual coverage, which is critical for the Quran collections indexed in Turkish.

From `backend/src/embeddings.py`:

```python
class DenseEncoder:
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
    DEFAULT_MODEL = "openai/text-embedding-3-large"
    EMBEDDING_DIMENSION = 3072
    RATE_LIMIT_RPM = 20
    CACHE_EXPIRE = 86400 * 7  # 7 days
```

Embeddings are cached in Redis with a 7-day TTL using a SHA-256 key derived from the model name and input text:

```python
def _get_cache_key(self, text: str) -> str:
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    return f"embedding:{self.model_name}:{text_hash}"
```

The cache follows a fail-open pattern: if Redis is unavailable, the encoder falls back to direct API calls without interrupting the request.

### 2.2 HNSW Index Configuration

Qdrant stores dense vectors in a Hierarchical Navigable Small World (HNSW) graph index. The collection creation parameters, from `backend/src/indexer.py`, are:

```python
vectors_config={
    "dense": VectorParams(
        size=3072,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(
            m=16,
            ef_construct=200,
        ),
        quantization_config=ScalarQuantization(
            scalar=ScalarQuantizationConfig(
                type=ScalarType.INT8,
                quantile=0.99,
                always_ram=True
            )
        ),
    )
},
sparse_vectors_config={
    "sparse": SparseVectorParams(
        index=SparseIndexParams(on_disk=False)
    )
},
```

The parameters `m=16` and `ef_construct=200` represent a quality-speed tradeoff. `m` controls the number of bidirectional links per node in the graph; higher values improve recall at the cost of memory. `ef_construct=200` sets the size of the dynamic candidate list during index construction, directly affecting index quality.

Scalar quantization compresses each 32-bit float to an 8-bit integer, reducing memory consumption by approximately 75% while keeping the quantized vectors in RAM (`always_ram=True`) for low-latency access.

### 2.3 Cosine Similarity

Dense vector similarity is computed using cosine similarity. For query vector $\mathbf{q}$ and document vector $\mathbf{d}$:

$$\text{cosine}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \cdot \|\mathbf{d}\|}$$

Cosine similarity is scale-invariant, which matters here because embedding magnitudes vary across languages and text lengths. Qdrant normalizes vectors at index time when `Distance.COSINE` is specified, so the inner product at query time is equivalent to cosine similarity.

---

## 3. Sparse Vector Search (BM25)

### 3.1 BM25 Algorithm

BM25 (Best Match 25) is a probabilistic term-frequency weighting scheme that improves on TF-IDF by saturating term frequency and normalizing for document length. For a query $q$ with terms $t$ and document $d$:

$$\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$

Where:
- $f(t, d)$ is the term frequency of $t$ in document $d$
- $|d|$ is the document length in tokens
- $\text{avgdl}$ is the average document length across the corpus
- $k_1 \in [1.2, 2.0]$ controls term frequency saturation (typically 1.5)
- $b \in [0, 1]$ controls document length normalization (typically 0.75)
- $\text{IDF}(t) = \ln\left(\frac{N - n(t) + 0.5}{n(t) + 0.5} + 1\right)$, where $N$ is the corpus size and $n(t)$ is the number of documents containing $t$

The key insight is the saturation behavior: doubling the term frequency does not double the score. This prevents documents that repeat a keyword many times from dominating results over documents that use the keyword once in a highly relevant context.

### 3.2 FastEmbed Integration

Sparse vectors are produced by Qdrant's BM25 implementation via the FastEmbed library. The sparse index is stored in memory (`on_disk=False`) for query-time performance. Sparse vectors are stored alongside dense vectors in the same Qdrant collection under the `"sparse"` named vector slot.

The `SparseEncoder` class (referenced in `backend/src/AGENTS.md`) wraps FastEmbed's BM25 tokenizer and produces sparse vector representations compatible with Qdrant's `SparseVector` format, where each vector is a list of `(index, value)` pairs for non-zero terms.

### 3.3 Turkish Language Considerations

The Quran collections are indexed in Turkish, which presents specific challenges for BM25. Turkish is an agglutinative language: a single root word can generate dozens of surface forms through suffixation. The word "namaz" (prayer) appears as "namazı", "namazda", "namazdan", "namazını", and many other forms.

Clarus addresses this through two mechanisms:

1. **Query expansion** via `backend/src/turkish_utils.py`, which generates character variants for Turkish-specific letters (ı/i, ö/o, ü/u, ş/s, ğ/g, ç/c) to handle encoding inconsistencies.
2. **Lemmatization** via `backend/src/lemmatizer.py`, which normalizes Turkish text before indexing.

These preprocessing steps improve BM25 recall for Turkish queries without modifying the core BM25 algorithm.

---

## 4. Hybrid Search Strategy

### 4.1 Why Hybrid?

Dense and sparse retrieval have complementary failure modes:

- **Dense search** excels at semantic similarity but can miss exact keyword matches. A query for "Surah Al-Baqara verse 255" may not retrieve the Throne Verse if the embedding space does not encode verse identifiers as semantically meaningful.
- **Sparse search** excels at exact keyword matching but fails on paraphrase and cross-lingual queries. A Turkish query will not match an Arabic verse through BM25 alone.

Combining both retrieval modes captures results that either method would miss independently. This is the core motivation for hybrid search in information retrieval (Karpukhin et al., 2020).

### 4.2 Parallel Dense + Sparse Retrieval

Both retrieval modes run against the same Qdrant collection in a single query using Qdrant's named vector support. The `QuranSearcher` and `BibleSearcher` classes in `backend/src/search.py` issue queries against the `"dense"` named vector slot:

```python
results = qdrant_with_breaker(
    lambda: self.client.query_points(
        collection_name=self.collection_name,
        query=query_vector,
        using="dense",
        limit=limit,
        with_payload=True,
    )
)
```

The sparse retrieval path uses the `"sparse"` named vector slot with the BM25-encoded query. Both result sets are then passed to the RRF fusion function.

All external Qdrant calls are wrapped in a circuit breaker (`qdrant_with_breaker`) that opens after 5 consecutive failures and enters a 60-second half-open recovery period, preventing cascade failures from propagating to the API layer.

---

## 5. Multi-Query Expansion

### 5.1 LLM-Powered Query Variants

A single user query rarely captures all relevant phrasings of a concept. Clarus generates 3-5 query variants per original query using an LLM (Grok 4.1 Fast via OpenRouter). The parallel query preparation pipeline, from `backend/src/ultimate_rag.py`:

```python
enhanced_query, multi_queries = await asyncio.gather(
    self._enhance_query(query, source, detected_language),
    self._generate_multi_queries(
        query,
        query,  # Use original query instead of waiting for enhanced
        source,
        3,
        detected_language,
    ),
)

# Merge: enhanced query + multi-queries, deduplicate
all_queries = [query, enhanced_query, *multi_queries]
```

Enhancement and multi-query generation run in parallel via `asyncio.gather`, reducing latency compared to sequential execution. The final query list is deduplicated while preserving order.

### 5.2 Diversity Strategy

The multi-query generator is prompted to produce variants that approach the concept from different angles: synonyms, related concepts, different phrasings, and cross-lingual equivalents. For a query like "forgiveness in Islam", variants might include "tawbah repentance", "Allah's mercy and pardon", and "divine forgiveness Quran".

Each variant is encoded independently and searched against the collection. The resulting ranked lists are then fused via RRF, which naturally rewards documents that appear across multiple query variants.

All multi-query results are cached in Redis with a 7-day TTL using a semantic similarity threshold of 0.95 cosine similarity, so near-duplicate queries return cached results without additional LLM calls.

---

## 6. Reciprocal Rank Fusion (RRF)

### 6.1 Mathematical Foundation

Reciprocal Rank Fusion (Cormack et al., 2009) is a rank aggregation method that combines multiple ranked lists without requiring score normalization. For a document $d$ appearing in ranked lists $R$:

$$\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

Where $r(d)$ is the rank of document $d$ in list $r$ (1-indexed), and $k$ is a smoothing constant. Documents not appearing in a list contribute 0 to the sum.

The key property of RRF is that it is robust to score scale differences between retrieval methods. A cosine similarity score of 0.85 and a BM25 score of 12.3 cannot be directly compared, but their ranks can be. RRF operates entirely on ordinal rank information.

### 6.2 Why k=60?

The constant $k$ controls how much weight is given to lower-ranked results. With $k=60$:

- Rank 1 contributes $1/61 \approx 0.0164$
- Rank 10 contributes $1/70 \approx 0.0143$
- Rank 60 contributes $1/120 \approx 0.0083$

The ratio between rank 1 and rank 60 is approximately 2:1. This means even a result ranked 60th in one list can meaningfully contribute to the final score if it appears consistently across multiple lists.

The value $k=60$ was proposed in the original Cormack et al. paper as a robust default and has been validated empirically across many IR benchmarks. For this corpus, it was retained without modification after accuracy benchmarks showed no improvement from tuning.

A smaller $k$ (e.g., $k=10$) would make the fusion more aggressive, heavily discounting lower-ranked results. A larger $k$ (e.g., $k=100$) would flatten the score distribution, treating all ranks more equally. $k=60$ sits in a well-validated middle ground.

### 6.3 Implementation

The RRF implementation in `backend/src/ultimate_rag.py` (lines 1053-1085):

```python
def _rrf_fusion(self, result_lists: list[list], k: int = 60) -> list:
    """
    Reciprocal Rank Fusion - merges multiple ranked lists.

    RRF score = sum(1 / (k + rank)) for each list where item appears

    Args:
        result_lists: List of search result lists
        k: RRF constant (default: 60)
    """
    rrf_scores = {}

    for result_list in result_lists:
        for rank, result in enumerate(result_list, start=1):
            # Use result ID as key
            result_id = result.id

            # Calculate RRF score contribution
            score_contribution = 1.0 / (k + rank)

            if result_id not in rrf_scores:
                rrf_scores[result_id] = (result, 0.0)

            # Accumulate RRF score
            current_result, current_score = rrf_scores[result_id]
            rrf_scores[result_id] = (
                current_result,
                current_score + score_contribution,
            )

    # Sort by RRF score descending
    sorted_results = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_results]
```

The implementation uses a dictionary keyed by result ID to accumulate scores across all input lists. Documents appearing in multiple lists accumulate higher scores. The final sort is $O(n \log n)$ where $n$ is the number of unique documents across all lists.

### 6.4 Cross-Collection Fusion

For Bible searches without a specified testament, Clarus searches all three Bible collections (`bible_ot`, `bible_nt`, `bible_apocrypha`) in parallel using `ThreadPoolExecutor`, then fuses the results with RRF. From `backend/src/ultimate_rag.py`:

```python
# Parallel search across all collections
results_by_source = {}
with ThreadPoolExecutor(max_workers=len(collections)) as executor:
    futures = [executor.submit(search_collection, col) for col in collections]

    for future in as_completed(futures):
        source, results = future.result()
        results_by_source[source] = results

# Merge results with RRF fusion
all_results = [results_by_source.get(col, []) for col in collections]
fused_results = self._rrf_fusion(all_results, k=60)
```

The comparative analysis pipeline (`backend/src/comparative_rag.py`) uses an identical RRF implementation to fuse results across all four collections (Quran + three Bible collections) for cross-scripture queries.

### 6.5 Keyword Boost Integration

When a query contains multiple explicit keywords (extracted from the enhanced query), results matching two or more keywords receive a multiplicative boost applied after RRF scoring. From `backend/src/ultimate_rag.py` (lines 620-632):

```python
# Apply keyword coverage boost: results matching 2+ keywords get boosted
for result, rrf_score, matched_keywords in all_results.values():
    match_count = len(matched_keywords)
    # Boost formula: score * (1 + match_count * 0.15)
    # 1 match: no boost
    # 2 matches: +15%
    # 3 matches: +30%
    if match_count >= 2:
        boosted_score = rrf_score * (1 + match_count * 0.15)
    else:
        boosted_score = rrf_score
    boosted_results.append((result, boosted_score, matched_keywords))
```

The boost formula is:

$$\text{score}_{\text{boosted}} = \text{RRF}(d) \times (1 + n_{\text{matches}} \times 0.15)$$

Where $n_{\text{matches}}$ is the number of query keywords matched in the document. The threshold of 2 matches prevents single-keyword noise from triggering the boost. The coefficient 0.15 was chosen to provide a meaningful but not dominant signal: a document matching 3 keywords receives a 30% boost over its base RRF score.

---

## 7. Search Result Caching

### 7.1 Redis Cache Strategy

Individual search results are cached in Redis to avoid redundant Qdrant queries for repeated searches. The cache key is constructed from the collection name, query string, and result limit using SHA-256:

```python
cache_key = f"search:{collection}:{hashlib.sha256((query + str(limit)).encode()).hexdigest()}"
```

Results are serialized to JSON and stored with a 1-hour TTL:

```python
# Cache with 1-hour TTL (3600 seconds)
await redis_manager.client.setex(cache_key, 3600, cached_value)
```

The 1-hour TTL is shorter than the embedding cache TTL (7 days) because search results depend on the collection state, which can change when new verses are indexed. Embedding vectors for a given text are stable indefinitely.

Cache writes are fire-and-forget: the system does not await the cache write, so a slow Redis write does not add latency to the search response. Cache failures are logged as warnings and never propagate to the caller.

---

## 8. Performance Characteristics

The following metrics are based on accuracy benchmarks run against `backend/tests/test_data.json` ground truth.

| Metric | Value | Notes |
|--------|-------|-------|
| Quran recall | 80%+ | Measured against ground truth verse set |
| Bible recall | 100% | All benchmark queries return target verse |
| Multi-agent latency | ~40s | 5 agents + summary generation |
| Cost per query | ~$0.013 | With semantic cache active |
| Cache hit rate | 60-80% | LLM response deduplication |
| Indexed vectors | 43,055 | Across 4 primary collections |
| Embedding dimension | 3,072 | text-embedding-3-large |
| HNSW m parameter | 16 | Bidirectional links per node |
| HNSW ef_construct | 200 | Construction-time candidate list |
| Quantization | INT8 scalar | ~75% RAM reduction |
| RRF k parameter | 60 | Validated default |
| Search cache TTL | 3,600s | 1 hour |
| Embedding cache TTL | 604,800s | 7 days |

The cross-encoder reranking stage was removed on 2026-01-19 after benchmarks showed an 11% recall increase without it. The reranker was introducing false negatives by downranking semantically relevant verses that did not match the reranker's training distribution.

---

## 9. References

Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval*, 758-759.

Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 6769-6781.

Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333-389.

Malkov, Y. A., & Yashunin, D. A. (2018). Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 42(4), 824-836.
