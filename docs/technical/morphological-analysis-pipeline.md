# Morphological Analysis Pipeline for Sacred Text Search

## Abstract

Clarus implements a multi-language morphological analysis pipeline for root-based keyword search across the Quran (Arabic) and Bible (Hebrew, Aramaic, Greek). The system maps surface word forms to their underlying roots using a combination of database lookup, algorithmic stemming, and transliteration normalization, enabling users to search by root concept rather than exact spelling. This document describes the computational linguistics techniques applied to Arabic, Hebrew, Greek, and Turkish text processing within the Clarus RAG system.

---

## 1. Introduction

Morphological analysis is the computational study of word structure. For sacred text search, it solves a fundamental problem: the same root concept appears in dozens of surface forms. A user searching for "write" in Arabic should find كتاب (book), كاتب (writer), and مكتوب (written) because all three derive from the root كتب (k-t-b). Without morphological analysis, a keyword search returns only exact matches and misses the majority of relevant verses.

This matters more for sacred texts than for ordinary corpora. Quranic Arabic, Biblical Hebrew, and Koine Greek are all morphologically rich languages where a single root can generate hundreds of derived forms through prefixation, suffixation, and internal vowel patterns. Turkish, the language of the Quran translations indexed in Clarus, presents a different challenge: agglutinative morphology where words grow by stacking suffixes.

The pipeline handles four distinct language families:

- **Root-based Semitic languages**: Arabic (Quran) and Hebrew/Aramaic (Old Testament), where most words derive from triconsonantal roots
- **Inflected ancient Greek**: Koine Greek (New Testament), where lemma-based lookup via Strong's Concordance is the standard approach
- **Agglutinative Turkish**: The target language for Quran translations, requiring lemmatization to strip case and tense suffixes

---

## 2. Arabic Morphological Analysis

### 2.1 The Arabic Root System

Arabic is a root-based Semitic language. The vast majority of Arabic words derive from triconsonantal (three-consonant) roots through a system of patterns called *wazn* (morphological templates). The root provides the semantic core; the pattern determines the grammatical category and specific meaning.

The root كتب (k-t-b, "to write") illustrates this:

| Surface Form | Transliteration | Meaning |
|---|---|---|
| كَتَبَ | kataba | he wrote (verb, past) |
| يَكْتُبُ | yaktubu | he writes (verb, present) |
| كِتَاب | kitāb | book (noun) |
| كَاتِب | kātib | writer (active participle) |
| مَكْتُوب | maktūb | written (passive participle) |
| مَكْتَبَة | maktaba | library (noun of place) |
| كِتَابَة | kitāba | writing (verbal noun) |

All seven forms share the consonantal skeleton k-t-b. A morphological search for this root retrieves all of them.

### 2.2 Root Extraction Algorithm

The `QuranMorphologySearch` class in `quran_morphology.py` implements a four-step cascade for root extraction. The underlying data comes from the Quranic Arabic Corpus v0.4 (University of Leeds), stored in three PostgreSQL tables: `qm_surahs`, `qm_ayahs`, and `qm_words`. The corpus contains 77,429 word tokens with 1,651 unique roots.

**Step 0: Special-term override**

Before any database or algorithmic lookup, a hardcoded dictionary handles terms whose roots cannot be reliably derived algorithmically. The most important case is the word for God:

```python
SPECIAL_TERMS: dict[str, tuple[str, str]] = {
    "الله": ("أله", "exact_match"),
    "لله": ("أله", "exact_match"),
    "بالله": ("أله", "exact_match"),
    "والله": ("أله", "exact_match"),
    "القران": ("قرأ", "exact_match"),
    # Latin forms
    "allah": ("أله", "buckwalter_exact"),
    "quran": ("قرأ", "buckwalter_exact"),
}
```

**Step 1: Exact database lookup**

The normalized input is matched against `token_clean` in `qm_words`:

