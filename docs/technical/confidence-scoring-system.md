# Two-Phase Sigmoid-Calibrated Confidence Scoring

## Abstract

Clarus computes a confidence score for every search and generation response using a two-phase architecture that separates retrieval quality from answer quality, calibrates each signal individually with sigmoid functions, and fuses the phases via a geometric-arithmetic hybrid blend. This document describes the mathematical foundations of the system, the rationale for each design decision, and the exact parameter values used in production.

---

## 1. Introduction: Why Not Just Average?

The naive approach to confidence scoring is a weighted arithmetic mean of available signals:

$$\text{score} = \sum_i w_i \cdot s_i$$

This fails in practice for two reasons specific to RAG systems.

**The structural ceiling problem.** RRF scores for this corpus range from approximately 0.001 to 0.05. Even a perfect retrieval result produces a raw RRF score around 0.016. When this is multiplied by a weight and summed with other signals, the maximum achievable weighted average is structurally bounded well below 1.0. In the previous version of this system, the ceiling was approximately 72%, meaning a perfect response could never score above 0.72 regardless of quality.

**The compensation problem.** Arithmetic means allow weak signals to be compensated by strong ones. A hallucinated answer with many fake citations can score 50% just by being long. The geometric component of the new system prevents this: if retrieval quality is near zero, the final score is near zero regardless of how polished the generated text appears.

The two-phase sigmoid system resolves both problems. Sigmoid calibration maps raw signals to the full [0, 1] range, and geometric blending enforces the GIGO (Garbage In, Garbage Out) principle.

---

## 2. Sigmoid Calibration (Platt Scaling)

### 2.1 Mathematical Foundation

Each raw signal is passed through a sigmoid function before being combined:

$$f(x) = \frac{1}{1 + e^{-k(x - x_0)}}$$

Where:
- $x_0$ is the **midpoint**: the input value considered "adequate", which maps to an output of exactly 0.5
- $k$ is the **steepness**: controls how quickly the curve transitions from low to high output

From `backend/src/confidence_scorer.py`:

```python
@staticmethod
def _sigmoid(x: float, midpoint: float, steepness: float) -> float:
    """
    Standard sigmoid function: 1 / (1 + exp(-k * (x - midpoint)))

    Args:
        x: Input value
        midpoint: Value that maps to 0.5 output (the "adequate" threshold)
        steepness: How quickly the curve transitions (higher = steeper)

    Returns:
        float: Calibrated value [0.0, 1.0]
    """
    z = -steepness * (x - midpoint)
    # Clamp to prevent math overflow
    z = max(-500.0, min(500.0, z))
    return 1.0 / (1.0 + math.exp(z))
```

The overflow clamp at ±500 prevents `math.exp` from raising an exception on extreme inputs while preserving the asymptotic behavior of the sigmoid.

### 2.2 Why Sigmoid?

Sigmoid calibration is a form of Platt scaling (Platt, 1999), originally developed to convert SVM decision function outputs into probability estimates. The key properties that make it appropriate here are:

1. **Bounded output.** The sigmoid maps any real input to (0, 1), so no signal can produce an out-of-range confidence value.
2. **Monotonicity.** Higher raw signal values always produce higher calibrated values.
3. **Tunable sensitivity.** The midpoint and steepness parameters allow each signal to be calibrated independently to its natural scale. An RRF score of 0.012 and a word count of 100 require very different sigmoid parameters to produce comparable outputs.
4. **Graceful degradation.** Signals near zero produce outputs near zero, not negative values, which would require clamping.

---

## 3. Phase 1: Retrieval Confidence

Phase 1 answers the question: did the search engine find relevant documents? It operates on the raw search results before the LLM generates any text.

### 3.1 Score Quality Signal

The score quality signal measures the absolute magnitude of the retrieved RRF scores.

- **Metric:** Median of the top-5 RRF scores
- **Sigmoid parameters:** midpoint = 0.012, steepness = 200.0

The median is used instead of the mean to be robust against outliers. A single very high-scoring result does not inflate the signal if the remaining results are weak.

The steepness of 200.0 is high because RRF scores occupy a narrow range (approximately 0.001 to 0.05). A steepness of 200 produces a transition width of roughly 0.02 score units, which is appropriate for this range.

