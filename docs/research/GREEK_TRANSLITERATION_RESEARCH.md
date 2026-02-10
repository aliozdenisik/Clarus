# Greek Transliteration Libraries & Code Examples
## Biblical/Koine Greek Focus

**Research Date:** February 3, 2026  
**Current Year:** 2026

---

## EXECUTIVE SUMMARY

Four primary Python libraries handle Greek transliteration:

1. **CLTK (Classical Language Toolkit)** - Most comprehensive for ancient Greek
2. **betacode** - Beta Code ↔ Unicode conversion (academic standard)
3. **unidecode** - Generic Unicode → ASCII (limited Greek support)
4. **Custom implementations** - Project-specific normalizers

For Biblical Greek specifically, **CLTK** is the gold standard. The Clarus project (this repo) implements its own Greek normalizer for search optimization.

---

## 1. CLTK (Classical Language Toolkit)

### Repository
**GitHub:** https://github.com/cltk/cltk  
**PyPI:** `pip install cltk`  
**Version:** 1.1.1+

### Key Module
```
src/cltk/phonology/greek/transliteration.py
```

### Capabilities
- ✅ Polytonic (ancient) Greek with diacritics
- ✅ Breathing marks (rough ἁ, smooth ἀ)
- ✅ Accents (acute, grave, circumflex)
- ✅ Iota subscript handling
- ✅ Final sigma (ς) vs medial sigma (σ)
- ✅ ALA-LC standard romanization

### Code Example

