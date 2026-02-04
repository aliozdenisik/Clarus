# Confidence Scoring Methodology

**Last Updated:** 2024-05-20  
**Version:** 2.0 (Two-Phase Sigmoid-Calibrated)

## Overview

Clarus uses a **Two-Phase Sigmoid-Calibrated** confidence scoring system designed to mimic human intuition about search quality. This replaces the previous "weighted arithmetic mean" approach, which suffered from a structural ceiling of ~72% and failed to distinguish between "good" (80%) and "excellent" (95%) results.

The new system produces a meaningful score distribution (40-95%) where:
- **< 50%**: Poor retrieval or hallucinated answer.
- **60-75%**: Decent retrieval, but potentially missing key context.
- **80-90%**: Strong retrieval and well-grounded answer.
- **> 90%**: Exceptional match (definitive source found).

---

## The Paradigm Shift

### The Old Way: Arithmetic Mean
Previously, we used a weighted average of 6 raw signals (e.g., `0.3 * rrf_score + 0.2 * citation_count`).
- **Problem 1: The Ceiling Effect.** RRF scores are naturally low (0.01 - 0.05). Even a "perfect" match rarely exceeded a raw weighted sum of 0.72.
- **Problem 2: Linear Penalties.** A missing citation linearly penalized the score, even if the answer was short and concise.
- **Problem 3: Dead Signals.** Signals like `llm_confidence` (asking the LLM "how confident are you?") proved useless, as models consistently hallucinated 90%+ confidence.

### The New Way: Two-Phase Sigmoid
We now separate **Retrieval** (finding the data) from **Generation** (using the data), calibrate each signal individually using sigmoid functions, and fuse them geometrically.

$$ f(x) = \frac{1}{1 + e^{-k(x - x_0)}} $$

Where $x_0$ is the **midpoint** (what we consider "adequate") and $k$ is the **steepness** (sensitivity).

---

## Phase 1: Retrieval Confidence
*Did we find relevant documents?*

This phase analyzes the raw search results before the LLM even sees them.

### 1. Score Quality (`RRF_MIDPOINT`)
- **Metric:** Median RRF score of the top 5 results.
- **Why:** We use the median (not mean) to be robust against outliers. We use RRF scores (not cosine similarity) because they combine dense and sparse rankings.
- **Tuning:** `RRF_MIDPOINT` is set to `0.012`. 
  - If RRF scores > 0.012, this signal approaches 1.0.
  - If RRF scores < 0.012, it drops rapidly.

### 2. Score Separation (`SEPARATION_MIDPOINT`)
- **Metric:** Ratio of the Top Score to the 5th Score ($Score_{top} / Score_{5th}$).
- **Why:** A high ratio (> 1.5) means the search engine found a "clear winner" distinctive from the rest. Flat scores suggest ambiguity.
- **Tuning:** `SEPARATION_MIDPOINT` = 1.5.

### 3. Result Coverage
- **Metric:** $Actual Results / Expected Results$.
- **Why:** If we asked for 10 verses but only found 2, confidence should drop.

**Phase 1 Composition:**
$$ Retrieval = 0.60 \times Quality + 0.25 \times Separation + 0.15 \times Coverage $$

---

## Phase 2: Answer Quality
*Is the generated answer well-grounded?*

This phase analyzes the generated text and citations.

### 1. Citation Density (`EXPECTED_DENSITY`)
- **Metric:** Citations per paragraph vs. Expected Density.
- **Why:** A "Search" query needs fewer citations (~2/para) than a "Compare" query (~4/para).
- **Tuning:** Defined in `EXPECTED_DENSITY` map (e.g., Search=2.0, Ask=3.0, Compare=4.0).

### 2. Top-K Citation Rate (`TOP_K_MIDPOINT`)
- **Metric:** Percentage of citations that come from the top-10 search results.
- **Why:** We want the LLM to use the *best* retrieved results, not obscure ones buried at rank 50.
- **Tuning:** `TOP_K_MIDPOINT` = 0.5 (We expect at least 50% of citations to be from the top 10).

### 3. Answer Substance (`MIN_WORDS`)
- **Metric:** Word count vs. Minimum Threshold.
- **Why:** Prevents high scores for one-sentence non-answers.
- **Tuning:** `MIN_WORDS` (Search=50, Ask=100, Compare=200).

**Phase 2 Composition:**
$$ Answer = 0.50 \times Density + 0.35 \times TopK + 0.15 \times Substance $$

---

## Final Fusion: The Hybrid Blend

We use a **Geometric-Arithmetic Hybrid** to combine Phase 1 and Phase 2.

### The GIGO Principle (Garbage In, Garbage Out)
If Retrieval (Phase 1) is bad, the Answer (Phase 2) *cannot* be trusted, even if it looks perfect. A simple arithmetic mean would allow a hallucinated answer to score 50% just by being long and having fake citations.

$$ Geometric = Retrieval^{0.6} \times Answer^{0.4} $$

The geometric mean forces the score to 0 if *either* component is 0. We weight retrieval higher (0.6) because it is foundational.

### The Final Calculation
$$ Raw = 0.6 \times Geometric + 0.4 \times Arithmetic $$
$$ Final = Sigmoid(Raw, Midpoint=0.45, Steepness=6.0) $$

This final sigmoid stretches the raw scores (which cluster around 0.3-0.7) into the full user-facing range (0.15-0.95).

---

## Removed Signals

### 1. `llm_confidence`
- **What it was:** Asking the LLM "On a scale of 0-1, how confident are you?"
- **Why removed:** **Dead Signal.** RLHF-tuned models (GPT-4, Claude 3) are trained to be helpful and confident. They almost always returned 0.9 or 1.0, even when hallucinating. It added noise without signal.

### 2. `citation_coverage`
- **What it was:** Percentage of retrieved verses that were cited in the answer.
- **Why removed:** **Structural Penalty.** If we retrieve 20 relevant verses but the user asks for a "brief summary", the LLM correctly cites only 2-3 verses. The old metric penalized this correct behavior. We replaced it with **Citation Density**, which measures density *per generated paragraph* rather than against the retrieved pool.

---

## Tuning Guide

Modify `backend/src/confidence_scorer.py` to tune these values based on feedback.

| Parameter | Current | Description |
|-----------|---------|-------------|
| `RRF_MIDPOINT` | `0.012` | Lower if scores are consistently too low. Higher if "noise" results get high confidence. |
| `SEPARATION_MIDPOINT` | `1.5` | Lower if the system is too harsh on ambiguous queries. |
| `DENSITY_STEEPNESS` | `2.0` | Higher makes the system stricter about missing citations. |
| `FINAL_MIDPOINT` | `0.45` | The "center" of the final score. Lower this to boost all scores globally. |
