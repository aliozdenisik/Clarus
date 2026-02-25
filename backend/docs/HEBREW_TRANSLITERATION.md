# Hebrew Transliteration Normalization

## Overview

This document describes the Hebrew transliteration normalization system used in Clarus for matching user ASCII queries (e.g., `elohim`) against Strong's Concordance scholarly transliterations (e.g., `ʼĕlôhîym`).

## Problem Statement

Strong's Concordance uses scholarly transliteration with diacritics:
- `ʼĕlôhîym` (H430 - God)
- `chêçêd` (H2617 - lovingkindness)
- `shâmaʻ` (H8085 - hear)

Users type simple ASCII:
- `elohim`
- `chesed`
- `shama`

**Challenge**: Match ASCII input against scholarly transliterations reliably.

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cache Build (Startup)                        │
├─────────────────────────────────────────────────────────────────┤
│  bm_strongs.transliteration                                     │
│         │                                                       │
│         ▼                                                       │
│  normalize_transliteration_for_lookup()                         │
│         │                                                       │
│         ▼                                                       │
│  _transliteration_map["elohim"] = ["H0430"]                     │
│  _transliteration_map["hesed"] = ["H2617"]                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Query Time (Search)                          │
├─────────────────────────────────────────────────────────────────┤
│  User input: "chesed"                                           │
│         │                                                       │
│         ▼                                                       │
│  normalize_user_hebrew_query("chesed")                          │
│         │                                                       │
│         ▼                                                       │
│  "hesed"                                                        │
│         │                                                       │
│         ▼                                                       │
│  _transliteration_map["hesed"] → ["H2617"]                      │
│         │                                                       │
│         ▼                                                       │
│  bm_words lookup → 247 occurrences                              │
└─────────────────────────────────────────────────────────────────┘
```

## Normalization Rules

The normalization function applies these transformations in order:

### Step 0: Pre-NFD Character Replacement
Characters that would be incorrectly decomposed by NFD:

| Character | Replacement | Reason |
|-----------|-------------|--------|
| `ç` (c-cedilla) | `s` | Strong's uses ç for Samekh (ס) |
| `Ç` | `S` | Uppercase variant |

### Step 1: Unicode NFD Decomposition
Separates base characters from combining diacritics:
- `ê` → `e` + combining circumflex
- `ô` → `o` + combining circumflex

### Step 2: Strip Combining Characters
Removes all Unicode category `Mn` (Mark, nonspacing):
- Removes circumflex, macron, breve, etc.
- `ĕlôhîym` → `elohiym`

### Step 3: Remove Modifier Letters
Removes aleph/ayin markers:

| Character | Unicode | Name |
|-----------|---------|------|
| `ʼ` | U+02BC | Modifier letter apostrophe (Aleph) |
| `ʻ` | U+02BB | Modifier letter turned comma (Ayin) |
| `ʾ` | U+02BE | Alternative aleph marker |
| `ʿ` | U+02BF | Alternative ayin marker |
| `'` | U+0027 | ASCII apostrophe |
| `` ` `` | U+0060 | ASCII grave accent |

### Step 4: Lowercase
Standard case normalization.

### Step 5: Het (ח) Normalization
Hebrew Het is variously transliterated as `ch`, `kh`, or `h`:

| Pattern | Result | Example |
|---------|--------|---------|
| `kh` | `h` | `khesed` → `hesed` |
| `ch` (not after `s`) | `h` | `chesed` → `hesed` |
| `sch` | `sch` | Preserved (German spelling) |

### Step 6: Qoph (ק) Normalization
| Pattern | Result | Example |
|---------|--------|---------|
| `q` | `k` | `qadosh` → `kadosh` |

### Step 7: Holem-Vav (וֹ) Pattern
The Hebrew vowel holem-vav is often written as `ow`:

| Pattern | Result | Example |
|---------|--------|---------|
| `Cow` (C=consonant) | `Co` | `yowm` → `yom` |

### Step 8: Masculine Plural (-ים)
Hebrew masculine plural ending:

| Pattern | Result | Example |
|---------|--------|---------|
| `...ym` (word-final) | `...m` | `elohiym` → `elohim` |

### Step 9: Simplify `iy` Sequences
| Pattern | Result | Example |
|---------|--------|---------|
| `iy` | `i` | `elohiym` → `elohim` |

## Complete Transformation Examples

| Strong's Input | Step-by-Step | Final Output |
|----------------|--------------|--------------|
| `ʼĕlôhîym` | `ʼ→∅`, `ĕ→e`, `ô→o`, `î→i`, `ym→m` | `elohim` |
| `chêçêd` | `ç→s`, `ê→e`, `ch→h` | `hesed` |
| `shâmaʻ` | `â→a`, `ʻ→∅` | `shama` |
| `yôwm` | `ô→o`, `ow→o` | `yom` |
| `dâbâr` | `â→a` | `dabar` |
| `ʼâhab` | `ʼ→∅`, `â→a` | `ahab` |
| `yâdaʻ` | `â→a`, `ʻ→∅` | `yada` |

## Industry Standard Comparison

### Sefaria (Jewish Text Platform)
- Uses two-form storage: `form` (with vowels) + `c_form` (consonantal)
- Fallback chain: exact → consonantal → n-grams → prefix-stripped
- Similar Het/Qoph normalization

### Unidecode (Python Library)
- General-purpose Unicode → ASCII
- Does NOT handle Biblical Hebrew patterns:
  - `ym → m` (plural ending)
  - `ch → h` (Het)
  - `ow → o` (holem-vav)

### Our Implementation
- **Unidecode-equivalent**: NFD + strip combining chars
- **Plus Biblical Hebrew rules**: Het, Qoph, plural, holem-vav
- **Result**: More accurate than plain unidecode

| Feature | Sefaria | Unidecode | Clarus |
|---------|---------|-----------|--------|
| Unicode normalization | ✓ | ✓ | ✓ |
| Het (ch→h) | ✓ | ✗ | ✓ |
| Samekh (ç→s) | - | ✗ | ✓ |
| Plural (ym→m) | ✓ | ✗ | ✓ |
| Holem-vav (ow→o) | ✓ | ✗ | ✓ |
| Two-form storage | ✓ (DB) | - | ✓ (Cache) |

## Code Location

| File | Function | Purpose |
|------|----------|---------|
| `src/hebrew_normalizer.py` | `normalize_transliteration_for_lookup()` | Normalize Strong's transliteration |
| `src/hebrew_normalizer.py` | `normalize_user_hebrew_query()` | Normalize user input |
| `src/bible_morphology.py` | `_load_strongs_cache()` | Build normalized lookup cache |
| `src/bible_morphology.py` | `_find_root_latin()` | Latin query lookup with normalization |

## Usage Example

```python
from src.hebrew_normalizer import (
    normalize_transliteration_for_lookup,
    normalize_user_hebrew_query,
)

