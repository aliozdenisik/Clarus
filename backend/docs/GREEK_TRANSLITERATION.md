# Greek Transliteration Normalization

## Overview

This document describes the Greek transliteration normalization system used in Clarus for matching user ASCII queries (e.g., `zoe`, `eirene`) against Strong's Concordance scholarly transliterations (e.g., `zōḗ`, `eirḗnē`).

## Problem Statement

Strong's Concordance uses scholarly Greek transliteration with macrons and accents:
- `zōḗ` (G2222 - life)
- `eirḗnē` (G1515 - peace)
- `agápē` (G26 - love)
- `lógos` (G3056 - word)

Users type simple ASCII:
- `zoe`
- `eirene`
- `agape`
- `logos`

**Challenge**: Match ASCII input against scholarly transliterations reliably.

### The Macron Problem

Greek transliterations use macrons to distinguish vowel length:
- `ō` (omega - ω) vs `o` (omicron - ο)
- `ē` (eta - η) vs `e` (epsilon - ε)

Without normalization:
- `reverse_transliterate_greek('zoe')` → `ζοε` (WRONG: omicron + epsilon)
- Should be: `ζωή` (omega + eta)

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cache Build (Startup)                        │
├─────────────────────────────────────────────────────────────────┤
│  bm_strongs.transliteration (for G* entries)                    │
│         │                                                       │
│         ▼                                                       │
│  normalize_greek_transliteration_for_lookup()                   │
│         │                                                       │
│         ▼                                                       │
│  _transliteration_map["zoe"] = ["G2222"]                        │
│  _transliteration_map["eirene"] = ["G1515"]                     │
│  _transliteration_map["agape"] = ["G26"]                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Query Time (Search)                          │
├─────────────────────────────────────────────────────────────────┤
│  User input: "zoe"                                              │
│         │                                                       │
│         ▼                                                       │
│  normalize_user_greek_query("zoe") → "zoe"                      │
│         │                                                       │
│         ▼                                                       │
│  _transliteration_map["zoe"] → ["G2222"]                        │
│         │                                                       │
│         ▼                                                       │
│  bm_strongs[G2222].original_word → "ζωή"                        │
│         │                                                       │
│         ▼                                                       │
│  _search_by_lemma("ζωή") → 135 occurrences                      │
└─────────────────────────────────────────────────────────────────┘
```

## Key Insight: Greek vs Hebrew Data Model

| Language | bm_words column | Search method |
|----------|-----------------|---------------|
| Hebrew | `strong_number` ✅ | `_search_by_strong()` |
| Greek | `lemma` only (no strong_number) | `_search_by_lemma()` |

This is why the Greek lookup flow returns the **lemma** from `bm_strongs.original_word`, not the Strong's number.

## Normalization Rules

The `normalize_greek_transliteration_for_lookup()` function applies:

### Step 1: Unicode NFD Decomposition
Separates base characters from combining diacritics:
- `ō` → `o` + combining macron
- `ḗ` → `e` + combining macron + combining acute

### Step 2: Strip Combining Characters
Removes all Unicode category `Mn` (Mark, nonspacing):
- Removes macrons, accents, breathing marks
- `zōḗ` → `zoe`
- `eirḗnē` → `eirene`

### Step 3: Lowercase
Standard case normalization.

## Implementation Files

| File | Function | Purpose |
|------|----------|---------|
| `greek_normalizer.py` | `normalize_greek_transliteration_for_lookup()` | Strip macrons/accents via NFD |
| `greek_normalizer.py` | `normalize_user_greek_query()` | Normalize user input |
| `bible_morphology.py` | `_load_strongs_cache()` | Build normalized cache for G* entries |
| `bible_morphology.py` | `_find_root_latin()` Step L5a | Lookup normalized Greek transliteration |

## Code Example

```python
from src.greek_normalizer import (
    normalize_greek_transliteration_for_lookup,
    normalize_user_greek_query,
)

# Cache build: Strong's transliteration → normalized key
strong_translit = "zōḗ"  # From bm_strongs
normalized = normalize_greek_transliteration_for_lookup(strong_translit)
# normalized = "zoe"
# Cache: _transliteration_map["zoe"] = ["G2222"]

# Query time: User input → same normalization
user_input = "zoe"
query_normalized = normalize_user_greek_query(user_input)
# query_normalized = "zoe"
# Lookup: _transliteration_map["zoe"] → ["G2222"]
# Get lemma: bm_strongs[G2222].original_word → "ζωή"
# Search: _search_by_lemma("ζωή") → 135 results
```

## Test Results

| Query | Strong's | Lemma | Occurrences |
|-------|----------|-------|-------------|
| `zoe` | G2222 | ζωή | 135 |
| `eirene` | G1515 | εἰρήνη | 91 |
| `agape` | G26 | ἀγάπη | 116 |
| `logos` | G3056 | λόγος | 330 |
| `theos` | G2316 | θεός | 1307 |
| `christos` | G5547 | χριστός | 528 |
| `pistis` | G4102 | πίστις | 242 |
| `pneuma` | G4151 | πνεῦμα | 379 |

All Greek Latin transliteration tests pass with `root_source=greek_transliteration_normalized`.

## Industry Standards Referenced

1. **Unicode NFD Normalization** - Standard approach for stripping diacritics
2. **Strong's Concordance** - Source of scholarly Greek transliterations
3. **SBL Greek Transliteration** - Academic standard for Biblical Greek

## Comparison with Hebrew

| Aspect | Greek | Hebrew |
|--------|-------|--------|
| Diacritics | Macrons (ō, ē) | Circumflex, cedilla (ô, ç) |
| Word markers | None | Aleph (ʼ), Ayin (ʻ) |
| Consonant variants | None | Het (ch/kh/h), Qoph (q/k) |
| Search target | Lemma | Strong's number |
| Normalization complexity | Simple (NFD strip) | Complex (multiple rules) |

## Related Documentation

- [HEBREW_TRANSLITERATION.md](HEBREW_TRANSLITERATION.md) - Hebrew transliteration system
- [WORD_SEARCH_TESTING.md](WORD_SEARCH_TESTING.md) - Test case documentation