From `backend/src/confidence_scorer.py`:

```python
# Signal 1: Score Quality
# Uses median of top-5 RRF scores, sigmoid-calibrated
if scores:
    top_scores = sorted(scores[: min(5, len(scores))], reverse=True)
    median_idx = len(top_scores) // 2
    median_score = top_scores[median_idx]
    score_quality = self._sigmoid(median_score, self.RRF_MIDPOINT, self.RRF_STEEPNESS)
else:
    score_quality = 0.0
```

Constants:
```python
RRF_MIDPOINT = 0.012   # "adequate" median RRF score for top-5 results
RRF_STEEPNESS = 200.0  # High steepness for small RRF value range (0.001-0.05)
```

### 3.2 Score Separation Signal

The score separation signal detects whether the search found a "clear winner" or returned a flat, ambiguous ranking.

- **Metric:** Ratio of the top-1 score to the top-5 score ($\text{score}_1 / \text{score}_5$)
- **Sigmoid parameters:** midpoint = 1.5, steepness = 3.0

A ratio above 1.5 means the top result scores at least 50% higher than the fifth result, indicating the search engine found a distinctly relevant document. A flat ratio near 1.0 suggests ambiguity: many documents are equally plausible, which typically correlates with lower answer quality.

```python
# Signal 2: Score Separation
# Does the top result clearly stand out from rank 5?
if scores and len(scores) >= 2:
    top = scores[0]
    fifth = scores[min(4, len(scores) - 1)]
    if fifth > 1e-10:
        separation_ratio = top / fifth
    else:
        separation_ratio = 10.0  # Very high if bottom is near-zero
    score_separation = self._sigmoid(
        separation_ratio,
        self.SEPARATION_MIDPOINT,
        self.SEPARATION_STEEPNESS,
    )
else:
    score_separation = 0.5  # Neutral if insufficient data
```

Constants:
```python
SEPARATION_MIDPOINT = 1.5  # top/5th ratio considered "clear winner"
SEPARATION_STEEPNESS = 3.0
```

When fewer than 2 results are available, the signal defaults to 0.5 (neutral) rather than 0.0 (failure), because a single high-quality result is not evidence of poor retrieval.

### 3.3 Result Coverage Signal

The result coverage signal measures whether the search returned the expected number of results.

- **Metric:** $\min(\text{actual} / \text{expected}, 1.0)$

This signal is not sigmoid-calibrated because it is already bounded in [0, 1] and has a natural linear interpretation. If the system requested 10 results and received 2, coverage is 0.2. The `min(..., 1.0)` clamp prevents over-coverage from inflating the signal.

```python
# Signal 3: Result Coverage
# Did we get the expected number of results?
if expected_results > 0:
    result_coverage = min(actual_results / expected_results, 1.0)
else:
    result_coverage = 1.0
```

### 3.4 Phase 1 Composition

The three signals are combined as a weighted sum:

$$\text{Retrieval} = 0.60 \times \text{Quality} + 0.25 \times \text{Separation} + 0.15 \times \text{Coverage}$$

```python
# Combine Phase 1 signals
retrieval = 0.60 * score_quality + 0.25 * score_separation + 0.15 * result_coverage
```

Score quality receives the highest weight (0.60) because it directly measures whether the retrieved documents are relevant. Separation (0.25) is a secondary quality indicator. Coverage (0.15) is a sanity check that rarely fails in practice.

For multi-collection queries (compare mode), a source breadth bonus is added:

$$\text{Retrieval} = \min\left(\text{Retrieval} + 0.05 \times \frac{\text{collections with results}}{\text{total collections}}, 1.0\right)$$

```python
# Source breadth BONUS (additive, not penalty)
# Only applies for multi-collection queries (compare mode)
breadth_bonus = 0.0
if total_collections > 1:
    breadth_bonus = 0.05 * (collections_with_results / total_collections)
    retrieval = min(retrieval + breadth_bonus, 1.0)
```

The maximum breadth bonus is 0.05 (5 percentage points), applied only when results are found across all searched collections.

---

## 4. Phase 2: Answer Quality

