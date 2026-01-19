---
trigger: always_on
---

# Qur’an & Bible RAG System Rules

## 1. Priority Order
The RAG system must always operate according to the following priority order:

1. **Source Text Accuracy (Qur’an & Bible)**
2. **Retrieval and Grounding Accuracy**
3. **Speed**
4. **Cost**

Speed or cost must never override fidelity to the original religious texts.

---

## 2. Canonical Source Integrity
- The exact source (Surah/Ayah or Book/Chapter/Verse) must be preserved.
- Texts must never be altered, paraphrased, or normalized unless explicitly requested.

---

## 3. Translation Fidelity
- When translations are used:
  - Meaning-preserving fidelity is mandatory.
- Original language (Arabic, Hebrew, Greek) takes precedence when available.

---

## 4. Grounded and Faithful Generation
- All generated responses must be **strictly grounded** in retrieved verses.
- The system must not introduce theological interpretations, opinions, or commentary unless explicitly requested.
- If multiple interpretations exist, the system must present them neutrally and attribute them properly.

---

## 5. Error Minimization and Religious Sensitivity
- Hallucinations, fabricated verses, or incorrect attributions are strictly prohibited.
- Conflicting translations or manuscript traditions must be acknowledged, not resolved by assumption.
- The system must maintain respectful and neutral language at all times.

---

## 6. Uncertainty Handling
- If the requested information cannot be reliably retrieved:
  - The system must clearly state the limitation.
  - No speculative or inferred content may be generated.

---

## 7. Efficiency and Optimization
- Only after textual accuracy and grounding are guaranteed may the system:
  - Optimize retrieval latency,
  - Reduce computation or token usage,
  - Apply indexing or caching strategies.
- Optimization must never compromise textual fidelity.

---

## 8. System Behavior
- The RAG system applies these rules implicitly.
- These rules govern retrieval, generation, ranking, translation, and citation steps.
