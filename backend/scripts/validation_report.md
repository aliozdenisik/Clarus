# Bible Keyword Search — Data Source Validation Report

**Date:** 2026-02-02
**Task:** Wave 0 — Data Source Validation & OSHB XML Prototype Parse
**Author:** Sisyphus Agent (automated validation)

---

## 1. OSHB XML Structure Analysis

**Source:** `openscriptures/morphhb` (WLC 4.20, OSHM morphology, CC-BY-4.0)

### 1.1 Element Hierarchy

```
<osis>                                    # Root (OSIS namespace)
  <osisText xml:lang="he">               # Language: Hebrew
    <header>                              # Metadata, revision history
      <work osisWork="OSHB">              # Work identifiers
    </header>
    <div type="book" osisID="Gen">        # Book container
      <chapter osisID="Gen.1">            # Chapter container
        <verse osisID="Gen.1.1">          # Verse container
          <w lemma="b/7225"               # Word element
             morph="HR/Ncfsa"             #   morphological tag
             id="01001"                   #   unique word ID
             n="1.0">                     #   word position
            בְּ/רֵאשִׁ֖ית                    #   Hebrew text (with cantillation)
          </w>
          <seg type="x-maqqef">־</seg>    # Punctuation segment
          <seg type="x-sof-pasuq">׃</seg> # End-of-verse marker
        </verse>
      </chapter>
    </div>
  </osisText>
</osis>
```

### 1.2 `<w>` Element Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `lemma` | Strong's number(s) with optional prefixes | `"b/7225"`, `"1254 a"`, `"c/m/6529"` |
| `morph` | Morphological tag (OSHM scheme) | `"HR/Ncfsa"`, `"HVqp3ms"` |
| `id` | Unique word identifier | `"01001"` |
| `n` | Word position within verse | `"1.0"` |
| `type` | Special marker (Kethiv only) | `"x-ketiv"` |

### 1.3 `<seg>` Element Types

| Type | Description | Count (Genesis) |
|------|-------------|-----------------|
| `x-sof-pasuq` | End of verse marker (׃) | ~1,533 |
| `x-maqqef` | Hyphen/maqqef (־) | ~2,800 |
| `x-paseq` | Paseq separator (׀) | ~337 |

### 1.4 Word Count for Genesis 1-3

| Chapter | `<w>` Elements |
|---------|---------------|
| Genesis 1 | **434** |
| Genesis 2 | **328** |
| Genesis 3 | **347** |
| **Total Gen 1-3** | **1,109** |

**Total `<w>` elements in Genesis:** 20,629
**Total `<w>` elements across all 39 books:** 306,785

---

## 2. Strong's Number Format Variants (Complete Catalog)

**Source:** All 39 OSHB book files parsed.

### 2.1 Primary Formats

