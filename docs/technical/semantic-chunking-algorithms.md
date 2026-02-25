# Semantic Chunking Algorithms for Verse-Level Text

## Abstract

Clarus implements embedding-based semantic chunking to group related verses into retrieval units for RAG (Retrieval-Augmented Generation) search. The algorithm computes cosine similarity between consecutive verse embeddings, detects topic boundaries where similarity drops below a configurable threshold, and enforces structural constraints (surah/chapter boundaries, maximum chunk size). This document describes the chunking algorithms for both the Quran (`SemanticVerseChunker`) and Bible (`BibleSemanticVerseChunker`), including the mathematical formulation, threshold strategies, and the differences between the two implementations.

---

## 1. Introduction

A RAG system retrieves text chunks from a vector database and passes them to a language model as context. The quality of retrieval depends critically on how the source text is divided into chunks. Too small, and individual chunks lack context. Too large, and the embedding averages over unrelated content, reducing retrieval precision.

Sacred texts present a specific version of this problem. Verses are the natural atomic unit of religious text: they are cited individually, memorized individually, and carry independent meaning. Splitting a verse across two chunks would be semantically and culturally wrong. At the same time, many topics in the Quran and Bible span multiple consecutive verses. A question about the creation narrative in Genesis should retrieve the full passage, not a single verse.

The chunking problem for sacred texts therefore has three hard constraints:

1. **Verse atomicity**: A verse must never be split. It is either entirely in one chunk or entirely in another.
2. **Structural boundaries**: Chunks must not cross surah (Quran) or chapter (Bible) boundaries.
3. **Topic coherence**: Semantically related consecutive verses should be grouped together.

The Clarus chunking algorithm satisfies all three constraints.

---

## 2. The Chunking Problem for Sacred Texts

### 2.1 Verse Atomicity Constraint

Both `SemanticVerseChunker` and `BibleSemanticVerseChunker` treat verses as indivisible units. The chunking algorithm operates on a list of verse objects and produces groups of whole verses. No verse is ever split between chunks.

This is enforced structurally: the algorithm only decides *where to place boundaries between verses*, never within a verse. The `SemanticChunk` dataclass stores `verse_ids: list[str]` and `combined_translation: str` (the concatenation of all verse translations in the chunk), making it impossible to represent a partial verse.

### 2.2 Structural Boundaries

Surah and chapter boundaries are treated as hard breaks. When the surah ID (Quran) or book/chapter ID (Bible) changes between two consecutive verses, a new chunk always begins regardless of semantic similarity.

```python
# Quran: surah boundary check
if self.respect_surah_boundary:
    if self._verses[i].surah_id != self._verses[next_verse_idx].surah_id:
        boundaries.append(next_verse_idx)
        continue

# Bible: book and chapter boundary checks
if curr_verse.book_id != next_verse.book_id:
    boundaries.append(next_verse_idx)
    continue
if self.respect_chapter_boundary and curr_verse.chapter != next_verse.chapter:
    boundaries.append(next_verse_idx)
    continue
```

The `continue` statement skips the semantic similarity check entirely for structural boundaries, ensuring they are never overridden.

### 2.3 Topic Coherence

Within a surah or chapter, the algorithm uses embedding similarity to detect topic shifts. The intuition is that consecutive verses discussing the same topic will have similar embeddings, while a shift in topic will produce a drop in similarity. The algorithm places a chunk boundary wherever similarity falls below a computed threshold.

---

## 3. Embedding-Based Similarity

### 3.1 Consecutive Verse Similarity

The algorithm computes cosine similarity between the embeddings of each consecutive pair of verses. For a sequence of $n$ verses with embeddings $\mathbf{e}_1, \mathbf{e}_2, \ldots, \mathbf{e}_n$, the similarity array has $n-1$ elements:

$$\text{sim}(v_i, v_{i+1}) = \cos(\mathbf{e}_i, \mathbf{e}_{i+1}) = \frac{\mathbf{e}_i \cdot \mathbf{e}_{i+1}}{\|\mathbf{e}_i\| \cdot \|\mathbf{e}_{i+1}\|}$$

The implementation normalizes all embeddings first, then computes the dot product of consecutive pairs:

```python
def compute_similarities(self, embeddings: np.ndarray | None = None) -> np.ndarray:
    # Normalize embeddings for cosine similarity
    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    normalized = embeddings_array / norms

    # Compute similarity between consecutive pairs
    # similarity[i] = cosine_sim(verse[i], verse[i+1])
    similarities = np.sum(normalized[:-1] * normalized[1:], axis=1)
    return similarities
```

The normalization step converts each embedding vector to unit length. After normalization, the dot product equals the cosine similarity, which is computed efficiently as an element-wise product followed by a sum along the embedding dimension.

