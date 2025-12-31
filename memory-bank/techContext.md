# Tech Context

## Technologies Used

### Core Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Vector DB | Qdrant | ≥1.7.0 |
| Dense Embeddings | OpenAI `text-embedding-3-large` | 3072 dim |
| Sparse Embeddings | FastEmbed `Qdrant/bm25` | Latest |
| Reranker | Qwen3-Reranker-0.6B-seq-cls | HuggingFace |
| LLM | Gemini 2.5 Flash Lite | via OpenRouter |
| Framework | Python | 3.10+ |

### Key Libraries

```
qdrant-client>=1.7.0      # Vector database client
fastembed>=0.2.0          # Fast embedding library
sentence-transformers>=2.7.0  # Transformer models
transformers>=4.51.0      # HuggingFace transformers
torch>=2.0.0              # PyTorch backend
rich>=13.0.0              # CLI formatting
diskcache>=5.6.0          # Embedding cache
tenacity>=8.2.0           # Retry logic
zeyrek>=0.1.0             # Turkish lemmatization
python-dotenv>=1.0.0      # Environment variables
```

## Development Setup

### Prerequisites

1. Docker (for Qdrant)
2. Python 3.10+
3. OpenRouter API key

### Quick Start

```bash
# 1. Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
echo "OPENROUTER_API_KEY=your-key" > .env

# 4. Index data
python main.py index
python main.py build-semantic-chunks --threshold 25
python main.py index-bible --translation turhadi
```

## Technical Constraints

### API Rate Limits

- OpenRouter: 20 requests/minute (configurable)
- OpenAI Embeddings: Rate limited via tenacity

### Memory Considerations

- Reranker model loads ~600MB
- Embedding models cached to disk
- Qdrant runs in Docker with default memory

### Performance Tuning

- HNSW: `m=16`, `ef_construct=200`
- Scalar Quantization: `int8`
- RRF k-parameter: `60`
- Rerank pool size: `50`

## Dependencies

### External Services

| Service | Purpose | Required |
|---------|---------|----------|
| Qdrant | Vector storage | Yes |
| OpenRouter | LLM API | Yes (for enhancement) |
| Docker | Qdrant container | Recommended |

### Data Files

```
data/
├── quran_tr.json          # Quran Turkish translation
├── semantic_chunks.json   # Pre-computed semantic chunks
├── bible_turhadi.json     # Bible Turkish
└── bible_kjva.json        # Bible English (KJVA)
```

## Tool Usage Patterns

### CLI Commands

| Command | Purpose |
|---------|---------|
| `search` | Quran search with Ultimate RAG |
| `search-bible` | Bible search |
| `search-semantic` | Direct semantic chunk search |
| `index` | Index Quran data |
| `index-bible` | Index Bible data |
| `build-semantic-chunks` | Create semantic chunks |
| `info` | Collection statistics |
| `cache-info` / `cache-clear` | Cache management |
| `build-graph` | GraphRAG construction |

### Environment Variables

```env
OPENROUTER_API_KEY=...    # Required for LLM
QDRANT_URL=http://localhost:6333  # Optional
```
