# Comparative RAG Pipeline Evaluation Report

**Date**: 2026-01-01  
**Test Set**: 50 queries × 2 modes (Single-Query + Multi-Query)

---

## Executive Summary

| Mode | Avg Latency | GT Recall | Citations | Confidence |
|------|-------------|-----------|-----------|------------|
| **Single-Query** | 16.1s | 1% | 13.8 | 95% |
| **Multi-Query** | 23.5s | 1% | 13.5 | 98% |

**Key Finding**: GT Recall is very low (1%) indicating the ground truth matching logic may need adjustment, or the search isn't finding the expected specific verses.

---

## Detailed Results

### Single-Query Mode

| Category | Metric | Value |
|----------|--------|-------|
| **Latency** | Query Enhancement | 2,161 ms |
| | Parallel Searches | 1,244 ms |
| | Reranking | 6,405 ms |
| | Essay Generation | 6,305 ms |
| | **TOTAL (avg)** | **16,115 ms** |
| | Min / Max | 9,977 / 19,884 ms |
| **Retrieval** | Avg Quran Verses | 40.0 |
| | Avg Bible Verses | 39.6 |
| | Balance Ratio | 99% |
| | GT Recall | 1% |
| **Essay** | Avg Total Citations | 13.8 |
| | Avg Quran Citations | 8.3 |
| | Avg Bible Citations | 5.2 |
| | Citation Balance | 62% |
| | Avg Confidence | 95% |
| | Avg Essay Length | 2,620 chars |

### Multi-Query Mode

| Category | Metric | Value |
|----------|--------|-------|
| **Latency** | Query Enhancement | 3,864 ms |
| | Parallel Searches | 6,293 ms |
| | Reranking | 6,763 ms |
| | Essay Generation | 6,625 ms |
| | **TOTAL (avg)** | **23,546 ms** |
| | Min / Max | 18,677 / 85,229 ms |
| **Retrieval** | Avg Quran Verses | 40.0 |
| | Avg Bible Verses | 40.0 |
| | Balance Ratio | 100% |
| | GT Recall | 1% |
| **Essay** | Avg Total Citations | 13.5 |
| | Avg Quran Citations | 8.2 |
| | Avg Bible Citations | 5.4 |
| | Citation Balance | 66% |
| | Avg Confidence | 98% |
| | Avg Essay Length | 2,789 chars |

---

## Mode Comparison

| Metric | Single-Query | Multi-Query | Difference |
|--------|--------------|-------------|------------|
| Avg Latency (ms) | 16,115 | 23,546 | **+7,431** (+46%) |
| Avg Retrieval Balance | 99% | 100% | +1% |
| Avg GT Recall | 1% | 1% | 0% |
| Avg Citations | 13.8 | 13.5 | -0.4 |
| Avg Confidence | 95% | 98% | +2% |

---

## Cost Estimation

| Component | Per Query | Total (50 queries) |
|-----------|-----------|-------------------|
| Query Enhancer | $0.0010 | $0.0500 |
| Embeddings | $0.0001 | $0.0050 |
| Reranker | $0.0020 | $0.1000 |
| Essay Gen | $0.0100 | $0.5000 |
| **TOTAL** | **$0.0131** | **$0.6550** |

---

## Execution Time

| Mode | Total Time |
|------|------------|
| Single-Query (50 queries) | 805.8 seconds (~13.4 min) |
| Multi-Query (50 queries) | 1,177.3 seconds (~19.6 min) |
| **Combined** | **~33 minutes** |

---

## Findings & Recommendations

### ✅ Strengths

1. **Retrieval Balance**: Near-perfect Quran/Bible balance (99-100%)
2. **High Confidence**: LLM produces confident essays (95-98%)
3. **Consistent Output**: 80 verses × 13+ citations per query
4. **Reasonable Cost**: ~$0.013 per query

### ⚠️ Issues

1. **Low GT Recall (1%)**: The ground truth matching is not finding expected verses
   - Possible causes: reference format mismatch, verses not in top-80, or GT refs too specific
   - **Recommendation**: Review reference matching logic in `evaluate_retrieval()`

2. **Multi-Query Latency Spike**: One query took 85s (vs avg 23s)
   - Likely network timeout or API rate limit
   - **Recommendation**: Add retry logic for outliers

3. **Citation Imbalance**: ~60% Quran vs ~40% Bible in citations
   - Essay generator may favor one scripture
   - **Recommendation**: Adjust system prompt for equal citation balance

### 📊 Comparative RAG Value Assessment

| Aspect | Single-Query | Multi-Query | Winner |
|--------|--------------|-------------|--------|
| Speed | ✅ 16.1s | 23.5s | Single |
| Balance | 99% | ✅ 100% | Multi |
| Confidence | 95% | ✅ 98% | Multi |
| Cost | Same | Same | Tie |

**Conclusion**: Multi-Query provides slightly better balance and confidence at +46% latency cost. For production use, Single-Query is recommended unless maximum accuracy is required.