Embeddings are produced by OpenAI `text-embedding-3-large`, which outputs 3072-dimensional vectors. The Quran chunker embeds Turkish translations; the Bible chunker embeds English text.

### 3.2 Sliding Window Approach

The similarity computation is inherently a sliding window of size 2: each similarity value $\text{sim}(v_i, v_{i+1})$ captures the local topic continuity between adjacent verses. This is a deliberate design choice. A wider window (e.g., comparing $v_i$ to the centroid of the next $k$ verses) would smooth over short topic transitions and miss fine-grained boundaries.

The resulting similarity array is a 1D signal over verse positions. Topic boundaries appear as local minima in this signal.

---

## 4. Boundary Detection

### 4.1 Fixed Threshold Strategy

The simplest strategy places a boundary wherever similarity falls below a fixed value:

$$\text{boundary at } i \iff \text{sim}(v_i, v_{i+1}) < \tau$$

where $\tau$ is the `similarity_threshold` parameter (default: 0.75).

```python
else:  # "fixed" or unknown
    computed_threshold = threshold
    print(f"Fixed threshold: {computed_threshold:.4f}")
```

A threshold of 0.75 means that two consecutive verses must share at least 75% cosine similarity to remain in the same chunk. This is a relatively conservative threshold that produces moderately sized chunks.

### 4.2 Percentile-Based Threshold

The default strategy in `create_semantic_chunks()` is `threshold_type="percentile"`. Rather than using a fixed value, it computes the threshold as a percentile of the observed similarity distribution:

$$\tau_p = \text{percentile}(\{\text{sim}(v_i, v_{i+1})\}_{i=1}^{n-1},\ p)$$

```python
if threshold_type == "percentile":
    percentile_value = threshold if threshold <= 100 else 10
    computed_threshold = np.percentile(similarities_array, percentile_value)
    print(f"Percentile-based threshold: {computed_threshold:.4f} (p={percentile_value})")
```

When `threshold=0.75` and `threshold_type="percentile"`, the value 0.75 is interpreted as the 75th percentile of the similarity distribution. This means approximately 25% of consecutive verse pairs will be split into separate chunks. The percentile approach adapts to the actual similarity distribution of the corpus, making it more robust than a fixed threshold across different surahs or books with varying topic density.

### 4.3 Standard Deviation-Based Threshold

The standard deviation strategy places boundaries at positions where similarity falls more than $k$ standard deviations below the mean:

$$\tau_\sigma = \mu - k \cdot \sigma$$

where $\mu = \text{mean}(\text{similarities})$ and $\sigma = \text{std}(\text{similarities})$.

```python
elif threshold_type == "std":
    k = threshold if threshold < 10 else 1.0
    computed_threshold = np.mean(similarities_array) - k * np.std(similarities_array)
    print(f"Std-based threshold: {computed_threshold:.4f} (k={k})")
```

With $k=1.0$, this splits at positions more than one standard deviation below the mean similarity. This strategy is sensitive to the variance of the similarity distribution and tends to produce fewer, larger chunks than the percentile approach.

### 4.4 Interquartile Range Threshold

The IQR strategy uses the interquartile range to identify outlier low-similarity positions:

$$\tau_\text{IQR} = Q_1 - k \cdot \text{IQR}$$

where $Q_1$ is the 25th percentile, $\text{IQR} = Q_3 - Q_1$, and $k$ defaults to 1.5.

```python
elif threshold_type == "interquartile":
    q1 = np.percentile(similarities_array, 25)
    q3 = np.percentile(similarities_array, 75)
    iqr = q3 - q1
    k = threshold if threshold < 10 else 1.5
    computed_threshold = q1 - k * iqr
    print(f"IQR-based threshold: {computed_threshold:.4f} (Q1={q1:.4f}, IQR={iqr:.4f}, k={k})")
```

This is analogous to the standard box-plot outlier detection rule. Positions where similarity is unusually low (below the lower fence) are treated as topic boundaries.

### 4.5 Gradient-Based Detection

The gradient strategy detects boundaries where the similarity signal drops sharply, rather than where it is absolutely low:

```python
elif threshold_type == "gradient":
    gradient_values = np.gradient(similarities_array)
    gradients = gradient_values
    grad_threshold = float(np.percentile(gradient_values, threshold if threshold <= 100 else 10))
    computed_threshold = None
    print(f"Gradient-based detection: threshold={grad_threshold:.4f}")
```

A boundary is placed where the gradient (rate of change) of the similarity signal falls below the $p$-th percentile of all gradients. This detects sudden drops in similarity even when the absolute similarity value remains relatively high.

### 4.6 How Boundaries Are Detected

The boundary detection loop iterates over all consecutive verse pairs. Index 0 is always a boundary (the first verse always starts a chunk). For each subsequent position, the algorithm checks structural constraints first, then applies the semantic threshold:

