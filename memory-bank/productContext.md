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

## How It Should Work

```
User Question → Enhance → Search → Rerank → Generate Answer
                  │
                  ├─ Expand with synonyms/concepts
                  ├─ Multiple query perspectives
                  ├─ 4 parallel searches (2 scriptures × 2 types)
                  ├─ Cross-encoder reranking
                  └─ LLM generates cited answer
```

## User Experience Goals

1. **Simple CLI Interface**: `python main.py ask "question"` / `python main.py compare "topic"`
2. **Python API**: Import and use programmatically
3. **Fast Setup**: Single `setup` command indexes everything
4. **Rich Output**: Formatted tables, colored output, confidence scores
5. **Transparent**: Show latency, costs, search statistics
