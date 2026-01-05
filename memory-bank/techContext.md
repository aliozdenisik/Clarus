# Technical Context

## Technologies Used

| Category | Technology | Details |
|----------|------------|---------|
| **Vector DB** | Qdrant | Local Docker instance, port 6333 |
| **Dense Embeddings** | OpenAI text-embedding-3-large | 3072 dimensions, via OpenRouter |
| **Sparse Embeddings** | Qdrant BM25 | FastEmbed integration |
| **LLM (Enhancement)** | Gemini 2.5 Flash Lite | Query expansion |
| **LLM (Answers)** | Gemini 2.5 Flash | Answer generation |
| **Reranker** | Qwen3-Reranker-8B | Via SiliconFlow API |
| **Language** | Python 3.12 | Ubuntu native (3.13 also compatible) |
| **CLI** | argparse + Rich | Beautiful terminal output |
| **OS** | Ubuntu Linux | Migrated from Windows (2026-01-05) |

## Development Setup

### Prerequisites

```bash
# Start Qdrant (with persistent storage)
docker run -d --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables (.env)

```env
OPENROUTER_API_KEY=your-openrouter-key
SILICONFLOW_API_KEY=your-siliconflow-key
```

### First-Time Setup

```bash
python main.py setup  # Indexes Quran, Bible, and semantic chunks
```

## Technical Constraints

1. **Qdrant Local Only**: No cloud deployment yet
2. **API Rate Limits**: SiliconFlow reranker has usage limits
3. **Embedding Costs**: OpenAI embeddings incur per-token costs
4. **Memory**: Large models (torch, transformers) require significant RAM
5. **Cache Size**: Embedding cache can grow large (cache/embeddings/cache.db)

## Dependencies

### Core

- `qdrant-client>=1.7.0` - Vector database client
- `fastembed>=0.2.0` - BM25 sparse embeddings
- `sentence-transformers>=2.7.0` - Transformer models
- `torch>=2.0.0` - PyTorch backend
- `rich>=13.0.0` - Terminal formatting

### Data Processing

- `pandas>=2.0.0` - Data manipulation
- `diskcache>=5.6.0` - Embedding persistence
- `tenacity>=8.2.0` - Retry logic

### Turkish NLP

- `zeyrek>=0.1.0` - Turkish lemmatization for BM25

## Tool Usage Patterns

### CLI Commands (main.py)

```bash
# Indexing
python main.py index                    # Quran
python main.py index-bible              # Bible
python main.py build-semantic-chunks    # Quran chunks
python main.py build-bible-semantic-chunks  # Bible chunks
python main.py setup                    # All of the above

# Searching
python main.py search "query"           # Quran
python main.py search-bible "query"     # Bible
python main.py search-semantic "query"  # Quran semantci chunks

# Q&A
python main.py ask "question"           # Quran Q&A
python main.py ask-bible "question"     # Bible Q&A
python main.py compare "topic"          # Comparative analysis

# Utilities
python main.py info                     # Collection info
python main.py cache-info               # Cache stats
python main.py cache-clear              # Clear cache
```

### Python API

```python
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

# Single scripture
rag = UltimateRAG()
results = rag.search_quran("sabır")
answer = rag.ask_quran("Namaz nedir?")

# Comparative
comp = ComparativeRAG()
essay = comp.compare("Yaratılış")
```

## Directory Structure

```
qdrant/
├── main.py                 # CLI entrypoint
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in git)
├── data/                   # Source data (JSON)
├── src/                    # Python modules
├── tests/                  # Test scripts
├── cache/                  # Embedding cache
├── qdrant_data/            # Qdrant Docker volume
└── memory-bank/            # This documentation
```