Phase 2 answers the question: is the generated answer well-grounded in the retrieved documents? It operates on the generated text and citation metadata.

### 4.1 Citation Density Signal

The citation density signal measures how frequently the answer cites retrieved verses, normalized by the expected density for the query type.

- **Metric:** Citations per paragraph vs. expected density
- **Sigmoid parameters:** midpoint = `expected_density * 0.7`, steepness = 2.0

Expected densities per query type:

```python
EXPECTED_DENSITY = {
    "search": 2.0,   # ~2 citations per paragraph
    "ask": 3.0,      # ~3 citations per paragraph
    "compare": 4.0,  # ~4 citations per paragraph (multi-source)
}
```

The midpoint is set to 70% of the expected density rather than 100%, because the sigmoid at 70% of expected produces an output of 0.5, meaning "adequate but not excellent". This prevents the system from being too harsh on answers that cite slightly fewer verses than the target density.

```python
# Signal 1: Citation Density
expected_density = self.EXPECTED_DENSITY.get(query_type, 3.0)
actual_density = cited_count / max(num_paragraphs, 1)
citation_density = self._sigmoid(
    actual_density, expected_density * 0.7, self.DENSITY_STEEPNESS
)
```

Constants:
```python
DENSITY_STEEPNESS = 2.0  # Steepness for citation density sigmoid
```

### 4.2 Top-K Citation Rate Signal

The top-K citation rate signal measures whether the LLM used the highest-ranked retrieved results, rather than lower-ranked ones.

- **Metric:** Estimated fraction of citations drawn from the top-10 results
- **Sigmoid parameters:** midpoint = 0.5, steepness = 6.0

The estimation is a heuristic: the system assumes citations come from the top results first, because the LLM prompt instructs it to prioritize highest-scored verses. This is an approximation; the true citation source is not tracked at the verse level.

```python
# Signal 2: Top-K Citation Rate (estimated)
# Heuristic: assume citations come from top results first
top_k = min(10, total_results)
if top_k > 0:
    estimated_top_k_cited = min(cited_count, top_k)
    top_k_rate = estimated_top_k_cited / top_k
    top_k_citation_rate = self._sigmoid(
        top_k_rate, self.TOP_K_MIDPOINT, self.TOP_K_STEEPNESS
    )
else:
    top_k_citation_rate = 0.0
```

Constants:
```python
TOP_K_MIDPOINT = 0.5   # 50% of top-K cited = adequate
TOP_K_STEEPNESS = 6.0
```

### 4.3 Answer Substance Signal

The answer substance signal prevents high confidence scores for trivially short answers.

- **Metric:** $\min(\text{word count} / \text{min words}, 1.0)$

Minimum word counts per query type:

```python
MIN_WORDS = {
    "search": 50,
    "ask": 100,
    "compare": 200,
}
```

```python
# Signal 3: Answer Substance
# Does the answer meet minimum length for its type?
min_words = self.MIN_WORDS.get(query_type, 100)
answer_substance = min(answer_length_words / max(min_words, 1), 1.0)
```

This signal is not sigmoid-calibrated because it is already bounded in [0, 1] and the linear interpretation is appropriate: an answer at exactly the minimum length scores 1.0, and shorter answers score proportionally lower.

### 4.4 Phase 2 Composition

The three signals are combined as a weighted sum:

$$\text{Answer} = 0.50 \times \text{Density} + 0.35 \times \text{TopK} + 0.15 \times \text{Substance}$$

```python
# Combine Phase 2 signals
answer_qual = (
    0.50 * citation_density
    + 0.35 * top_k_citation_rate
    + 0.15 * answer_substance
)
```

Citation density receives the highest weight (0.50) because it is the most direct measure of answer grounding. Top-K citation rate (0.35) rewards use of the best retrieved results. Substance (0.15) is a floor check.

---

## 5. Final Fusion: Geometric-Arithmetic Hybrid

### 5.1 The GIGO Principle

The final score combines Phase 1 and Phase 2 using a hybrid of geometric and arithmetic means. The geometric component enforces the GIGO principle: if retrieval quality is near zero, the final score is near zero regardless of answer quality.

$$\text{Geometric} = \text{Retrieval}^{0.6} \times \text{Answer}^{0.4}$$

