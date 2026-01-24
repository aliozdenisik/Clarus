# Product Context

## Why This Project Exists

Traditional keyword search fails for religious texts because:

- **Semantic Complexity**: Religious concepts span multiple verses and contexts
- **Language Barriers**: Quran in Turkish, Bible in English - cross-lingual search needed
- **Thematic Connections**: Related themes scattered across books/chapters
- **Comparative Study**: Scholars need to compare concepts across scriptures

## Problems It Solves

### 1. Finding Relevant Verses

- Users ask conceptual questions ("What does Islam say about patience?")
- System must understand intent, not just keywords
- Must find semantically related verses, not just exact matches

### 2. Cross-Scripture Comparison

- Researchers studying both texts need unified search
- Must balance results between Quran and Bible
- Generate academic-quality comparative analysis

### 3. Accurate Citations

- Answers must cite specific verses
- References must be verifiable (Surah:Verse, Book:Chapter:Verse)
- High confidence in generated content

## How It Works

```
User Question -> Enhance -> Search -> Rerank -> Generate Answer
                   |
                   +-- Expand with synonyms/concepts
                   +-- Multiple query perspectives
                   +-- 4 parallel searches (4 testament collections)
                   +-- RRF fusion + reranking
                   +-- LLM generates cited answer
```

## User Experience Goals

### Web App (General Interface)

1. **Modern UI**: Next.js 15 app with Linear-style dark theme
2. **Interactive**: Real-time search results, spring animations
3. **Structured Analysis**: Visual breakdown of comparative essays (5 paragraphs)
4. **Accessible**: Login/Register flow, responsive design for mobile/desktop

### CLI (Power User Interface)

1. **Simple Commands**: `python main.py ask "question"` / `python main.py compare "topic"`
2. **Rich Output**: Formatted tables, colored output, confidence scores
3. **Fast Setup**: Single `setup` command indexes everything
4. **Transparent**: Show latency, costs, search statistics

### REST API (Programmatic Access)

1. **Standard REST**: JSON request/response with OpenAPI docs
2. **SSE Streaming**: Real-time token streaming for LLM responses
3. **Authentication**: JWT for user tracking and rate limiting
4. **Integrations**: Easy to integrate with other applications

### Python API (Library Usage)

1. **Direct Import**: `from src.ultimate_rag import UltimateRAG`
2. **Full Control**: Access all pipeline components
3. **Batch Processing**: Suitable for research workflows