```sql
SELECT root FROM qm_words WHERE token_clean = :q AND root IS NOT NULL LIMIT 1
```

**Step 2: Prefix stripping**

Arabic words frequently carry prepositional and conjunctive prefixes. The system tries stripping each prefix (longest first) and re-querying:

```python
PREFIXES = [
    "ولل",  # wa-li-l (and for the)
    "وال",  # wa-al (and the)
    "فال",  # fa-al (so the)
    "لل",   # li-l (for the)
    "ال",   # al (the)
    "ول",   # wa-l (and)
    "فل",   # fa-l (so)
    "و",    # wa (and)
    "ف",    # fa (so/then)
    "ل",    # li (for/to)
    "ب",    # bi (with/in)
    "ك",    # ka (like/as)
]
```

**Step 3: Input-as-root check**

If the input itself is a root (the user typed the root directly), a hamza-normalized SQL query finds it:

```sql
SELECT DISTINCT root FROM qm_words
WHERE REPLACE(REPLACE(REPLACE(root, 'أ', 'ا'), 'إ', 'ا'), 'آ', 'ا') = :q
AND root IS NOT NULL LIMIT 1
```

**Step 4: Tashaphyne algorithmic fallback**

When database lookup fails, the system falls back to the Tashaphyne Arabic light stemmer:

```python
from tashaphyne.stemming import ArabicLightStemmer
stemmer = ArabicLightStemmer()
stemmer.light_stem(query)
algo_root = stemmer.get_root()
```

The algorithmically derived root is then verified against the database to confirm it exists in the Quranic corpus.

**Result sources** are tracked for transparency: `exact_match`, `prefix_stripped`, `algorithmic`, `buckwalter_exact`, `buckwalter_fuzzy`, or `not_found`.

### 2.3 Buckwalter Transliteration

The Buckwalter transliteration scheme maps Arabic Unicode characters to ASCII, enabling users who cannot type Arabic to search using Latin characters. It is the standard scheme in computational Arabic linguistics (Buckwalter, 2002).

The mapping is implemented via the `pyarabic` library's `utf82latin` function. Key correspondences:

| Arabic | Buckwalter | Unicode |
|---|---|---|
| ا | A | U+0627 |
| ب | b | U+0628 |
| ت | t | U+062A |
| ث | v | U+062B |
| ج | j | U+062C |
| ح | H | U+062D |
| خ | x | U+062E |
| د | d | U+062F |
| ذ | * | U+0630 |
| ر | r | U+0631 |
| ز | z | U+0632 |
| س | s | U+0633 |
| ش | $ | U+0634 |
| ص | S | U+0635 |
| ض | D | U+0636 |
| ط | T | U+0637 |
| ظ | Z | U+0638 |
| ع | E | U+0639 |
| غ | g | U+063A |
| ف | f | U+0641 |
| ق | q | U+0642 |
| ك | k | U+0643 |
| ل | l | U+0644 |
| م | m | U+0645 |
| ن | n | U+0646 |
| ه | h | U+0647 |
| و | w | U+0648 |
| ي | y | U+064A |

Note that Buckwalter is case-sensitive: `H` (U+062D, ح) differs from `h` (U+0647, ه), and `S` (U+0635, ص) differs from `s` (U+0633, س). The Latin path in `_find_root_latin` handles this by using case-insensitive SQL matching and selecting the most frequent root when multiple case variants exist.

Example: كتب → `ktb`, الله → `Allh`, رحمن → `rHmn`

### 2.4 Arabic Text Normalization

The `normalize_arabic()` function in `arabic_normalizer.py` applies a six-step pipeline. The same pipeline runs at both indexing time and query time, ensuring consistency:

