<div align="center">

# Clarus

**Maximum-accuracy RAG search engine for sacred texts**

Comparative theological analysis across Quran and Bible with 5-agent LLM synthesis

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Backend CI](https://github.com/aliozdenisik/Clarus/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/aliozdenisik/Clarus/actions/workflows/backend-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC382D.svg?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)

[Getting Started](#-getting-started) · [Features](#-features) · [Usage](#-usage) · [API Reference](#-api-reference) · [Architecture](#-architecture)

</div>

---

## Overview

Clarus is a production-ready Retrieval-Augmented Generation (RAG) system designed for **maximum retrieval accuracy** on religious texts. It combines state-of-the-art hybrid search (dense + sparse vectors) with multi-agent LLM synthesis to provide scholarly-quality comparative analysis across the Quran and Bible.

### Why Clarus?

- **Hybrid Search** — Combines semantic embeddings with BM25 keyword matching via Reciprocal Rank Fusion (RRF)
- **Multi-Agent Synthesis** — 5 specialized agents provide perspectives from Quran, Old Testament, New Testament, and Apocrypha
- **High Accuracy** — 80%+ recall on Quran, 100% recall on Bible with 96% confidence scores
- **Production Ready** — FastAPI backend with JWT auth, rate limiting, and semantic caching

---

## Architecture

```
Query → ENHANCE → MULTI-QUERY → PARALLEL SEARCH → RRF FUSION → MULTI-AGENT ANSWER
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
    ┌────┴────┐    ┌─────────┐    ┌────┴────┐    ┌─────────────────┐
    │  QURAN  │    │ BIBLE   │    │ BIBLE   │    │     BIBLE       │
    │   (TR)  │    │   OT    │    │   NT    │    │   APOCRYPHA     │
    │  6,236  │    │ 23,145  │    │  7,957  │    │     5,717       │
    └─────────┘    └─────────┘    └─────────┘    └─────────────────┘
```

| Stage | Description | Technology |
|-------|-------------|------------|
| **Query Enhancement** | LLM expands and clarifies user query | Grok 4.1 Fast |
| **Multi-Query Generation** | Creates 3-5 query variants for better recall | Grok 4.1 Fast |
| **Parallel Search** | Hybrid search across 4 collections | OpenAI text-embedding-3-large + BM25 |
| **RRF Fusion** | Combines results with k=60 | Reciprocal Rank Fusion |
| **Multi-Agent Answer** | 5 specialized agents synthesize response | Gemini 2.5 Flash |

---

## Features

### Core Capabilities

- **Hybrid Search** — Dense vectors (OpenAI text-embedding-3-large, 3072 dim) + Sparse vectors (BM25 via FastEmbed)
- **Semantic Chunking** — Context-aware text segmentation preserving verse boundaries
- **Query Enhancement** — LLM-powered query expansion for improved recall
- **Multi-Query RAG** — Generates multiple query perspectives to maximize coverage

### Multi-Agent System

| Agent | Collection | Role |
|-------|------------|------|
| QuranAgent | `quran_tr` | Quran perspective and commentary |
| OldTestamentAgent | `bible_ot` | Old Testament (Torah, Prophets, Writings) |
| NewTestamentAgent | `bible_nt` | New Testament (Gospels, Epistles) |
| ApocryphaAgent | `bible_apocrypha` | Deuterocanonical texts |
| SummaryAgent | — | Synthesizes all perspectives into cohesive essay |

### Production Features

- **Semantic Cache** — 95% similarity threshold, 7-day TTL, reduces API costs by 60-80%
- **JWT Authentication** — Secure API access with Google OAuth support
- **Rate Limiting** — 50 queries/day per user (configurable)
- **SSE Streaming** — Token-by-token response streaming

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- OpenRouter API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/clarus.git
cd clarus

# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd backend
uv sync
```

### Configuration

Create a `.env` file in the `backend/` directory:

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key

# Optional (for API usage)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
JWT_SECRET_KEY=your-secret-key
```

### Quick Start

```bash
# Start Qdrant vector database
docker run -p 6333:6333 qdrant/qdrant

# Index all collections (run once, ~2 minutes)
python scripts/setup_all_collections.py

# Verify installation
python main.py info
```

---

## Usage

### CLI Commands

#### Search

```bash
# Quran search (Turkish)
python main.py search "sabir ve namaz"

# Bible search (English KJVA)
python main.py search-bible "love your neighbor"

# Semantic chunk search
python main.py search-semantic "creation of Adam"
```

#### Question & Answer

```bash
# Ask Quran
python main.py ask "What is patience in Islam?"

# Ask Bible
python main.py ask-bible "What is love according to the Bible?"
```

#### Comparative Analysis

```bash
# Single essay mode (faster)
python main.py compare "The concept of forgiveness"

# Multi-agent mode (5-paragraph detailed analysis)
python main.py compare --multi-agent "The creation story"
```

#### System Commands

```bash
python main.py info          # Collection statistics
python main.py cache-info    # Cache statistics
python main.py cache-clear   # Clear semantic cache
```

### Python API

```python
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

# Initialize RAG pipeline
rag = UltimateRAG(enable_semantic_chunks=True)

# Search
results = rag.search_quran("intercession concept", top_k=5)
results = rag.search_bible("forgiveness", translation="kjva")

# Question & Answer
answer = rag.ask_quran("How to perform prayer?")
answer = rag.ask_bible("How to love your neighbor?")

# Comparative Analysis
comp = ComparativeRAG()

# Single essay
essay = comp.compare("Creation and the origin of humanity")
print(essay['essay'])

# Multi-agent analysis
result = comp.compare_multi_agent("Creation and the origin of humanity")
print(result['paragraphs'])
```

---

## API Reference

### Starting the Server

```bash
# Start infrastructure
docker compose up -d  # PostgreSQL + Qdrant

# Start FastAPI server
uvicorn app.main:app --reload
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | JWT authentication |
| `/api/search/quran` | POST | Quran search |
| `/api/search/bible` | POST | Bible search |
| `/api/stream/search` | GET | SSE streaming search |
| `/api/compare/` | POST | Multi-agent comparison |
| `/docs` | GET | OpenAPI documentation |

---

## Collections

| Collection | Verses | Language | Source |
|------------|--------|----------|--------|
| `quran_tr` | 6,236 | Turkish | Quran |
| `bible_ot` | 23,145 | English | Old Testament (KJVA) |
| `bible_nt` | 7,957 | English | New Testament (KJVA) |
| `bible_apocrypha` | 5,717 | English | Apocrypha (KJVA) |

**Total:** 43,055 indexed verses

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Dense Encoder** | OpenAI text-embedding-3-large (3072 dim) |
| **Sparse Encoder** | Qdrant/BM25 via FastEmbed |
| **Vector Database** | Qdrant (HNSW + Scalar Quantization) |
| **LLM (Enhancement)** | Grok 4.1 Fast via OpenRouter |
| **LLM (Generation)** | Gemini 2.5 Flash via OpenRouter |
| **Fusion Algorithm** | Reciprocal Rank Fusion (k=60) |
| **Semantic Cache** | Custom (θ=0.95, 7-day TTL) |
| **Backend** | FastAPI + SQLAlchemy (async) |
| **Authentication** | JWT + Google OAuth |

---

## Performance

| Metric | Value |
|--------|-------|
| Overall F1 Score | **57%+** |
| Quran Recall | **80%+** |
| Bible Recall | **100%** |
| Confidence Score | **96%** |
| Multi-Agent Latency | **~40s** |
| Cost per Query | **~$0.013** (with cache) |

---

## Project Structure

```
clarus/
├── backend/
│   ├── main.py                 # CLI entrypoint
│   ├── requirements.txt
│   ├── app/                    # FastAPI application
│   │   ├── main.py             # ASGI entrypoint
│   │   ├── config.py           # Settings
│   │   ├── auth/               # JWT + OAuth
│   │   └── api/                # Route handlers
│   ├── src/                    # RAG pipeline modules
│   │   ├── ultimate_rag.py     # Main RAG pipeline
│   │   ├── comparative_rag.py  # Comparative analysis
│   │   ├── multi_agent_answer_generator.py
│   │   ├── search.py           # Hybrid search
│   │   ├── embeddings.py       # Dense + sparse encoders
│   │   └── ...
│   ├── data/
│   │   ├── quran_tr.json
│   │   └── bible_kjva.json
│   └── tests/
├── frontend/                   # Next.js 15 (optional)
├── docker-compose.yml
└── memory-bank/                # Project documentation
```

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a PR.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**[Back to Top](#clarus)**

</div>
