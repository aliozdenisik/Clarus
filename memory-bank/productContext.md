# Product Context

## Why This Project Exists

Traditional keyword-based search for religious texts fails to capture:

- Semantic meaning and context
- Thematic relationships between verses
- Natural language queries in Turkish

This project solves these problems by combining state-of-the-art RAG techniques.

## Problems It Solves

1. **Poor recall**: Keyword search misses semantically related verses
2. **Context fragmentation**: Single-verse results lose narrative context
3. **Language barriers**: Turkish queries need specialized handling
4. **Ranking accuracy**: Traditional systems can't prioritize the most relevant results

## How It Should Work

```
User Query → LLM Enhancement → Multi-Query Generation → Parallel Search → RRF Fusion → Reranking → Results
```

### User Flow

1. User enters natural language query (e.g., "Kur'an'da sabır kavramı")
2. LLM enhances query with synonyms and related concepts
3. System generates 3-5 query variations for different perspectives
4. Parallel search on both single-verse and semantic chunk collections
5. Results merged via Reciprocal Rank Fusion (RRF)
6. Cross-encoder reranker provides final ordering
7. User receives top-k most relevant results with references

## User Experience Goals

- **Intuitive CLI**: Simple commands like `search`, `search-bible`
- **Fast responses**: Semantic caching for repeated queries
- **Rich context**: Semantic chunks provide thematic groupings
- **Transparency**: Verbose mode shows pipeline stages
- **Flexibility**: Control over result count, translation, search mode

## Target Users

- **Researchers**: Need accurate verse retrieval for scholarly work
- **Students**: Learning religious texts, need contextual results
- **Developers**: Using the API for building applications