```python
def normalize_arabic(text: str) -> str:
    # Step 1: Strip tashkeel (diacritics/harakat)
    result = araby.strip_tashkeel(text)
    # Step 2: Hamza normalization
    result = result.replace("\u0623", "\u0627")  # أ → ا
    result = result.replace("\u0625", "\u0627")  # إ → ا
    result = result.replace("\u0622", "\u0627")  # آ → ا
    result = result.replace("\u0624", "\u0648")  # ؤ → و
    result = result.replace("\u0626", "\u064a")  # ئ → ي
    # Step 3: Hamzatu'l-wasl normalization
    result = result.replace("\u0671", "\u0627")  # ٱ → ا
    # Step 4: Ta-marbuta → ha
    result = result.replace("\u0629", "\u0647")  # ة → ه
    # Step 5: Alef-maksura → ya
    result = result.replace("\u0649", "\u064a")  # ى → ي
    # Step 6: Strip tatweel (elongation character)
    result = result.replace("\u0640", "")
    # Step 7: NFC normalization
    result = unicodedata.normalize("NFC", result)
    return result
```

The hamza normalization is particularly important: the letter alef appears in four Unicode variants (ا, أ, إ, آ) depending on the position of the hamza diacritic. Normalizing all four to bare alef (ا) ensures that words like أَكَلَ and اكل match the same root.

**Latin query normalization** handles Turkish keyboard input (users may type `ş`, `ç`, `ğ`, `ı`, `ö`, `ü`):

```python
def normalize_latin_query(text: str) -> str:
    text = text.lower()
    tr_map = str.maketrans("şçğıöü", "scgiou")
    return text.translate(tr_map)
```

**Buckwalter vowel stripping** handles romanized input where users include short vowels:

```python
def strip_buckwalter_vowels(text: str) -> str:
    # Removes: a(fatha), i(kasra), u(damma), o(sukun), ~(shadda), _(superscript alef)
    return "".join(c for c in text if c not in "aiuo~_")
```

This converts `kitab` to `ktb` and `salaam` to `slm`, enabling matching against the consonant-only root representations in the database.

**Fuzzy matching** via PostgreSQL `pg_trgm` serves as a last resort for Latin input that does not match after all normalization steps:

```sql
SELECT DISTINCT root, root_buckwalter,
       similarity(root_buckwalter, :q) AS sim
FROM qm_words
WHERE root_buckwalter % :q AND root IS NOT NULL
ORDER BY sim DESC
LIMIT 5
```

---

## 3. Hebrew Morphological Analysis

### 3.1 Hebrew Root System

Biblical Hebrew shares the triconsonantal root system with Arabic. Most Hebrew words derive from three-consonant roots, with vowel patterns and affixes determining grammatical function. The root שׁמר (sh-m-r, "to guard/keep") generates שׁוֹמֵר (shomer, guardian), מִשְׁמָר (mishmar, watch/guard), and שְׁמִירָה (shemira, guarding).

Unlike Arabic, where the root system is still productive in Modern Standard Arabic, Biblical Hebrew roots are accessed primarily through lexicographic tools. Clarus uses Strong's Exhaustive Concordance as the authoritative root-to-word mapping.

### 3.2 Strong's Concordance Integration

Strong's Exhaustive Concordance (James Strong, 1890) assigns a unique number to every Hebrew and Greek word in the King James Bible. Hebrew words receive numbers H1 through H8674; Greek words receive G1 through G5624. These numbers serve as stable identifiers for roots and lemmas across different editions and translations.

The `BibleMorphologySearch` class loads the entire `bm_strongs` table into memory at startup (~14,000 entries, approximately 2 MB). Three lookup structures are built:

1. **Forward map**: `strong_number → {original_word, transliteration, definition, language}`
   - Indexed by both padded (H0430) and unpadded (H430) variants
2. **Reverse map**: `normalized_hebrew → [strong_numbers]`
   - Enables lookup from Hebrew script input
3. **Transliteration map**: `transliteration_lower → [strong_numbers]`
   - Enables lookup from Latin input