# Normalize Strong's transliteration (at cache build time)
strongs_translit = "ʼĕlôhîym"
normalized = normalize_transliteration_for_lookup(strongs_translit)
# Result: "elohim"

# Normalize user query (at search time)
user_query = "chesed"
normalized = normalize_user_hebrew_query(user_query)
# Result: "hesed"

# Both "chesed" and "chêçêd" normalize to "hesed" → match!
```

## Test Coverage

| Test Category | Count | Pass Rate |
|---------------|-------|-----------|
| Hebrew Original (אלהים) | 15 | 100% |
| Hebrew Strong's (H430) | 20 | 100% |
| Hebrew Latin (elohim) | 30 | 100% |
| Total Hebrew | 65 | 100% |

### Test Cases for Latin Input

| Input | Expected Strong's | Occurrences |
|-------|-------------------|-------------|
| `elohim` | H0430 | 2,596 |
| `ahab` | H0157 | 204 |
| `chesed` | H2617 | 247 |
| `dabar` | H1697 | 1,439 |
| `shama` | H8085 | 1,159 |
| `yada` | H3045 | 944 |
| `yom` | H3117 | 2,287 |

## References

### Academic Standards
- **SBL Hebrew**: Society of Biblical Literature transliteration standard
- **Michigan-Claremont**: Standard used by OpenScriptures Hebrew Bible (OSHB)

### Data Sources
- **Strong's Concordance**: `bm_strongs` table with `transliteration` column
- **OSHB Morphology**: `bm_words` table with `strong_number` column

### External Resources
- [Sefaria Hebrew Utilities](https://github.com/Sefaria/Sefaria-Project/blob/master/sefaria/utils/hebrew.py)
- [OpenScriptures Hebrew Lexicon](https://github.com/openscriptures/HebrewLexicon)
- [SBL Hebrew Font Manual](http://www.sbl-site.org/Fonts/SBLHebrewUserManual1.5x.pdf)

## Changelog

| Date | Change |
|------|--------|
| 2026-02-03 | Initial implementation with Biblical Hebrew rules |
| 2026-02-03 | Fixed ç→s ordering (must happen before NFD) |
| 2026-02-03 | Added zero-padded Strong's numbers (H0430 format) |