```python
boundaries = [0]  # First verse always starts a chunk

for i, sim in enumerate(similarities_array):
    next_verse_idx = i + 1

    # Hard structural boundary (surah/chapter change)
    if self.respect_surah_boundary:
        if self._verses[i].surah_id != self._verses[next_verse_idx].surah_id:
            boundaries.append(next_verse_idx)
            continue

    # Semantic threshold check
    elif sim < computed_threshold:
        boundaries.append(next_verse_idx)
```

The result is a list of indices where new chunks begin.

---

## 5. Chunk Constraints

### 5.1 Maximum Chunk Size

The default maximum chunk size is 10 verses (`max_chunk_size=10`). When the boundary detection algorithm produces a chunk larger than this limit, `_apply_size_constraints()` subdivides it by finding the lowest-similarity position within the allowed range:

```python
if chunk_size > self.max_chunk_size:
    start_idx = prev_boundary
    while start_idx + self.max_chunk_size < current_boundary:
        search_start = start_idx
        search_end = min(start_idx + self.max_chunk_size, current_boundary)

        if search_end - 1 > search_start:
            local_sims = similarities_array[search_start : search_end - 1]
            min_sim_idx = np.argmin(local_sims) + search_start + 1
            adjusted.append(min_sim_idx)
            start_idx = min_sim_idx
```

This greedy approach finds the weakest semantic link within each window and splits there, producing the most natural subdivision of an oversized chunk.

### 5.2 Minimum Chunk Size

The minimum chunk size is 1 verse (`min_chunk_size=1`). Single-verse chunks are permitted when a verse is structurally isolated (e.g., the last verse of a surah before a boundary) or semantically distinct from its neighbors. There is no merging of small chunks; the algorithm accepts single-verse chunks rather than forcing artificial groupings.

### 5.3 Surah and Chapter Boundary Enforcement

Surah boundaries (Quran) and book/chapter boundaries (Bible) are enforced as hard constraints that override semantic similarity. This reflects the editorial structure of the texts: surah and chapter divisions were established by religious tradition and carry meaning independent of topic continuity.

The Bible chunker enforces book boundaries unconditionally and chapter boundaries conditionally (controlled by `respect_chapter_boundary`, default `True`):

```python
# Always break on book change
if curr_verse.book_id != next_verse.book_id:
    boundaries.append(next_verse_idx)
    continue

# Optionally break on chapter change
if self.respect_chapter_boundary and curr_verse.chapter != next_verse.chapter:
    boundaries.append(next_verse_idx)
    continue
```

---

## 6. Quality Metrics

### 6.1 Internal Similarity

Each `SemanticChunk` and `BibleSemanticChunk` stores the internal similarity values and their average:

```python
internal_sims = []
if end_idx - start_idx > 1:
    internal_sims = similarities_array[start_idx : end_idx - 1].tolist()
```

The `avg_internal_similarity` field is computed in `__post_init__`:

$$\bar{s}_\text{chunk} = \frac{1}{|C| - 1} \sum_{i=1}^{|C|-1} \text{sim}(v_i, v_{i+1})$$

where $|C|$ is the number of verses in the chunk. A high average internal similarity indicates that the chunk is topically coherent. Single-verse chunks have no internal similarity (the field is an empty list).

The `get_statistics()` method on `SemanticVerseChunker` reports the full distribution of the similarity signal:

```python
return {
    "num_verses": len(self._verses),
    "similarity_mean": float(np.mean(self._similarities)),
    "similarity_std": float(np.std(self._similarities)),
    "similarity_min": float(np.min(self._similarities)),
    "similarity_max": float(np.max(self._similarities)),
    "similarity_p10": float(np.percentile(self._similarities, 10)),
    "similarity_p25": float(np.percentile(self._similarities, 25)),
    "similarity_p50": float(np.percentile(self._similarities, 50)),
    "threshold": self.similarity_threshold,
    "max_chunk_size": self.max_chunk_size,
}
```

### 6.2 Boundary Sharpness

Boundary sharpness is the drop in similarity at a chunk boundary relative to the average internal similarity of the adjacent chunks. A sharp boundary indicates a genuine topic transition; a soft boundary may indicate an arbitrary split.

While not computed as an explicit metric in the current implementation, it can be derived from the stored `internal_similarities` and the similarity value at the boundary position. High-quality chunking produces boundaries where the similarity drops significantly below the average internal similarity of the surrounding chunks.

---

## 7. Quran-Specific Implementation

The `SemanticVerseChunker` class in `semantic_chunker.py` processes Quran verses in Turkish translation. Key implementation details:

**Data model**: Each verse is a `QuranChunk` object with fields including `surah_id`, `verse_id`, `translation` (Turkish), `arabic_text`, `translation_normalized`, and `translation_lemma`. The chunker embeds the `translation` field (Turkish text).