When multiple Strong's numbers map to the same transliteration key (homographs), the lists are sorted by occurrence count in descending order. For example, "torah" maps to both H2960 (burden, 2 occurrences) and H8451 (law, 219 occurrences); H8451 is returned first.

The `_find_root` method dispatches based on script detection:

```python
script = detect_script(query)
if STRONGS_PATTERN.match(query):      # H3789 or G2316
    return await self._find_by_strongs_number(query)
if script == "hebrew":
    return await self._find_root_hebrew(query)
elif script == "greek":
    return await self._find_root_greek(query)
return await self._find_root_latin(query)
```

Script detection checks Unicode code points: Hebrew characters fall in U+0590-U+05FF, Arabic in U+0600-U+06FF, and Greek in U+0370-U+03FF or U+1F00-U+1FFF.

### 3.3 Hebrew Text Normalization

The `normalize_hebrew()` function in `hebrew_normalizer.py` applies a three-step pipeline:

```python
def normalize_hebrew(text: str) -> str:
    # Step 1: Strip nikud (vowel points and cantillation marks)
    result = remove_hebrew_nikud(text)
    # Step 2: NFC Unicode normalization
    result = unicodedata.normalize("NFC", result)
    # Step 3: Strip remaining combining characters
    result = "".join(c for c in result if unicodedata.category(c) != "Mn")
    return result
```

The nikud removal strips Unicode ranges U+0591-U+05BD (cantillation marks and vowel points) and U+05BF-U+05C7 (additional vowel marks), while preserving U+05BE (Maqaf, the Hebrew hyphen used as a word separator).

Example: `בְּרֵאשִׁ֖ית` (with nikud) normalizes to `בראשית` (consonants only).

### 3.4 Hebrew Transliteration

The `transliterate_hebrew()` function implements the SBL General Latin transliteration standard, the scholarly convention used in academic biblical studies:

```python
mapping = {
    "א": "ʾ",   # aleph
    "ב": "b",   # bet
    "ג": "g",   # gimel
    "ד": "d",   # dalet
    "ה": "h",   # he
    "ו": "w",   # vav
    "ז": "z",   # zayin
    "ח": "ḥ",   # het
    "ט": "ṭ",   # tet
    "י": "y",   # yod
    "כ": "k",   "ך": "k",   # kaf / final kaf
    "ל": "l",   # lamed
    "מ": "m",   "ם": "m",   # mem / final mem
    "נ": "n",   "ן": "n",   # nun / final nun
    "ס": "s",   # samek
    "ע": "ʿ",   # ayin
    "פ": "p",   "ף": "p",   # pe / final pe
    "צ": "ṣ",   "ץ": "ṣ",   # tsadi / final tsadi
    "ק": "q",   # qof
    "ר": "r",   # resh
    "שׁ": "š",  # shin (with dot)
    "שׂ": "ś",  # sin (with dot)
    "ש": "š",   # default to shin
    "ת": "t",   # tav
}
```

Final forms (ך, ם, ן, ף, ץ) are mapped identically to their regular counterparts, since they represent the same phoneme in word-final position.

**User-facing normalization** converts scholarly transliterations with diacritics to plain ASCII for matching user input. The `normalize_transliteration_for_lookup()` function handles several well-known problems in Hebrew romanization:

- **The Het problem** (ח): Can be written as `ch`, `kh`, `h`, `x`, or `ḥ`. All normalize to `h`.
- **The Tsadi problem** (צ): Can be written as `tz`, `ts`, `z`, or `ṣ`. All normalize to `ts`.
- **The Qoph problem** (ק): Can be written as `q` or `k`. Both normalize to `k`.
- **The Shin problem** (שׁ): Can be written as `sh` or `š`. Both normalize to `sh`.

