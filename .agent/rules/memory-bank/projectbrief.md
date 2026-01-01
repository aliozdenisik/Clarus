# Sacred Texts Ultimate RAG Search - Project Brief

## Project Overview

A maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts, specifically **Quran (Turkish)** and **Bible (Turkish/English)**.

## Core Requirements

1. **High-accuracy semantic search** for religious texts
2. **Hybrid search** combining semantic embeddings with BM25 keyword matching
3. **Turkish language optimization** with lemmatization support
4. **Multi-source support**: Quran and Bible (multiple translations)
5. **CLI interface** for easy interaction
6. **Comparative Analysis**: Synthesis of theological concepts across scriptures

## Goals

- Achieve **84%+ hit rate** for Quran searches
- Achieve **90%+ keyword matching** in enhanced mode
- Provide contextually relevant results with **0.99+ rerank scores**
- Support both single-verse and semantic chunk retrieval
- Generate coherent, cited comparative theological essays
- **Provide direct answers** to specific questions with citations

## Success Criteria

- Users can find relevant verses using natural language queries
- System handles complex theological queries (e.g., "şefaat kavramı", "miras hukuku")
- Cross-references and thematically grouped results are returned
- Low latency with semantic caching
- Comparative essays provide accurate, balanced synthesis of Quran and Bible perspectives
- **Direct Q&A** provides synthesized answers for quick information retrieval

## Scope

- **In Scope**: Quran (Turkish), Bible (Turkish - turhadi, English - KJVA), Comparative Analysis, **Bible Semantic Chunks**
- **Out of Scope**: Other religious texts, real-time translation (except query)

## Key Stakeholders

- Religious researchers
- Theological students
- General users seeking scriptural references