$$\text{Arithmetic} = 0.55 \times \text{Retrieval} + 0.45 \times \text{Answer}$$

$$\text{Raw} = 0.6 \times \text{Geometric} + 0.4 \times \text{Arithmetic}$$

```python
# Final: Geometric-Arithmetic Hybrid Blend
# Geometric component: bad retrieval tanks the score (GIGO principle)
# Arithmetic component: allows partial compensation
#
# retrieval^0.6 × answer^0.4 → retrieval matters more in geometric
# 0.55 × retrieval + 0.45 × answer → balanced in arithmetic
# 60% geometric + 40% arithmetic → lean toward penalizing weak links
if retrieval_confidence > 0 and answer_quality > 0:
    geometric = (retrieval_confidence**0.6) * (answer_quality**0.4)
else:
    geometric = 0.0

arithmetic = 0.55 * retrieval_confidence + 0.45 * answer_quality
raw = 0.6 * geometric + 0.4 * arithmetic
```

The exponents in the geometric component (0.6 for retrieval, 0.4 for answer) weight retrieval more heavily, reflecting the foundational role of retrieval quality. A system that retrieves irrelevant documents cannot produce a trustworthy answer, even if the generated text appears coherent.

The 60/40 split between geometric and arithmetic components allows partial compensation: a very strong answer can partially offset mediocre retrieval, but cannot fully compensate for it.

### 5.2 Final Sigmoid Calibration

The raw score is passed through a final sigmoid to spread the distribution across the user-facing range:

$$\text{Calibrated} = \frac{1}{1 + e^{-6.0 \times (\text{Raw} - 0.45)}}$$

```python
# Final sigmoid calibration
# Maps: 0.3 raw → ~0.45, 0.5 raw → ~0.65, 0.7 raw → ~0.82, 0.9 raw → ~0.93
calibrated = self._sigmoid(raw, self.FINAL_MIDPOINT, self.FINAL_STEEPNESS)
```

Constants:
```python
FINAL_MIDPOINT = 0.45  # Center of final calibration sigmoid
FINAL_STEEPNESS = 6.0  # Spread of final sigmoid
```

The midpoint of 0.45 means a raw score of 0.45 maps to a calibrated score of 0.50. Raw scores below 0.45 are compressed toward the lower end of the user-facing range; raw scores above 0.45 are stretched toward the upper end.

### 5.3 Score Clamping

The calibrated score is clamped to [0.15, 0.95]:

$$\text{Final} = \max(0.15, \min(0.95, \text{Calibrated}))$$

```python
# Floor at 0.15 (we returned something), ceiling at 0.95 (never 100% certain)
final_score = max(0.15, min(0.95, calibrated))
```

The floor of 0.15 reflects that any response that returns results has some minimum value. The ceiling of 0.95 reflects epistemic humility: the system never claims certainty, because the ground truth of theological interpretation is not computable.

---

## 6. Removed Signals

### 6.1 `llm_confidence`

**What it was:** The system previously asked the LLM to self-report its confidence on a 0-1 scale as part of the generation prompt.

**Why removed:** Dead signal. RLHF-tuned models are trained to be helpful and confident. In practice, models consistently returned values of 0.9 or higher regardless of actual retrieval quality, including on queries where the retrieved documents were clearly irrelevant. The signal added noise without predictive value.

This is a known failure mode documented in Niculescu-Mizil & Caruana (2005): models trained with cross-entropy loss tend to produce overconfident probability estimates that require post-hoc calibration. Asking the model to self-report confidence bypasses calibration entirely.

### 6.2 `citation_coverage`

**What it was:** The fraction of retrieved verses that were cited in the generated answer.

**Why removed:** Structural penalty on correct behavior. When a user asks for a brief summary and the system retrieves 20 relevant verses, the LLM correctly cites 2-3 of the most relevant ones. The old metric penalized this behavior by computing $2/20 = 0.10$ coverage, producing a low signal even for a high-quality concise answer.

The replacement signal, citation density, measures citations per generated paragraph rather than against the retrieved pool. This rewards appropriate citation density for the answer length and query type, without penalizing conciseness.

---

## 7. Score Distribution Analysis

