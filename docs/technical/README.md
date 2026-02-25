# Technical Documentation

Academic and technical papers explaining the mathematical foundations, algorithms, and architectural decisions behind Clarus.

These documents are intended for developers, researchers, and anyone interested in understanding **how** and **why** the system works the way it does — not just what it does.

## Papers

### Search & Retrieval

| Document | Description |
|----------|-------------|
| [Hybrid Search and RRF Fusion](hybrid-search-and-rrf-fusion.md) | Mathematical foundations of dense (text-embedding-3-large) + sparse (BM25) vector search and Reciprocal Rank Fusion with k=60 parameter analysis |
| [Confidence Scoring System](confidence-scoring-system.md) | Two-phase sigmoid-calibrated scoring replacing naive weighted averages, based on Platt scaling from machine learning calibration literature |

### Natural Language Processing

| Document | Description |
|----------|-------------|
| [Morphological Analysis Pipeline](morphological-analysis-pipeline.md) | Computational linguistics for Arabic root extraction (1,651 roots), Hebrew/Greek Strong's concordance, Buckwalter transliteration, and cross-language normalization |
| [Semantic Chunking Algorithms](semantic-chunking-algorithms.md) | Embedding-based verse grouping using cosine similarity boundary detection with configurable threshold strategies (fixed, percentile, std-based) |

### System Architecture

| Document | Description |
|----------|-------------|
| [Multi-Agent RAG Architecture](multi-agent-rag-architecture.md) | 5-agent parallel search and synthesis system for comparative theological analysis across Quran and Bible collections |
| [Caching and Resilience Patterns](caching-and-resilience-patterns.md) | Redis caching architecture (semantic cache, rate limiting, token blacklist), circuit breaker state machines, and fail-open resilience design |

## Key Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Embedding Dimensions | 3,072 | OpenAI text-embedding-3-large |
| RRF Constant (k) | 60 | Tuned for this corpus |
| Indexed Vectors | ~123,000 | 13 collections |
| Morphology Database | 77,429 words, 1,651 roots | Quranic Arabic Corpus v0.4 |
| Confidence Score Range | 15%–95% | Sigmoid-calibrated |
| Cache Cost Reduction | 60–80% | Redis semantic cache |
| Supported Languages | 8 | TR, EN, ES, FR, IT, PT, AR, DE |

## Academic References

The following foundational works inform Clarus's design:

- **Cormack, G.V., Clarke, C.L.A., & Buettcher, S.** (2009). *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods.* SIGIR '09.
- **Robertson, S. & Zaragoza, H.** (2009). *The Probabilistic Relevance Framework: BM25 and Beyond.* Foundations and Trends in Information Retrieval.
- **Platt, J.** (1999). *Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods.* Advances in Large Margin Classifiers.
- **Lewis, P. et al.** (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS 2020.
- **Karpukhin, V. et al.** (2020). *Dense Passage Retrieval for Open-Domain Question Answering.* EMNLP 2020.
- **Dukes, K. & Habash, N.** (2010). *Morphological Annotation of Quranic Arabic.* LREC 2010.
- **Nygard, M.** (2007). *Release It! Design and Deploy Production-Ready Software.* Pragmatic Bookshelf.

## Contributing

When adding technical documentation:

- Use academic tone with proper mathematical notation (LaTeX `$$` blocks for GitHub rendering)
- Include code snippets from the actual implementation with file paths and line numbers
- Cite relevant papers and standards
- Keep each document focused on one system or algorithm family
- Update this README when adding new documents

---

**Last Updated:** 2026-02-25