| Format | Count | % | Examples | Description |
|--------|-------|---|----------|-------------|
| `plain_number` | 148,142 | 48.3% | `430`, `853`, `1961` | Bare Strong's number |
| `1_prefix` | 88,363 | 28.8% | `c/559`, `d/8064`, `b/7225` | Single prefix + number |
| `number_variant_letter` | 41,396 | 13.5% | `1254 a`, `5921 a`, `7363 b` | Number + space + variant letter |
| `1_prefix_with_variant` | 17,092 | 5.6% | `c/6213 a`, `m/5921 a` | Prefix + number + variant |
| `bare_prefix` | 5,876 | 1.9% | `l`, `b`, `m`, `k`, `c` | Prefix-only (no Strong's number) |
| `2_prefix` | 4,566 | 1.5% | `c/d/776`, `c/l/2822` | Two prefixes + number |
| `compound_plus` | 801 | 0.3% | `1177+`, `4314+`, `883+` | Compound name with `+` suffix |
| `2_prefix_with_variant` | 793 | 0.3% | `c/b/1328 b`, `c/l/3722 a` | Two prefixes + number + variant |
| `3_prefix` | 22 | <0.01% | `c/m/l/4605`, `c/l/d/7134` | Three prefixes + number |
| `3_prefix_with_variant` | 2 | <0.01% | `c/l/m/1004 b`, `c/l/m/7097 a` | Three prefixes + number + variant |

### 2.2 Prefix Meanings

| Prefix | Hebrew | Meaning | Morph Code |
|--------|--------|---------|------------|
| `b` | בְּ | in, at, with | `R` (preposition) |
| `c` | וְ | and, but | `C` (conjunction) |
| `d` | הַ | the (article) | `Td` (article) |
| `k` | כְּ | like, as | `R` (preposition) |
| `l` | לְ | to, for | `R` (preposition) |
| `m` | מִ | from | `R` (preposition) |

### 2.3 Bare Prefix Breakdown

| Bare Prefix | Count | Context |
|-------------|-------|---------|
| `l` | 4,413 | Preposition with pronominal suffix (e.g., `ל/וֹ` = "to him") |
| `b` | 1,362 | Preposition with pronominal suffix (e.g., `בּ/וֹ` = "in him") |
| `m` | 92 | Preposition with pronominal suffix (e.g., `מֵ/הֶם` = "from them") |
| `k` | 9 | Preposition with pronominal suffix (e.g., `כָּ/הֶם` = "like them") |

### 2.4 Parsing Strategy Recommendation

```
lemma_str → split by '/'
  → last part = Strong's number (may include ' a', ' b' variant suffix)
  → preceding parts = grammatical prefixes (b, c, d, k, l, m)
  → if '+' suffix → compound proper name
  → if bare prefix only (no number) → pronominal suffix, no Strong's lookup needed
```

---

## 3. Morphological Tag Format

### 3.1 Hebrew Morphological Tags (OSHM Scheme)

**Format:** `H{POS}{details}` where `H` = Hebrew language prefix.

| Code | Part of Speech | Example | Meaning |
|------|---------------|---------|---------|
| `HV` | Verb | `HVqp3ms` | Qal perfect 3rd masc sing |
| `HN` | Noun | `HNcmsa` | Common noun masc sing absolute |
| `HA` | Adjective | `HAamsa` | Adjective masc sing absolute |
| `HR` | Preposition | `HR/Ncfsa` | Preposition + noun |
| `HC` | Conjunction | `HC/Vqw3ms` | Conjunction + verb |
| `HT` | Particle | `HTd` (article), `HTn` (negative), `HTo` (object marker) |
| `HP` | Pronoun | `HPp2ms` | Personal pronoun 2nd masc sing |
| `HS` | Suffix | `HSp3ms` | Pronominal suffix 3rd masc sing |

**Verb Stem Codes (after `HV`):**

| Code | Stem | Description |
|------|------|-------------|
| `q` | Qal | Simple active |
| `N` | Niphal | Simple passive/reflexive |
| `p` | Piel | Intensive active |
| `P` | Pual | Intensive passive |
| `h` | Hiphil | Causative active |
| `H` | Hophal | Causative passive |
| `t` | Hithpael | Reflexive |
| `v` | Special | Rare stems (Hishtaphel, etc.) |

**Verb Form Codes:**

| Code | Form |
|------|------|
| `p` | Perfect |
| `i` | Imperfect |
| `w` | Wayyiqtol (narrative) |
| `v` | Imperative |
| `a` | Infinitive absolute |
| `c` | Infinitive construct |
| `r` | Participle |

### 3.2 Compound Morphological Tags

Tags can be compound, separated by `/`:
- `HC/Vqw3ms` = Conjunction + Qal wayyiqtol 3ms
- `HR/Ncfsa` = Preposition + Common noun fem sing absolute
- `HTd/Ncmpa` = Article + Common noun masc plur absolute
- `HC/R/Vqc` = Conjunction + Preposition + Qal infinitive construct

---

## 4. Aramaic Morphological Tag Format (Daniel 2:4b-7:28)

### 4.1 Language Prefix

Aramaic sections use prefix `A` instead of `H`:

| Hebrew | Aramaic | Meaning |
|--------|---------|---------|
| `HV` | `AV` | Verb |
| `HN` | `AN` | Noun |
| `HA` | `AA` | Adjective |
| `HR` | `AR` | Preposition |
| `HC` | `AC` | Conjunction |
| `HT` | `AT` | Particle |
| `HP` | `AP` | Pronoun |
| `HD` | `AD` | Adverb |

### 4.2 Aramaic Section Distribution in Daniel

| Chapter | Total Words | Hebrew | Aramaic | Notes |
|---------|-------------|--------|---------|-------|
| Dan 1 | 306 | 297 | 9 | Mostly Hebrew narrative |
| Dan 2 | 859 | 39 | 1 (+ 819 Aramaic*) | Transition at 2:4b |
| Dan 3 | 650 | 0 | 0* | Full Aramaic |
| Dan 4 | 620 | 0 | 0* | Full Aramaic |
| Dan 5 | 548 | 0 | 0* | Full Aramaic |
| Dan 6 | 558 | 0 | 0* | Full Aramaic |
| Dan 7 | 507 | 0 | 0* | Full Aramaic |
| Dan 8 | 384 | 364 | 20 | Return to Hebrew |
| Dan 9 | 467 | 456 | 11 | Hebrew with Aramaic loanwords |
| Dan 10 | 342 | 331 | 11 | Hebrew |
| Dan 11 | 617 | 592 | 25 | Hebrew |
| Dan 12 | 177 | 164 | 13 | Hebrew |

*Note: Chapters 3-7 show 0 for both Hebrew and Aramaic in the `H`/`HA` prefix count because the Aramaic morph tags use `A` prefix (not `HA`). The actual Aramaic word counts are: Dan 3: ~650, Dan 4: ~620, Dan 5: ~548, Dan 6: ~558, Dan 7: ~507.

### 4.3 Aramaic-Specific Features

1. **Emphatic State:** Aramaic nouns use `/א` suffix for emphatic (definite) state
   - Example: `מַלְכָּ/א` (the king) — morph: `ANcmsd/Td`
   - The `/Td` in morph indicates the emphatic article is part of the word

2. **Aramaic Verb Stems:** Same codes as Hebrew but with `A` prefix
   - `AVqp3ms` = Aramaic Qal perfect 3ms
   - `AVhp3ms` = Aramaic Haphel (= Hebrew Hiphil) perfect 3ms

3. **Mixed Hebrew/Aramaic:** Dan 2:4 contains both Hebrew and Aramaic words in the same verse, clearly distinguished by morph prefix.

### 4.4 Aramaic Morph Tag Distribution (Daniel 2-7)

| Category | Count | Top Tags |
|----------|-------|----------|
| `AN` (Noun) | 1,105 | `ANcmsd/Td` (273), `ANp` (138), `ANcmsa` (92) |
| `AC` (Conjunction) | 684 | `AC` (76), `AC/Ncmsd/Td` (46), `AC/Vqrmsa` (28) |
| `AV` (Verb) | 670 | `AVqrmsa` (80), `AVqp3ms` (78), `AVqrmpa` (49) |
| `AR` (Preposition) | 619 | `AR` (152), `AR/Sp3ms` (52), `AR/Ncmsc` (46) |
| `AT` (Particle) | 319 | `ATr` (191), `ATn` (60), `ATa` (16) |
| `AA` (Adjective) | 169 | `AAamsa` (35), `AAafsa` (23), `AAamsd/Td` (19) |
| `AP` (Pronoun) | 106 | `APdxms` (25), `APp2ms` (16), `APp1cs` (12) |
| `AD` (Adverb) | 30 | `AD` (30) |

---

## 5. Kethiv/Qere Variant Format

### 5.1 Identification

- **Kethiv** (written form): `<w type="x-ketiv">` — 1,268 occurrences across all books
- **Qere** (read form): The immediately following `<w>` element (no special type attribute)

### 5.2 Pattern

```xml
<!-- Kethiv (written in scroll) -->
<w lemma="c/559" morph="HC/Vqw3ms" type="x-ketiv">ו/יאמר</w>
<!-- Qere (read aloud) -->
<w lemma="c/559" morph="HC/Vqw1cs">וָ/אֹמַ֣ר</w>
```

### 5.3 Types of Kethiv/Qere Differences

| Type | Example | Description |
|------|---------|-------------|
| Spelling variant | `ו/ישתחו` → `וַ/יִּשְׁתַּ֖חוּ` | Same word, different orthography |
| Stem difference | `ו/ילדו` (Qal) → `וַ/יִּוָּלְד֧וּ` (Niphal) | Different verbal stem |
| Person/number | `ו/יאמר` (3ms) → `וָ/אֹמַ֣ר` (1cs) | Different grammatical form |
| Different word | `לא` → `לוּ` | Entirely different word |

### 5.4 Parsing Implication

For keyword search, **both Kethiv and Qere forms should be indexed**. The Kethiv `<w>` has `type="x-ketiv"` and the Qere follows immediately. Both share the same `lemma` (Strong's number) in most cases.

---

## 6. Scrollmapper JSON Schema (KJVA)

**Source:** `scrollmapper/bible_databases` — `sources/en/KJVA/KJVA.json`

### 6.1 Schema Structure

```json
{
  "books": [
    {
      "name": "Genesis",                    // Book name (string)
      "chapters": [
        {
          "chapter": 1,                      // Chapter number (int)
          "name": "Genesis 1",               // Chapter display name (string)
          "verses": [
            {
              "verse": 1,                    // Verse number (int)
              "chapter": 1,                  // Chapter number (int, redundant)
              "name": "Genesis 1:1",         // Full reference (string)
              "text": "In the beginning..."  // Verse text (string)
            }
          ]
        }
      ]
    }
  ]
}
```

### 6.2 Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `books[].name` | string | Book name (e.g., "Genesis", "1 Samuel") |
| `books[].chapters[].chapter` | int | Chapter number |
| `books[].chapters[].name` | string | Display name (e.g., "Genesis 1") |
| `books[].chapters[].verses[].verse` | int | Verse number |
| `books[].chapters[].verses[].chapter` | int | Chapter number (redundant) |
| `books[].chapters[].verses[].name` | string | Full reference (e.g., "Genesis 1:1") |
| `books[].chapters[].verses[].text` | string | English verse text (KJVA) |

### 6.3 Notes

- File size: ~13.5 MB (full KJVA including Apocrypha)
- Nested structure: `books → chapters → verses`
- The `name` field at verse level provides a ready-made reference string
- No Strong's numbers or morphological data — this is English text only
- Useful for: displaying English translations alongside Hebrew keyword search results

---

## 7. Strong's Dictionary (Hebrew)

**Source:** `openscriptures/strongs` — `hebrew/strongs-hebrew-dictionary.js`

### 7.1 Format

JavaScript file containing a JSON object assigned to `var strongsHebrewDictionary`.

### 7.2 Entry Schema

```json
{
  "H3789": {
    "lemma": "כָּתַב",           // Hebrew word
    "xlit": "kâthab",           // Transliteration
    "pron": "kaw-thab'",        // Pronunciation
    "derivation": "a primitive root;",  // Etymology
    "strongs_def": "to grave...",       // Strong's definition
    "kjv_def": "describe, record..."    // KJV usage
  }
}
```

### 7.3 Statistics

- **Total entries:** 8,427 (H1 through H8674, with gaps)
- **Saved to:** `backend/data/strongs/strongs_hebrew.json`

### 7.4 Verified Key Entries

| Strong's | Lemma | Transliteration | Meaning |
|----------|-------|-----------------|---------|
| H3789 | כָּתַב | kâthab | to write |
| H559 | אָמַר | ʼâmar | to say |
| H1980 | הָלַךְ | hâlak | to walk |
| H1254 | בָּרָא | bârâʼ | to create |
| H8085 | שָׁמַע | shâmaʻ | to hear |
| H3045 | יָדַע | yâdaʻ | to know |
| H5414 | נָתַן | nâthan | to give |
| H6213 | עָשָׂה | ʻâsâh | to make |
| H935 | בּוֹא | bôwʼ | to come |
| H1961 | הָיָה | hâyâh | to be |

---

## 8. Issues & Concerns

### 8.1 Strong's JSON Parsing

The `strongs-hebrew-dictionary.js` file is not valid JSON — it's a JavaScript variable assignment. The file also contains some entries with embedded quotes that break standard JSON parsing. **Resolution:** Used regex-based extraction, successfully parsed 8,427 of ~8,674 entries. A few entries with complex nested quotes were lost. For production, consider using the XML source (`StrongHebrewG.xml`) instead.

### 8.2 Aramaic Strong's Numbers

Some Aramaic Strong's numbers (e.g., H560 `אמר` Aramaic) are **not present** in the extracted Strong's dictionary. This is because the JS file may have parsing issues for those entries. The XML source should be used as fallback.

### 8.3 Bare Prefix Lemmas

5,876 words have bare prefix lemmas (`l`, `b`, `m`, `k`, `c`) with no Strong's number. These are prepositions attached to pronominal suffixes. The ETL pipeline must handle these gracefully — they should be indexed as grammatical particles, not as searchable roots.

### 8.4 Compound Names (`+` suffix)

801 words use the `+` suffix format (e.g., `1177+` for Baal-*). These represent multi-word proper names where the Strong's number refers to the first component. The ETL pipeline should strip the `+` for Strong's lookup but preserve it for display.

### 8.5 Kethiv/Qere Dual Indexing

1,268 Kethiv entries exist. For maximum search recall, both Kethiv and Qere forms should be indexed. The Kethiv `<w>` has `type="x-ketiv"` and is immediately followed by the Qere `<w>`. Both typically share the same Strong's number.

### 8.6 Variant Letters on Strong's Numbers

41,396 words (13.5%) use variant letters (e.g., `1254 a`, `2490 c`). These distinguish homonyms — different words that share the same Strong's number. The ETL pipeline should:
1. Strip the variant letter for Strong's dictionary lookup
2. Preserve the variant for disambiguation in search results

### 8.7 Ezra Aramaic Sections

In addition to Daniel 2:4b-7:28, Ezra 4:8-6:18 and 7:12-26 also contain Aramaic. These were not fully validated in this report but follow the same `A` prefix morph tag pattern.

---

## 9. Summary & Recommendations

### Data Sources Validated

| Source | Status | Location |
|--------|--------|----------|
| OSHB XML (morphhb) | ✅ Validated | Clone from `openscriptures/morphhb` |
| Strong's Hebrew JSON | ✅ Extracted (8,427 entries) | `backend/data/strongs/strongs_hebrew.json` |
| Scrollmapper KJVA | ✅ Schema validated | `scrollmapper/bible_databases` |
| Test data | ✅ 30 entries verified | `backend/tests/bible_keyword_test_data.json` |

### ETL Pipeline Requirements (for Task 1+)

1. **XML Parser:** Use `xml.etree.ElementTree` with OSIS namespace
2. **Lemma Parser:** Handle 9 format variants (see Section 2)
3. **Morph Parser:** Handle Hebrew (`H` prefix) and Aramaic (`A` prefix)
4. **Kethiv/Qere:** Index both forms, flag Kethiv with `type="x-ketiv"`
5. **Strong's Lookup:** Strip prefixes and variant letters before lookup
6. **Aramaic Detection:** Use morph prefix `A` to identify Aramaic words
7. **Compound Names:** Handle `+` suffix for multi-word proper names
8. **Bare Prefixes:** Skip or index as particles (no Strong's lookup)