The following table shows the mapping from raw scores (before final sigmoid) to calibrated final scores, based on the parameters `FINAL_MIDPOINT=0.45` and `FINAL_STEEPNESS=6.0`:

| Raw Score | Calibrated Score | Interpretation |
|-----------|-----------------|----------------|
| 0.10 | 0.18 | Very poor retrieval, minimal answer |
| 0.20 | 0.25 | Poor retrieval or very short answer |
| 0.30 | 0.37 | Below-adequate retrieval |
| 0.40 | 0.49 | Near-adequate, borderline |
| 0.45 | 0.50 | Adequate (sigmoid midpoint) |
| 0.50 | 0.60 | Good retrieval and answer |
| 0.60 | 0.73 | Strong retrieval, well-cited answer |
| 0.70 | 0.83 | Very strong retrieval |
| 0.80 | 0.90 | Excellent retrieval and answer |
| 0.90 | 0.95 | Near-maximum (clamped) |

The sigmoid stretches the middle range (0.3-0.7 raw) into a wider user-facing range (0.37-0.83), making the difference between adequate and excellent results visible to users.

---

## 8. Tuning Guide

All parameters are defined as class constants in `backend/src/confidence_scorer.py`. The following table lists each parameter, its current value, and guidance for adjustment.

| Parameter | Current Value | Description | Adjustment Guidance |
|-----------|--------------|-------------|---------------------|
| `RRF_MIDPOINT` | `0.012` | Median RRF score considered "adequate" | Lower if scores are consistently below 0.012 for good results. Raise if noise results are scoring too high. |
| `RRF_STEEPNESS` | `200.0` | Sensitivity of score quality sigmoid | Raise to make the system stricter about RRF score magnitude. Lower to smooth the transition. |
| `SEPARATION_MIDPOINT` | `1.5` | Top/5th score ratio for "clear winner" | Lower if the system is too harsh on ambiguous multi-topic queries. |
| `SEPARATION_STEEPNESS` | `3.0` | Sensitivity of separation sigmoid | Raise to make the system stricter about requiring a clear top result. |
| `DENSITY_STEEPNESS` | `2.0` | Sensitivity of citation density sigmoid | Raise to penalize missing citations more aggressively. |
| `TOP_K_MIDPOINT` | `0.5` | Fraction of top-K results cited = adequate | Lower if the LLM consistently cites fewer than 50% of top results. |
| `TOP_K_STEEPNESS` | `6.0` | Sensitivity of top-K citation sigmoid | Raise to make the system stricter about using top results. |
| `FINAL_MIDPOINT` | `0.45` | Center of final calibration sigmoid | Lower to boost all scores globally. Raise to make the system more conservative. |
| `FINAL_STEEPNESS` | `6.0` | Spread of final sigmoid | Lower to compress the score distribution. Raise to spread it further. |
| `EXPECTED_DENSITY["search"]` | `2.0` | Expected citations per paragraph for search | Adjust based on observed citation patterns in search responses. |
| `EXPECTED_DENSITY["ask"]` | `3.0` | Expected citations per paragraph for ask | Adjust based on observed citation patterns in ask responses. |
| `EXPECTED_DENSITY["compare"]` | `4.0` | Expected citations per paragraph for compare | Adjust based on observed citation patterns in compare responses. |
| `MIN_WORDS["search"]` | `50` | Minimum word count for search responses | Lower if brief search summaries are acceptable. |
| `MIN_WORDS["ask"]` | `100` | Minimum word count for ask responses | Raise if one-paragraph answers are insufficient. |
| `MIN_WORDS["compare"]` | `200` | Minimum word count for compare responses | Raise if comparative essays are expected to be longer. |

When tuning, adjust one parameter at a time and evaluate against the ground truth benchmark in `backend/tests/test_data.json`. The accuracy benchmark measures retrieval recall, not confidence calibration directly, but changes to confidence parameters can affect how results are ranked and filtered downstream.

---

## 9. References

Platt, J. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. *Advances in Large Margin Classifiers*, 10(3), 61-74.

Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. *Proceedings of the 22nd International Conference on Machine Learning (ICML)*, 625-632.

Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval*, 758-759.

Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333-389.