```python
# Step 6: Normalize Het variants
stripped = stripped.replace("kh", "h")
stripped = re.sub(r"(?<!s)ch", "h", stripped)  # preserve 'sch'
# Step 7: Normalize Qoph variants
stripped = stripped.replace("q", "k")
# Step 8: Handle holem-vav pattern
stripped = re.sub(r"([^aeiou])ow([^aeiou]|$)", r"\1o\2", stripped)
# Step 9: Handle final 'ym' plural
if stripped.endswith("ym"):
    stripped = stripped[:-2] + "m"
```

This means `chesed`, `hesed`, and `khesed` all resolve to the same normalized form and find Strong's H2617 (חֶסֶד, lovingkindness).

### 3.5 Dual b/v Indexing

The Hebrew letter ב (Bet) presents a transliteration ambiguity. When it carries a dagesh (a dot indicating a stop consonant), it is pronounced /b/ and transliterated as `b`. Without the dagesh (fricative), it is pronounced /v/ and transliterated as `v`. Different scholarly conventions use different defaults:

- Strong's Concordance: fricative convention (`davar` for דָּבָר)
- User searches: often stop convention (`dabar`)
- ISO 259:1984, ALA-LC, and SBL all distinguish the two

The `_generate_bet_vet_variant()` function generates the alternate form by swapping all `b` and `v` characters:

```python
def _generate_bet_vet_variant(text: str) -> str:
    trans_table = str.maketrans("bv", "vb")
    return text.translate(trans_table)
```

During cache loading, both the normalized transliteration and its b/v variant are indexed to the same Strong's number. A user searching `dabar` finds the same results as `davar`.

---

## 4. Greek Morphological Analysis

### 4.1 Koine Greek in the New Testament

The New Testament was written in Koine Greek, the common dialect of the Hellenistic period (roughly 300 BCE to 300 CE). Unlike Classical Greek, Koine Greek is relatively uniform in morphology, making lemma-based lookup practical.

