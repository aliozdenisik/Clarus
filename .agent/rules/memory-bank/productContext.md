# Product Context

## Why This Project Exists

Traditional keyword-based search for religious texts fails to capture:

- Semantic meaning and context
- Thematic relationships between verses
- Natural language queries in Turkish
- **Cross-scriptural theological nuances** (Quran vs Bible)

This project solves these problems by combining state-of-the-art RAG techniques.

## Problems It Solves

1. **Poor recall**: Keyword search misses semantically related verses
2. **Context fragmentation**: Single-verse results lose narrative context
3. **Language barriers**: Turkish queries need specialized handling
4. **Ranking accuracy**: Traditional systems can't prioritize the most relevant results
5. **Synthesis**: Users need to see how different traditions address the same topic

## How It Should Work

### Standard Search (Ultimate RAG)

```
User Query → LLM Enhancement → Multi-Query Generation → Parallel Search → RRF Fusion → Reranking → Results
```

### Direct Answer Generation (New)

```
User Query → Search Results (Top 10) → LLM Synthesis (Flash Lite) → Direct Answer + Citations
```

### Comparative Analysis

```
User Query → Parallel Enhancement (Quran/Bible) → 4-Way Search → Independent Reranking → Essay Generation
```

### User Flow

1. **Search**: User enters query -> System returns ranked verses + semantic chunks.
2. **Ask**: User asks a specific question -> System gives a direct, synthesized answer.
   - Example: "Kur'an'a göre miras paylaşımı nasıldır?"
   - Output: 1-2 paragraph answer with specific [Sure:Ayet] citations.
3. **Compare**: User asks theological question -> System generates cited comparative essay.
   - Example: "Kur'an ve İncil'de sabır kavramı"
   - Output: 3-4 paragraph essay with [Sure:Ayet] and [Book Ch:V] citations.

## User Experience Goals

- **Intuitive CLI**: Simple commands like `search`, `ask`, `compare`
- **Fast responses**: Semantic caching and Flash Lite for answers
- **Rich context**: Semantic chunks provide thematic groupings
- **Transparency**: Verbose mode shows pipeline stages
- **Flexibility**: Control over result count, translation, search mode
- **Scholarly Depth**: Essays provide balanced, well-cited theological synthesis

## Target Users

- **Researchers**: Need accurate verse retrieval for scholarly work
- **Students**: Learning religious texts, need contextual results
- **Developers**: Using the API for building applications
- **Theologians**: Analyzing comparative concepts across traditions