**Output**: `SemanticChunk` objects with a `chunk_id` in the format `{surah_id}:{start_verse}-{end_verse}_semantic` (e.g., `2:30-33_semantic`). The chunk stores both `combined_translation` (Turkish) and `combined_arabic` (Arabic), as well as `combined_normalized` and `combined_lemma` for text processing.

**Embedding caching**: Embeddings are cached to `cache/verse_embeddings.npy` with a metadata file tracking the number of verses. The cache is invalidated if the verse count changes:

```python
if use_cache and cache_path.exists() and cache_meta_path.exists():
    with open(cache_meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("num_verses") == len(self._verses):
        loaded_embeddings = np.load(cache_path)
        return loaded_embeddings
```

**Default parameters**:
- `similarity_threshold=0.75`
- `max_chunk_size=10`
- `min_chunk_size=1`
- `respect_surah_boundary=True`
- `threshold_type="percentile"` (in `create_semantic_chunks()`)

**Batch encoding**: Embeddings are computed in batches of 32 verses using the synchronous `DenseEncoder.encode_batch()`.

---

## 8. Bible-Specific Implementation

The `BibleSemanticVerseChunker` class in `bible_semantic_chunker.py` shares the same algorithmic core as the Quran chunker but differs in several ways:

**Structural boundaries**: The Bible chunker enforces both book boundaries (always) and chapter boundaries (configurable). The Quran chunker only enforces surah boundaries. This reflects the different editorial structures: the Bible's chapter divisions are a later addition (13th century CE) and less semantically meaningful than surah divisions, but they are still respected by default.

**Chunk ID format**: Bible chunks use the format `{translation}:{book_id}:{chapter}:{start_verse}-{end_verse}_semantic` (e.g., `kjva:1:1:1-5_semantic`), encoding the translation, book, chapter, and verse range.

**Async embedding**: The Bible chunker supports async embedding computation for faster processing of the larger Bible corpus (38,819 verses across OT, NT, and Apocrypha vs. 6,236 Quran verses):

```python
async def _compute_embeddings_async(self, texts, show_progress=True):
    return await self.async_encoder.encode_batch_async(
        texts,
        batch_size=256,   # 8x larger than sync default
        max_concurrent=10, # Parallel API calls
        show_progress=show_progress,
    )
```

**Per-translation caching**: Embedding cache files are named `bible_{translation}_embeddings.npy`, allowing multiple translations to be cached independently.

**Testament tracking**: Each `BibleSemanticChunk` stores a `testament` field (`OT`, `NT`, or `Apocrypha`), enabling testament-level filtering in search.

**Default parameters**: Identical to the Quran chunker: `similarity_threshold=0.75`, `max_chunk_size=10`, `respect_chapter_boundary=True`.

---

## 9. Comparison with Alternative Approaches

| Approach | Description | Limitation for Sacred Texts |
|---|---|---|
| **Fixed-size chunking** | Split every $k$ tokens or sentences | Splits verses mid-sentence; ignores topic structure |
| **Sentence-window chunking** | Overlap windows of $k$ sentences | Verse boundaries not respected; redundant storage |
| **Recursive character splitting** | Split on paragraph, sentence, word boundaries | No concept of verse atomicity |
| **Semantic chunking (this work)** | Embedding similarity with structural constraints | Requires embedding computation at index time |

Fixed-size chunking is the most common approach in general RAG systems (LangChain's `RecursiveCharacterTextSplitter`, LlamaIndex's `SentenceSplitter`). For sacred texts, it is inappropriate because it treats the text as a continuous stream and will split verses at arbitrary points.

Sentence-window chunking (Anthropic's "Contextual Retrieval" approach) adds surrounding context to each chunk at retrieval time. This could complement the Clarus approach but does not address the verse atomicity constraint at indexing time.

The Clarus approach is most similar to LangChain's `SemanticChunker` (Reimers & Gurevych, 2019), which also uses embedding similarity to detect topic boundaries. The key additions are:

1. Hard structural boundary enforcement (surah/chapter)
2. Maximum chunk size with similarity-guided subdivision
3. Storage of internal similarity metrics for quality assessment
4. Separate implementations for Quran (Turkish) and Bible (English) with appropriate caching strategies

---

## 10. References

Anthropic. (2024). "Contextual Retrieval." Anthropic Research Blog. https://www.anthropic.com/research/contextual-retrieval

LangChain. (2024). "SemanticChunker." LangChain Documentation. https://python.langchain.com/docs/how_to/semantic-chunker/

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In *Proceedings of EMNLP 2019* (pp. 3982-3992). Association for Computational Linguistics.

Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333-389.

Text Embeddings API. (2024). OpenAI `text-embedding-3-large` model documentation. https://platform.openai.com/docs/guides/embeddings