Clarus uses the MorphGNT dataset for Greek morphological data. Unlike the Hebrew OSHB data (which stores Strong's numbers per word), MorphGNT stores lemmas. The search pipeline therefore returns lemmas rather than Strong's numbers for Greek queries, and Greek Strong's number lookups are translated to lemmas via the `bm_strongs` cache.

### 4.2 Strong's Concordance for Greek (G1-G5624)

Greek Strong's numbers (G1-G5624) map to Greek lemmas in the `bm_strongs` table. When a user searches for `G2316` (θεός, God), the system:

1. Recognizes the Strong's pattern via `STRONGS_PATTERN = re.compile(r"^[HGhg]\d{1,5}$")`
2. Looks up the Greek word in `_strongs_cache`: `G2316 → {original_word: "θεός", transliteration: "theós"}`
3. Searches `bm_words` for the lemma `θεός`
4. Returns all New Testament verses containing that lemma

### 4.3 Greek Text Normalization

The `normalize_greek()` function in `greek_normalizer.py` handles both polytonic (ancient, with multiple accent types) and monotonic (modern, single accent) Greek:

```python
def normalize_greek(text: str) -> str:
    # Step 1: NFD decomposition to separate base letters from accents
    nfd_text = unicodedata.normalize("NFD", text)
    # Step 2: Strip combining characters (category Mn = Mark, nonspacing)
    result = "".join(c for c in nfd_text if unicodedata.category(c) != "Mn")
    # Step 3: NFC normalization
    result = unicodedata.normalize("NFC", result)
    # Step 4: Strip any remaining combining characters
    result = "".join(c for c in result if unicodedata.category(c) != "Mn")
    return result
```

This converts polytonic forms like `ἀγάπη` (with rough breathing and acute accent) to bare `αγαπη`. The Unicode ranges affected include U+0300-U+036F (Combining Diacritical Marks), U+1AB0-U+1AFF (Extended), and U+1DC0-U+1DFF (Supplement).

Example: `λόγος` → `λογος`, `ἀγάπη` → `αγαπη`

### 4.4 Greek Transliteration

The `transliterate_greek()` function implements the ALA-LC (American Library Association / Library of Congress) standard romanization for Greek:

```python
mapping = {
    # Vowels
    "α": "a",  "ε": "e",  "η": "ē",  "ι": "i",
    "ο": "o",  "υ": "y",  "ω": "ō",
    # Consonants
    "β": "b",  "γ": "g",  "δ": "d",  "ζ": "z",
    "θ": "th", "κ": "k",  "λ": "l",  "μ": "m",
    "ν": "n",  "ξ": "x",  "π": "p",  "ρ": "r",
    "σ": "s",  "ς": "s",  # regular and final sigma
    "τ": "t",  "φ": "ph", "χ": "ch", "ψ": "ps",
}
```

Multi-character sequences (θ→th, φ→ph, χ→ch, ψ→ps) are checked before single characters to avoid partial matches.

**User-facing normalization** strips diacritics from scholarly transliterations for plain ASCII matching:

```python
def normalize_greek_transliteration_for_lookup(translit: str) -> str:
    # NFD decomposition
    nfd = unicodedata.normalize("NFD", translit)
    # Remove combining characters (macrons ō→o, accents á→a)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    # Lowercase
    return stripped.lower()
```

This maps `zōḗ` → `zoe`, `eirḗnē` → `eirene`, `agápē` → `agape`, and `lógos` → `logos`.

**Reverse transliteration** converts Latin input back to Greek for lemma lookup:

```python
multi_char_mapping = {"th": "θ", "ph": "φ", "ch": "χ", "ps": "ψ"}
# Final sigma (ς) at word end, regular sigma (σ) otherwise
is_word_end = (i == len(text) - 1) or not text[i + 1].isalpha()
result += "ς" if is_word_end else "σ"
```

---

## 5. Cross-Reference Architecture

### 5.1 The BibleMorphologySearch Class

`BibleMorphologySearch` in `bible_morphology.py` orchestrates Hebrew and Greek morphology in a unified API. It uses a singleton pattern with an in-memory Strong's cache:

```python
class BibleMorphologySearch:
    _instance: Optional["BibleMorphologySearch"] = None
    _strongs_cache: dict[str, dict]       # number → entry
    _reverse_strongs: dict[str, list[str]] # normalized_hebrew → [numbers]
    _transliteration_map: dict[str, list[str]] # translit → [numbers]

    @classmethod
    async def get_instance(cls) -> "BibleMorphologySearch":
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance._load_strongs_cache()
        return cls._instance
```

The cache is loaded once at startup and reused across all requests. Loading involves building all three lookup structures plus sorting by occurrence count, which takes a single database round-trip.

### 5.2 Input Detection

The `_find_root()` method routes queries through a four-path cascade:

1. **Strong's number** (H#### or G####): Direct lookup via `STRONGS_PATTERN = re.compile(r"^[HGhg]\d{1,5}$")`
2. **Hebrew script** (U+0590-U+05FF): `_find_root_hebrew()` — nikud stripping, reverse Strong's lookup, fuzzy fallback
3. **Greek script** (U+0370-U+03FF or U+1F00-U+1FFF): `_find_root_greek()` — lemma exact match, word_clean match, fuzzy fallback
4. **Latin script**: `_find_root_latin()` — transliteration map lookup, normalized ASCII lookup, b/v variant lookup, fuzzy fallback

For Hebrew, the result is a Strong's number (e.g., `H3789`). For Greek, the result is a lemma (e.g., `θεός`). This asymmetry reflects the underlying data: the OSHB Hebrew data stores Strong's numbers per word token, while MorphGNT stores lemmas.

### 5.3 Strong's Number Cross-Referencing

Hebrew Strong's numbers are stored directly in `bm_words.strong_number`. Greek Strong's numbers are stored in `bm_strongs` but not in `bm_words` (MorphGNT uses lemmas instead). The translation path for Greek Strong's numbers is:

```
G2316 → bm_strongs cache → original_word: "θεός"
      → normalize_greek("θεός") → "θεος"
      → bm_words WHERE word_clean = "θεος" AND language = 'greek'
      → lemma: "θεός"
      → _search_by_lemma("θεός")
```

The `root_source` field in `BibleMorphologySearchResult` tracks which path was taken: `strongs_direct`, `strongs_to_lemma`, `exact_match`, `transliteration`, `fuzzy`, or `not_found`.

---

## 6. Turkish Language Processing

### 6.1 Turkish Lemmatization

Turkish is an agglutinative language: words are formed by attaching suffixes to a stem, and a single stem can generate dozens of surface forms. The word `namazla` (with prayer) and `namazını` (his/her prayer, accusative) both derive from the stem `namaz`. Without lemmatization, a search for `namaz` would miss both inflected forms.

Clarus uses the Zeyrek morphological analyzer (Sak et al., 2011) for Turkish lemmatization. The `get_lemma()` function in `lemmatizer.py` wraps Zeyrek with lazy initialization and output suppression:

```python
def get_lemma(word: str) -> str:
    word_lower = word.lower().strip()
    word_clean = re.sub(r"[^\w\s]", "", word_lower)

    # Check known corrections first
    if word_clean in KNOWN_LEMMA_CORRECTIONS:
        return KNOWN_LEMMA_CORRECTIONS[word_clean]

    analyzer = get_analyzer()
    results = analyzer.lemmatize(word_clean)
    if results and results[0][1]:
        lemmas = results[0][1]
        # Prefer lemmas that share a prefix with the input
        for lemma in lemmas:
            if lemma in word_clean or word_clean.startswith(lemma[:3]):
                return lemma
        return lemmas[0]
    return word_clean
```

### 6.2 Turkish-Specific Challenges

**Vowel harmony**: Turkish suffixes change their vowels to match the vowels of the stem. The plural suffix is `-lar` after back vowels and `-ler` after front vowels: `kitaplar` (books) vs. `evler` (houses). Zeyrek handles this internally.

**Agglutination depth**: Turkish words can carry many suffixes simultaneously. `Allaha` (to God, dative) requires stripping the dative suffix `-a`. `Allah'ın` (of God, genitive) requires stripping the apostrophe and genitive suffix `-ın`.

**İ/i case sensitivity**: Turkish has two distinct `i` letters: dotted `i` (U+0069) and dotless `ı` (U+0131). The uppercase of `i` is `İ` (U+0130), not `I`. The `normalize_latin_query()` function maps `ı` to `i` for ASCII compatibility.

**Known corrections**: Zeyrek occasionally returns incorrect lemmas for common words. A correction dictionary overrides these:

```python
KNOWN_LEMMA_CORRECTIONS = {
    "yardım": "yardım",   # Zeyrek incorrectly returns "yarmak"
    "yardımı": "yardım",
    "yardıma": "yardım",
    "kavuşacaklarını": "kavuşmak",
    "döneceklerini": "dönmek",
    "umanlar": "ummak",
    "huşu": "huşu",
}
```

### 6.3 Query Expansion for Turkish

Turkish lemmatization is applied during both indexing and query time. The `lemmatize_text()` function processes full sentences:

```python
def lemmatize_text(text: str) -> str:
    words = text.split()
    lemmas = [get_lemma(word) for word in words]
    return " ".join(lemmas)
```

Example: `"Sabır ve namazla Allah'a sığınıp yardım isteyin"` → `"sabır ve namaz allah sığın yardım iste"`

This lemmatized form is stored in `combined_lemma` on each semantic chunk and used for text normalization during indexing.

---

## 7. Etymology Database

### 7.1 Lane's Arabic-English Lexicon Integration

Lane's Arabic-English Lexicon (Edward William Lane, 1863) is the most comprehensive classical Arabic dictionary in English. The digitized version (Perseus/Tufts University, GPL-3.0) contains 47,919 entries covering 5,160 roots.

Clarus matches Lane's entries against the 1,651 Quranic roots from the Quranic Arabic Corpus. Of these, 1,337 roots (81%) have a corresponding Lane's entry. The remaining 314 roots receive LLM-generated Turkish definitions (Gemini 2.5 Flash via OpenRouter).

The etymology data is stored in PostgreSQL and served via the `/api/etymology/` endpoint. Each entry includes:

- Root in Arabic script and Buckwalter transliteration
- English definition from Lane's Lexicon
- Turkish definition (Lane's-derived or LLM-generated)
- Confidence score (0.0-1.0) for LLM-generated translations
- Occurrence count in the Quran
- Morphological forms derived from the root

### 7.2 LLM-Generated Turkish Definitions

For the 314 roots without Lane's coverage, and for all roots to provide Quranic-context Turkish definitions, Gemini 2.5 Flash generates Turkish translations. These are marked with confidence scores and a disclaimer that they are LLM-generated and not manually verified by human scholars.

### 7.3 Coverage Statistics

| Source | Roots | Coverage |
|---|---|---|
| Quranic Arabic Corpus v0.4 | 1,651 | 100% |
| Lane's Arabic-English Lexicon | 1,337 | 81% |
| LLM-generated (corpus-only roots) | 314 | 19% |
| Total with Turkish definition | 1,651 | 100% |

---

## 8. Data Sources and Citations

- **Quranic Arabic Corpus v0.4** — University of Leeds (GNU GPL)
  - Dukes, K. & Habash, N. (2010). "Morphological Annotation of Quranic Arabic." *Proceedings of the Seventh International Conference on Language Resources and Evaluation (LREC 2010)*. Valletta, Malta.
  - 77,429 word tokens, 1,651 unique roots, stored in `qm_surahs`, `qm_ayahs`, `qm_words` tables

- **Lane's Arabic-English Lexicon** — Edward William Lane (1863). Digitized by Perseus Digital Library, Tufts University (GPL-3.0).
  - 47,919 entries, 5,160 roots

- **Strong's Exhaustive Concordance** — James Strong (1890). Hebrew numbers H1-H8674, Greek numbers G1-G5624.

- **Open Scriptures Hebrew Bible (OSHB)** — Morphological data for Old Testament Hebrew, stored in `bm_words` with Strong's numbers per token.

- **MorphGNT** — Morphological Greek New Testament. Stores lemmas per token (no Strong's numbers in word table).

- **Buckwalter, T.** (2002). "Buckwalter Arabic Morphological Analyzer Version 1.0." Linguistic Data Consortium, University of Pennsylvania.

- **Sak, H., Güngör, T., & Saraçlar, M.** (2011). "Resources for Turkish Morphological Processing." *Language Resources and Evaluation*, 45(2), 249-261. (Zeyrek morphological analyzer)

---

## 9. References

Buckwalter, T. (2002). *Buckwalter Arabic Morphological Analyzer Version 1.0*. LDC2002L49. Philadelphia: Linguistic Data Consortium.

Dukes, K., & Habash, N. (2010). Morphological annotation of Quranic Arabic. In *Proceedings of LREC 2010* (pp. 2530-2536).

Lane, E. W. (1863). *An Arabic-English Lexicon*. London: Williams and Norgate. Digitized by Perseus Digital Library, Tufts University.

Sak, H., Güngör, T., & Saraçlar, M. (2011). Resources for Turkish morphological processing. *Language Resources and Evaluation*, 45(2), 249-261.

Society of Biblical Literature. (2014). *The SBL Handbook of Style*, 2nd ed. Atlanta: SBL Press.

Strong, J. (1890). *Strong's Exhaustive Concordance of the Bible*. New York: Hunt & Eaton.

Unicode Consortium. (2023). *The Unicode Standard, Version 15.0*. Mountain View, CA: Unicode Consortium.
