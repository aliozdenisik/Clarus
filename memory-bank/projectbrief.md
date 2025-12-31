# Sacred Texts Ultimate RAG Search - Project Brief

## Project Overview

A maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts, specifically **Quran (Turkish)** and **Bible (Turkish/English)**.

## Core Requirements

1. **High-accuracy semantic search** for religious texts
2. **Hybrid search** combining semantic embeddings with BM25 keyword matching
3. **Turkish language optimization** with lemmatization support
4. **Multi-source support**: Quran and Bible (multiple translations)
5. **CLI interface** for easy interaction

## Goals

- Achieve **84%+ hit rate** for Quran searches
- Achieve **90%+ keyword matching** in enhanced mode
- Provide contextually relevant results with **0.99+ rerank scores**
- Support both single-verse and semantic chunk retrieval

## Success Criteria

- Users can find relevant verses using natural language queries
- System handles complex theological queries (e.g., "şefaat kavramı", "miras hukuku")
- Cross-references and thematically grouped results are returned
- Low latency with semantic caching

## Scope

- **In Scope**: Quran (Turkish), Bible (Turkish - turhadi, English - KJVA)
- **Out of Scope**: Other religious texts, real-time translation

## Key Stakeholders

- Religious researchers
- Theological students
- General users seeking scriptural references
