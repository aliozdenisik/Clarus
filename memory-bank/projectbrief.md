# Clarus

## Project Overview

A maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts (Quran and Bible) with comparative theological analysis capabilities.

## Core Requirements

1. **Multi-Scripture Search**: Query both Quran (Turkish) and Bible (English KJVA) with high accuracy
2. **Semantic Understanding**: Use LLM-enhanced query expansion and semantic chunking
3. **Comparative Analysis**: Generate academic-style comparative essays across scriptures
4. **Answer Generation**: Produce cited answers from retrieved verses
5. **Dual Interface**: Accessible via CLI for power users and Web App for general users

## Project Goals

- **Accuracy**: 84%+ Quran hit rate, 75%+ Bible hit rate
- **Experience**: Fast, responsive Web App with streaming and animations
- **Quality**: High-confidence, well-cited responses with balanced scripture representation
- **Cost Efficiency**: ~$0.013 per query via semantic caching

## Key Features

| Feature | Description |
|---------|-------------|
| Query Enhancement | LLM expands queries with synonyms and related concepts |
| Multi-Query RAG | 3-5 query perspectives for better coverage |
| Parallel Search | Single-verse + Semantic chunk search simultaneously |
| RRF Fusion | Reciprocal Rank Fusion combines results |
| Cross-Encoder Reranking | Qwen3-Reranker-8B for final scoring |
| Answer Generation | Gemini 2.5 Flash generates cited responses |
| Comparative Essays | Academic theological comparisons |

## Source of Truth

This document defines the project scope. All other memory bank files build upon this foundation.
