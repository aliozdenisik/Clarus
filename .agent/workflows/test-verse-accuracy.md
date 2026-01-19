---
description: AI ayet doğruluğu testi - RAG sisteminin ürettiği cevaplardaki ayet referanslarının doğruluğunu ve halüsinasyon oranını ölçer
---

This workflow tests the verse fidelity and hallucination rate of the Sacred Texts RAG system.

---

## Prerequisites

1. Ensure the qdrant database is running:
```bash
docker ps | grep qdrant
```
Start it if it's not running:
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

2. Ensure collections are indexed:
```bash
cd /home/freyja/qdrant && python main.py info
```

---

## Step 1: Define Test Scope

The test dataset is located in `/home/freyja/qdrant/tests/test_data.json`. It contains 50 ground-truth queries.

**Options:**

- **Quick Test (5 queries):** IDs: 5, 36, 41, 46, 49
- **Mid-Test (15 queries):** Selection by category
- **Full Test (50 queries):** Entire dataset

---

## Step 2: Faithfulness Test

This test measures how closely RAG responses adhere to the source verses.

// turbo
```bash
cd /home/freyja/qdrant && python -c "
from tests.test_comparative_rag_evaluation import run_evaluation
# 5 queries for quick test
results = run_evaluation(sample_ids=[5, 36, 41, 46, 49], test_multi_query=False)
"
```

**Metrics to be Evaluated:**
- `gt_quran_recall`: Ground-truth rate of Quranic verses
- `gt_bible_recall`: Ground-truth rate of Bible verses
- `citation_balance`: Quran/Bible citation balance

---

## Step 3: Hallucination Detection

Identify fabricated or misattributed verses.

// turbo
```bash
cd /home/freyja/qdrant && python -c "
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

# Test query
test_query = 'Verses that say God knows everything'

# RAG search
rag = ComparativeRAG(verbose=True)
result = rag.compare(test_query)

print('=== HALLUCINATION CHECK ===')
print(f'Total Citations: {len(result.all_references)}')
print(f'Quran Citations: {result.quran_references}')
print(f'Bible Citations: {result.bible_references}')
print(f'Trust Score: {result.confidence:.0%}')
print()
print('=== ESSAY (FOR REVIEW) ===')
print(result.essay[:500])
"
```

**Manual Checklist:**
- [ ] Do the referenced verses actually exist?
- [ ] Are the verse contents accurately conveyed?
- [ ] Are there any fabricated/non-existent Surah/Book names?
- [ ] Are the verse numbers within the valid range?

---

## Step 4: Source Verification Test

Verifying a specific verse reference from the source:

// turbo
```bash
cd /home/freyja/qdrant && python -c "
from src.search import QuranSearcher, BibleSearcher

# Quran verification example
quran = QuranSearcher()
results = quran.search('Enam 59', limit=3)
print('=== QURAN VERIFICATION ===')
for r in results:
print(f'{r.surah_name} {r.surah_id}:{r.verse_id}')
print(f' {r.translation[:100]}...')
print()

# Bible verification example
bible = BibleSearcher(translation='kjva')
results = bible.search('Matthew 10:30', limit=3)
print('=== BIBLE VERIFICATION ===')
for r in results:
print(f'{r.book_name} {r.chapter}:{r.verse}')
print(f' {r.text[:100]}...')
"
```

---

## Step 5: Full Evaluation Report

Comprehensive evaluation for all 50 queries:

```bash
cd /home/freyja/qdrant && python -m pytest tests/test_comparative_rag_evaluation.py -v --tb=short
```

**Or run directly:**

```bash
cd /home/freyja/qdrant && python tests/test_comparative_rag_evaluation.py
```

---

## Step 6: Interpret Results

### Success Criteria

| Metric | Target | Critical Threshold |

|--------|-------|-------------|
| GT Recall (Quran) | > 70% | < 50% |
| GT Recall (Bible) | > 70% | < 50% |
| Hallucination Rate | < 5% | > 10% |
| Attribution Balance | > 60% | < 40% |
| Average Confidence | > 75% | < 60% |

### Result Evaluation

- **PASS (Successful):** All metrics are above target values
- **WARNING (Warning):** Some metrics are below target but above the critical threshold
- **FAIL (Failed):** Any metric is below the critical threshold

---

## Troubleshooting

### Low Recall
1. Check the embedding model
2. Set the semantic chunking threshold
3. Enable multi-query mode

### High Hallucination
1. Verify that Reranker is working correctly
2. Review the answer generator prompt
3. Lower the temperature value

### Unbalanced Citations
1. Check that both collections are indexed correctly
2. Balance the search limits
3. Set the RRF fusion parameters

---

## Related Files

- Test dataset: `tests/test_data.json`
- Evaluation script: `tests/test_comparative_rag_evaluation.py`
- RAG rules: `.agent/rules/rag-rules.md`
- Main application: `main.py`