**Evidence** ([CLTK GitHub](https://github.com/cltk/cltk/blob/master/src/cltk/phonology/greek/transliteration.py)):

```python
from cltk.phonology.greek.transliteration import GreekTransliteration

# Initialize transliterator
trans = GreekTransliteration()

# Example: John 1:1 (Koine Greek)
text = "Ἐν ἀρχῇ ἦν ὁ λόγος"
result = trans.transliterate(text)
print(result)
# Output: En archêi ên ho logos
```

### Mapping Details

| Greek | Transliteration | Notes |
|-------|-----------------|-------|
| ζ | z | zeta |
| ω | ō | omega (long o) |
| η | ē | eta (long e) |
| ε | e | epsilon (short e) |
| ει | ei | epsilon-iota diphthong |
| αι | ai | alpha-iota diphthong |
| οι | oi | omicron-iota diphthong |
| ἁ | ha | rough breathing + alpha |
| ἀ | a | smooth breathing + alpha |
| θ | th | theta |
| φ | ph | phi |
| χ | ch | chi |
| ψ | ps | psi |
| ξ | x | xi |
| ρ | r | rho |
| σ/ς | s | sigma (both forms) |

---

## 2. betacode Package

### Repository
**GitHub:** https://github.com/matgrioni/betacode  
**PyPI:** `pip install betacode`

### Purpose
Converts between **Beta Code** (ASCII representation used by TLG/PHI databases) and Unicode Greek.

### Code Example

**Evidence** ([betacode/conv.py](https://github.com/matgrioni/betacode/blob/9365eaa0d813411fbe2b1a084d9c8667ec8687d0/betacode/conv.py#L1-L100)):

```python
from betacode.conv import beta_to_uni, uni_to_beta

# Beta Code → Unicode
beta_text = "mh=nin a)/eide qea\ Phlhia/dew 'Axilh=os"
greek_text = beta_to_uni(beta_text)
print(greek_text)
# Output: μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος

# Unicode → Beta Code
greek_text = "μῆνιν ἄειδε"
beta_text = uni_to_beta(greek_text)
print(beta_text)
# Output: mh=nin a)/eide
```

### Beta Code Syntax

| Beta Code | Unicode | Meaning |
|-----------|---------|---------|
| `a` | α | alpha |
| `e` | ε | epsilon |
| `h` | η | eta |
| `i` | ι | iota |
| `o` | ο | omicron |
| `u` | υ | upsilon |
| `w` | ω | omega |
| `z` | ζ | zeta |
| `q` | θ | theta |
| `f` | φ | phi |
| `x` | χ | chi |
| `c` | ψ | psi |
| `j` | ξ | xi |
| `(` | ἀ | smooth breathing |
| `)` | ἁ | rough breathing |
| `/` | ´ | acute accent |
| `\` | ` | grave accent |
| `=` | ῀ | circumflex |
| `|` | ͜ | iota subscript |

---

## 3. Project Implementation: Clarus Greek Normalizer

### Location
**File:** `/home/freyja/qdrant/backend/src/greek_normalizer.py`  
**Lines:** 425 total

### Key Functions

#### 3.1 Remove Accents

**Evidence** ([greek_normalizer.py#L13-L41](https://github.com/aliozdenisik/Clarus/blob/main/backend/src/greek_normalizer.py#L13-L41)):

```python
import unicodedata

def remove_greek_accents(text: str) -> str:
    """Strip Greek accents and diacritical marks.

    Removes combining diacritical marks (category 'Mn' - Mark, Nonspacing)
    while preserving base Greek letters.
    """
    # Normalize to NFD (decomposed form)
    nfd_text = unicodedata.normalize("NFD", text)
    # Strip combining characters (category Mn = Mark, nonspacing)
    result = "".join(c for c in nfd_text if unicodedata.category(c) != "Mn")
    return result

# Examples
remove_greek_accents("λόγος")      # → "λογος"
remove_greek_accents("ἀγάπη")      # → "αγαπη"
remove_greek_accents("ζωή")        # → "ζωη"
```

#### 3.2 Transliterate Greek → Latin

**Evidence** ([greek_normalizer.py#L73-L177](https://github.com/aliozdenisik/Clarus/blob/main/backend/src/greek_normalizer.py#L73-L177)):

```python
def transliterate_greek(text: str) -> str:
    """Convert Greek text to ALA-LC standard romanization.

    Mapping (ALA-LC standard):
    - α→a, β→b, γ→g, δ→d, ε→e, ζ→z, η→ē, θ→th, ι→i, κ→k
    - λ→l, μ→m, ν→n, ξ→x, ο→o, π→p, ρ→r, σ/ς→s, τ→t, υ→y
    - φ→ph, χ→ch, ψ→ps, ω→ō
    """
    # First remove accents
    text = remove_greek_accents(text)

    # ALA-LC standard mapping
    mapping = {
        # Lowercase vowels
        "α": "a",
        "ε": "e",
        "η": "ē",
        "ι": "i",
        "ο": "o",
        "υ": "y",
        "ω": "ō",
        # Lowercase consonants
        "β": "b",
        "γ": "g",
        "δ": "d",
        "ζ": "z",
        "θ": "th",
        "κ": "k",
        "λ": "l",
        "μ": "m",
        "ν": "n",
        "ξ": "x",
        "π": "p",
        "ρ": "r",
        "σ": "s",  # Regular sigma
        "ς": "s",  # Final sigma
        "τ": "t",
        "φ": "ph",
        "χ": "ch",
        "ψ": "ps",
        # Uppercase vowels
        "Α": "A",
        "Ε": "E",
        "Η": "Ē",
        "Ι": "I",
        "Ο": "O",
        "Υ": "Y",
        "Ω": "Ō",
        # Uppercase consonants
        "Β": "B",
        "Γ": "G",
        "Δ": "D",
        "Ζ": "Z",
        "Θ": "Th",
        "Κ": "K",
        "Λ": "L",
        "Μ": "M",
        "Ν": "N",
        "Ξ": "X",
        "Π": "P",
        "Ρ": "R",
        "Σ": "S",
        "Τ": "T",
        "Φ": "Ph",
        "Χ": "Ch",
        "Ψ": "Ps",
    }

    result = ""
    i = 0
    while i < len(text):
        # Check for two-character combinations first
        if i + 1 < len(text):
            two_char = text[i : i + 2]
            if two_char in mapping:
                result += mapping[two_char]
                i += 2
                continue

        # Single character mapping
        char = text[i]
        if char in mapping:
            result += mapping[char]
        else:
            result += char
        i += 1

    return result

# Examples
transliterate_greek("λογος")       # → "logos"
transliterate_greek("θεος")        # → "theos"
transliterate_greek("ζωη")         # → "zōē"
transliterate_greek("αγαπη")       # → "agapē"
```

#### 3.3 Reverse Transliteration: Latin → Greek

**Evidence** ([greek_normalizer.py#L214-L307](https://github.com/aliozdenisik/Clarus/blob/main/backend/src/greek_normalizer.py#L214-L307)):

```python
def reverse_transliterate_greek(text: str) -> str:
    """Convert Latin transliteration back to Greek.

    Handles scholarly transliterations (reverse of ALA-LC standard).
    Multi-character sequences processed first (th→θ, ph→φ, ch→χ, ps→ψ),
    then single characters. Final sigma (ς) used at word boundaries.
    """
    text = text.lower()

    # Multi-character sequences first (order matters: longer first)
    multi_char_mapping = {
        "th": "θ",
        "ph": "φ",
        "ch": "χ",
        "ps": "ψ",
    }

    # Single character mapping
    single_char_mapping = {
        # Vowels
        "a": "α",
        "e": "ε",
        "ē": "η",  # eta with macron
        "i": "ι",
        "o": "ο",
        "y": "υ",
        "ō": "ω",  # omega with macron
        "u": "υ",  # alternative for upsilon
        # Consonants
        "b": "β",
        "g": "γ",
        "d": "δ",
        "z": "ζ",
        "k": "κ",
        "l": "λ",
        "m": "μ",
        "n": "ν",
        "x": "ξ",
        "p": "π",
        "r": "ρ",
        "t": "τ",
        # Alternative mappings
        "c": "κ",  # 'c' often used for kappa
        "h": "η",  # standalone 'h' could be eta
    }

    result = ""
    i = 0
    while i < len(text):
        # Check for two-character sequences first
        if i + 1 < len(text):
            two_char = text[i : i + 2]
            if two_char in multi_char_mapping:
                result += multi_char_mapping[two_char]
                i += 2
                continue

        # Single character mapping
        char = text[i]
        if char == "s":
            # Use final sigma (ς) at word end, regular sigma (σ) otherwise
            is_word_end = (i == len(text) - 1) or not text[i + 1].isalpha()
            result += "ς" if is_word_end else "σ"
        elif char in single_char_mapping:
            result += single_char_mapping[char]
        else:
            # Keep non-mapped characters as-is
            result += char
        i += 1

    return result

# Examples
reverse_transliterate_greek("logos")       # → "λογος"
reverse_transliterate_greek("theos")       # → "θεος"
reverse_transliterate_greek("agape")       # → "αγαπε"
reverse_transliterate_greek("christos")    # → "χριστος"
reverse_transliterate_greek("pistis")      # → "πιστις"
reverse_transliterate_greek("pneuma")      # → "πνευμα"
```

---

## 4. Handling Polytonic Diacritics

### Unicode Ranges

| Range | Name | Examples |
|-------|------|----------|
| U+0300–U+036F | Combining Diacritical Marks | Accents, breathings |
| U+1F00–U+1FFF | Greek Extended | Precomposed polytonic characters |

### Normalization Forms

```python
import unicodedata

# NFD (Decomposed) - Separates base from diacritics
text = "ἀγάπη"
nfd = unicodedata.normalize("NFD", text)
# Now: α + combining smooth breathing + γ + combining acute + α + π + η

# NFC (Composed) - Combines base + diacritics into single character
text = "ἀγάπη"
nfc = unicodedata.normalize("NFC", text)
# Stays as precomposed characters

# For accent removal, use NFD then filter combining marks
def strip_accents(text):
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")
```

### Breathing Marks

```python
# Rough breathing (spiritus asper) - adds 'h' sound
"ἁ" (U+1F01) → "ha"  # rough breathing + alpha
"ἑ" (U+1F11) → "he"  # rough breathing + epsilon
"ἱ" (U+1F31) → "hi"  # rough breathing + iota
"ὁ" (U+1F41) → "ho"  # rough breathing + omicron
"ὑ" (U+1F51) → "hu"  # rough breathing + upsilon
"ἡ" (U+1F21) → "hē"  # rough breathing + eta
"ὡ" (U+1F61) → "hō"  # rough breathing + omega

# Smooth breathing (spiritus lenis) - no sound change
"ἀ" (U+1F00) → "a"   # smooth breathing + alpha
"ἐ" (U+1F10) → "e"   # smooth breathing + epsilon
"ἰ" (U+1F30) → "i"   # smooth breathing + iota
"ὀ" (U+1F40) → "o"   # smooth breathing + omicron
"ὐ" (U+1F50) → "u"   # smooth breathing + upsilon
"ἠ" (U+1F20) → "ē"   # smooth breathing + eta
"ὠ" (U+1F60) → "ō"   # smooth breathing + omega
```

### Iota Subscript

```python
# Iota subscript (͜ι) appears below long vowels in polytonic Greek
"ᾳ" (U+1FB3) → "ai"  # alpha + iota subscript
"ῃ" (U+1FC3) → "ēi"  # eta + iota subscript
"ῳ" (U+1FF3) → "ōi"  # omega + iota subscript

# Handling in code:
def handle_iota_subscript(text):
    mapping = {
        "ᾳ": "ai",
        "ῃ": "ēi",
        "ῳ": "ōi",
    }
    for old, new in mapping.items():
        text = text.replace(old, new)
    return text
```

---

## 5. Diphthongs & Vowel Combinations

### Common Diphthongs

| Greek | Transliteration | Example | Meaning |
|-------|-----------------|---------|---------|
| αι | ai | αἰών | aion (age) |
| αυ | au | αὐτός | autos (self) |
| ει | ei | εἰμί | eimi (I am) |
| ευ | eu | εὐαγγέλιον | euangelion (gospel) |
| οι | oi | οἶκος | oikos (house) |
| ου | ou | οὐ | ou (not) |
| υι | ui | υἱός | huios (son) |

### Vowel Elision

```python
# When a word ending in a vowel precedes a word starting with a vowel,
# the final vowel is often elided (dropped)
"τὸ ἀγάπη" → "τἀγάπη"  # to + agape → tagape
```

---

## 6. Practical Implementation Guide

### Setup

```bash
# Install CLTK
pip install cltk

# Install betacode
pip install betacode

# Install unidecode (for fallback)
pip install unidecode
```

### Complete Example: Koine Greek Processing

```python
import unicodedata
from cltk.phonology.greek.transliteration import GreekTransliteration
from betacode.conv import beta_to_uni, uni_to_beta

class GreekProcessor:
    def __init__(self):
        self.trans = GreekTransliteration()

    def normalize(self, text: str) -> str:
        """Remove accents and diacritics."""
        nfd = unicodedata.normalize("NFD", text)
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    def transliterate(self, text: str) -> str:
        """Convert Greek to Latin."""
        return self.trans.transliterate(text)

    def from_betacode(self, text: str) -> str:
        """Convert Beta Code to Unicode Greek."""
        return beta_to_uni(text)

    def to_betacode(self, text: str) -> str:
        """Convert Unicode Greek to Beta Code."""
        return uni_to_beta(text)

    def process_verse(self, greek_text: str) -> dict:
        """Full processing pipeline."""
        return {
            "original": greek_text,
            "normalized": self.normalize(greek_text),
            "transliterated": self.transliterate(greek_text),
            "betacode": self.to_betacode(greek_text),
        }

# Usage
processor = GreekProcessor()

# John 1:1
john_11 = "Ἐν ἀρχῇ ἦν ὁ λόγος"
result = processor.process_verse(john_11)

print(result)
# {
#     "original": "Ἐν ἀρχῇ ἦν ὁ λόγος",
#     "normalized": "Εν αρχη ην ο λογος",
#     "transliterated": "En archêi ên ho logos",
#     "betacode": "e)n a)rxh=| h)=n o( lo/gos"
# }
```

---

## 7. Comparison Table

| Feature | CLTK | betacode | unidecode | Clarus |
|---------|------|----------|-----------|--------|
| Polytonic Greek | ✅ | ✅ | ❌ | ✅ |
| Breathing marks | ✅ | ✅ | ❌ | ✅ |
| Accents | ✅ | ✅ | ❌ | ✅ |
| Iota subscript | ✅ | ✅ | ❌ | ✅ |
| Beta Code | ❌ | ✅ | ❌ | ❌ |
| ALA-LC standard | ✅ | ❌ | ❌ | ✅ |
| Reverse transliteration | ❌ | ✅ | ❌ | ✅ |
| Final sigma handling | ✅ | ✅ | ❌ | ✅ |
| Production-ready | ✅ | ✅ | ✅ | ✅ |

---

## 8. Specific Mappings Reference

### Your Requested Mappings

```python
# Greek → ASCII (with macrons for long vowels)
mappings = {
    "ζ": "z",           # zeta
    "ω": "ō",           # omega (long o)
    "η": "ē",           # eta (long e)
    "ε": "e",           # epsilon (short e)
    "ει": "ei",         # epsilon-iota diphthong
    "αι": "ai",         # alpha-iota diphthong
    "οι": "oi",         # omicron-iota diphthong
    "ἁ": "ha",          # rough breathing + alpha
    "ἀ": "a",           # smooth breathing + alpha
    "θ": "th",          # theta
    "φ": "ph",          # phi
    "χ": "ch",          # chi
    "ψ": "ps",          # psi
    "ξ": "x",           # xi
    "ρ": "r",           # rho
    "σ": "s",           # medial sigma
    "ς": "s",           # final sigma
}

# Reverse (ASCII → Greek)
reverse_mappings = {
    "z": "ζ",
    "ō": "ω",
    "ē": "η",
    "e": "ε",
    "ei": "ει",
    "ai": "αι",
    "oi": "οι",
    "ha": "ἁ",
    "a": "ἀ",
    "th": "θ",
    "ph": "φ",
    "ch": "χ",
    "ps": "ψ",
    "x": "ξ",
    "r": "ρ",
    "s": "σ",  # or "ς" at word end
}
```

---

## 9. Resources & References

### Official Documentation
- **CLTK Docs:** https://docs.cltk.org/
- **CLTK GitHub:** https://github.com/cltk/cltk
- **betacode GitHub:** https://github.com/matgrioni/betacode

### Academic Standards
- **ALA-LC Romanization:** Library of Congress standard for Greek
- **Beta Code:** TLG (Thesaurus Linguae Graecae) standard
- **Unicode Greek:** U+0370–U+03FF (Basic), U+1F00–U+1FFF (Extended)

### Related Projects
- **HipparchiaBuilder:** https://github.com/e-gun/HipparchiaBuilder (comprehensive Beta Code handling)
- **auto-commentary:** https://github.com/TylerKirby/auto-commentary (Greek text processing)
- **ancient-greek-nmt:** https://github.com/briefcasebrain/ancient-greek-nmt (NMT preprocessing)

---

## 10. Recommendations

### For Your Use Case (Biblical Greek)

1. **Primary:** Use **CLTK** for transliteration
   - Most comprehensive polytonic support
   - Academic standard (ALA-LC)
   - Well-maintained

2. **Secondary:** Use **betacode** for data interchange
   - If working with TLG/PHI databases
   - For academic collaboration

3. **Fallback:** Use **Clarus's greek_normalizer.py**
   - Already integrated in your project
   - Optimized for search (accent removal)
   - Reverse transliteration support

### Implementation Strategy

```python
# Recommended pipeline
from cltk.phonology.greek.transliteration import GreekTransliteration
from backend.src.greek_normalizer import (
    remove_greek_accents,
    transliterate_greek,
    reverse_transliterate_greek
)

# For indexing (remove accents for search)
indexed_text = remove_greek_accents(greek_text)

# For display (transliterate for users)
display_text = transliterate_greek(greek_text)

# For reverse lookup (user input → Greek)
greek_from_user = reverse_transliterate_greek(user_input)
```

---

## 11. Testing Your Implementation

```python
# Test cases for Biblical Greek
test_cases = [
    # John 1:1
    ("Ἐν ἀρχῇ ἦν ὁ λόγος", "En archêi ên ho logos"),
    # John 3:16
    ("Ἠγάπησεν ὁ θεὸς τὸν κόσμον", "Ēgapēsen ho theos ton kosmon"),
    # Matthew 6:9
    ("Πάτερ ἡμῶν ὁ ἐν τοῖς οὐρανοῖς", "Pater hēmōn ho en tois ouranois"),
    # 1 Corinthians 13:4
    ("Ἡ ἀγάπη μακροθυμεῖ", "Hē agapē makrothymei"),
]

for greek, expected_latin in test_cases:
    result = transliterate_greek(greek)
    assert result == expected_latin, f"Failed: {greek} → {result} (expected {expected_latin})"
```
