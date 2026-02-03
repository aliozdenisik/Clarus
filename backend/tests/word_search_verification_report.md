# Word Search Verification Report

**Generated:** 2026-02-03 19:50:25
**Total Tests:** 150

## Executive Summary

| Metric | Value |
|--------|-------|
| **Overall Pass Rate** | **93.3%** |
| Passed | 140 |
| Failed | 10 |
| Errors | 0 |

## Results by Source

| Source | Total | Passed | Pass Rate |
|--------|-------|--------|-----------|
| Quran | 50 | 50 | 100.0% |
| Hebrew OT | 50 | 40 | 80.0% |
| Greek NT | 50 | 50 | 100.0% |

## Results by Input Type

| Input Type | Total | Passed | Pass Rate |
|------------|-------|--------|-----------|
| Latin | 84 | 74 | 88.1% |
| Original | 45 | 45 | 100.0% |
| Edge Case | 21 | 21 | 100.0% |

## Metric-Specific Pass Rates

| Metric | Pass Rate |
|--------|-----------|
| Total Occurrence (±5%) | 92.2% |
| Unique Words (80% intersection) | 92.2% |
| Books/Surahs Count (±5%) | 92.2% |
| Verse Count (±5%) | 92.2% |

## Detailed Results

### Quran

| ID | Query | Description | Status | Occurrences | Words | Books | Verses |
|-----|-------|-------------|--------|-------------|-------|-------|--------|
| Q-L01 | `ktb` | Write/Book - common root | ✅ | 319 | 47 | 61 | 279 |
| Q-L02 | `qwl` | Say/Speak - most frequent verb | ✅ | 1722 | 109 | 84 | 1383 |
| Q-L03 | `Amn` | Believe/Faith - core concept | ✅ | 879 | 110 | 77 | 723 |
| Q-L04 | `Elm` | Knowledge/Science | ✅ | 854 | 116 | 85 | 728 |
| Q-L05 | `Slm` | Peace/Islam/Submit | ✅ | 140 | 47 | 48 | 127 |
| Q-L06 | `Sbr` | Patience | ✅ | 103 | 38 | 45 | 93 |
| Q-L07 | `Hmd` | Praise | ✅ | 68 | 13 | 44 | 66 |
| Q-L08 | `rHm` | Mercy - with emphatic H | ✅ | 339 | 53 | 62 | 313 |
| Q-L09 | `Sly` | Prayer | ✅ | 25 | 20 | 21 | 25 |
| Q-L10 | `nsr` | Victory/Help | ✅ | 158 | 74 | 46 | 137 |
| Q-L11 | `Hkm` | Wisdom/Judgment | ✅ | 210 | 45 | 57 | 189 |
| Q-L12 | `Sdq` | Truth/Charity | ✅ | 155 | 58 | 49 | 144 |
| Q-L13 | `Zln` | Oppression/Darkness | ✅ | 4 | 4 | 3 | 4 |
| Q-L14 | `Swr` | Image/Form | ✅ | 19 | 8 | 17 | 17 |
| Q-L15 | `jnn` | Paradise/Garden | ✅ | 201 | 28 | 70 | 196 |
| Q-L16 | `nwr` | Light | ✅ | 194 | 23 | 62 | 174 |
| Q-L17 | `Hsn` | Good/Beautiful | ✅ | 194 | 44 | 50 | 177 |
| Q-L18 | `xwf` | Fear | ✅ | 124 | 44 | 42 | 112 |
| Q-L19 | `rjw` | Hope | ✅ | 28 | 14 | 21 | 27 |
| Q-L20 | `Twb` | Repentance | ✅ | 87 | 32 | 25 | 69 |
| Q-L21 | `hdY` | Guidance | ✅ | 316 | 103 | 62 | 268 |
| Q-L22 | `Daq` | Straitness (Edge: obscure root) | ✅ | 0 | 0 | 0 | 0 |
| Q-L23 | `mlk` | King/Kingdom | ✅ | 206 | 35 | 63 | 191 |
| Q-L24 | `smE` | Hear | ✅ | 185 | 53 | 57 | 163 |
| Q-L25 | `bSr` | See/Vision | ✅ | 148 | 45 | 62 | 139 |
| Q-L26 | `xlq` | Create | ✅ | 261 | 54 | 75 | 218 |
| Q-L27 | `Ezz` | Power/Honor | ✅ | 120 | 17 | 48 | 117 |
| Q-L28 | `wHd` | One/Unity | ✅ | 68 | 11 | 35 | 67 |
| Q-O01 | `كتب` | Write/Book | ✅ | 319 | 47 | 61 | 279 |
| Q-O02 | `قول` | Say/Speak | ✅ | 1722 | 109 | 84 | 1383 |
| Q-O03 | `امن` | Believe | ✅ | 879 | 110 | 77 | 723 |
| Q-O04 | `علم` | Knowledge | ✅ | 854 | 116 | 85 | 728 |
| Q-O05 | `سلم` | Peace/Submit | ✅ | 140 | 47 | 48 | 127 |
| Q-O06 | `صبر` | Patience | ✅ | 103 | 38 | 45 | 93 |
| Q-O07 | `حمد` | Praise | ✅ | 68 | 13 | 44 | 66 |
| Q-O08 | `رحم` | Mercy | ✅ | 339 | 53 | 62 | 313 |
| Q-O09 | `صلو` | Prayer | ✅ | 99 | 29 | 37 | 90 |
| Q-O10 | `نصر` | Victory | ✅ | 158 | 74 | 46 | 137 |
| Q-O11 | `حكم` | Wisdom | ✅ | 210 | 45 | 57 | 189 |
| Q-O12 | `صدق` | Truth | ✅ | 155 | 58 | 49 | 144 |
| Q-O13 | `ظلم` | Oppression | ✅ | 315 | 54 | 59 | 290 |
| Q-O14 | `جنن` | Paradise | ✅ | 201 | 28 | 70 | 196 |
| Q-O15 | `نور` | Light | ✅ | 194 | 23 | 62 | 174 |
| Q-E01 | `` | Empty string | ✅ | 0 | 0 | 0 | 0 |
| Q-E02 | `   ` | Whitespace only | ✅ | 0 | 0 | 0 | 0 |
| Q-E03 | `zzzzz` | Non-existent root | ✅ | 0 | 0 | 0 | 0 |
| Q-E04 | `!@#$%` | Special characters | ✅ | 0 | 0 | 0 | 0 |
| Q-E05 | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | Very long input (500+ chars) | ✅ | 0 | 0 | 0 | 0 |
| Q-E06 | `كتب ktb` | Mixed Arabic + Latin | ✅ | 0 | 0 | 0 | 0 |
| Q-E07 | `Allah` | Special term - Allah | ✅ | 2851 | 35 | 86 | 1879 |

### Hebrew OT

| ID | Query | Description | Status | Occurrences | Words | Books | Verses |
|-----|-------|-------------|--------|-------------|-------|-------|--------|
| H-L01 | `kathab` | Write - SBL transliteration | ✅ | 0 | 0 | 0 | 0 |
| H-L02 | `amar` | Say - common verb | ✅ | 0 | 0 | 0 | 0 |
| H-L03 | `elohim` | God - divine name | ❌ | 0 | 0 | 0 | 0 |
| H-L04 | `yhwh` | LORD - Tetragrammaton | ✅ | 6519 | 9 | 36 | 5520 |
| H-L05 | `ahab` | Love - verb | ❌ | 0 | 0 | 0 | 0 |
| H-L06 | `asah` | Do/Make - common verb | ✅ | 0 | 0 | 0 | 0 |
| H-L07 | `nathan` | Give - common verb | ✅ | 0 | 0 | 0 | 0 |
| H-L08 | `dabar` | Speak/Word - key term | ❌ | 0 | 0 | 0 | 0 |
| H-L09 | `shama` | Hear - Shema | ❌ | 0 | 0 | 0 | 0 |
| H-L10 | `raah` | See - common verb | ✅ | 0 | 0 | 0 | 0 |
| H-L11 | `yada` | Know - knowledge | ❌ | 0 | 0 | 0 | 0 |
| H-L12 | `halak` | Walk - lifestyle | ✅ | 0 | 0 | 0 | 0 |
| H-L13 | `amad` | Stand - position | ✅ | 0 | 0 | 0 | 0 |
| H-L14 | `yashab` | Dwell/Sit - settlement | ❌ | 0 | 0 | 0 | 0 |
| H-L15 | `qara` | Call - invocation | ❌ | 0 | 0 | 0 | 0 |
| H-L16 | `yatsa` | Go out - exodus theme | ❌ | 0 | 0 | 0 | 0 |
| H-L17 | `bo` | Come/Enter - movement | ✅ | 2559 | 256 | 39 | 2297 |
| H-L18 | `ebed` | Servant - service | ✅ | 0 | 0 | 0 | 0 |
| H-L19 | `melek` | King - royalty | ✅ | 0 | 0 | 0 | 0 |
| H-L20 | `erets` | Earth/Land - territory | ✅ | 0 | 0 | 0 | 0 |
| H-L21 | `shamayim` | Heaven - cosmology | ❌ | 0 | 0 | 0 | 0 |
| H-L22 | `yom` | Day - time unit | ✅ | 2300 | 61 | 39 | 1928 |
| H-L23 | `ben` | Son - kinship | ✅ | 4928 | 76 | 37 | 3651 |
| H-L24 | `ab` | Father - patriarch | ✅ | 0 | 0 | 0 | 0 |
| H-L25 | `adam` | Man/Adam - humanity | ✅ | 0 | 0 | 0 | 0 |
| H-L26 | `ishshah` | Woman/Wife - female | ✅ | 0 | 0 | 0 | 0 |
| H-L27 | `chesed` | Lovingkindness - covenant love | ❌ | 0 | 0 | 0 | 0 |
| H-L28 | `emeth` | Truth/Faithfulness - reliability | ✅ | 0 | 0 | 0 | 0 |
| H-O01 | `כתב` | Write | ✅ | 225 | 46 | 25 | 212 |
| H-O02 | `אמר` | Say | ✅ | 5302 | 59 | 39 | 4331 |
| H-O03 | `אלהים` | God | ✅ | 2596 | 48 | 35 | 2244 |
| H-O04 | `אהב` | Love | ✅ | 204 | 59 | 28 | 190 |
| H-O05 | `עשה` | Do/Make | ✅ | 2622 | 126 | 39 | 2280 |
| H-O06 | `נתן` | Give | ✅ | 2005 | 126 | 38 | 1811 |
| H-O07 | `דבר` | Speak | ✅ | 1440 | 52 | 34 | 1288 |
| H-O08 | `שמע` | Hear | ✅ | 1155 | 107 | 39 | 1069 |
| H-O09 | `ראה` | See | ✅ | 1293 | 151 | 38 | 1197 |
| H-O10 | `ידע` | Know | ✅ | 933 | 142 | 35 | 867 |
| H-O11 | `הלך` | Walk | ✅ | 504 | 72 | 34 | 470 |
| H-O12 | `עמד` | Stand | ✅ | 521 | 77 | 36 | 494 |
| H-O13 | `ישב` | Dwell | ✅ | 1082 | 133 | 38 | 977 |
| H-O14 | `מלך` | King | ✅ | 2518 | 42 | 35 | 1915 |
| H-O15 | `ארץ` | Earth/Land | ✅ | 2504 | 48 | 39 | 2190 |
| H-E01 | `` | Empty string | ✅ | 0 | 0 | 0 | 0 |
| H-E02 | `   ` | Whitespace only | ✅ | 0 | 0 | 0 | 0 |
| H-E03 | `H99999` | Non-existent Strong's number | ✅ | 0 | 0 | 0 | 0 |
| H-E04 | `!@#$%` | Special characters | ✅ | 0 | 0 | 0 | 0 |
| H-E05 | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | Very long input (500+ chars) | ✅ | 0 | 0 | 0 | 0 |
| H-E06 | `כתב H3789` | Mixed Hebrew + Strong's | ✅ | 225 | 46 | 25 | 212 |
| H-E07 | `G2316` | Greek Strong's in Hebrew search (cross-language) | ✅ | 0 | 0 | 0 | 0 |

### Greek NT

| ID | Query | Description | Status | Occurrences | Words | Books | Verses |
|-----|-------|-------------|--------|-------------|-------|-------|--------|
| G-L01 | `logos` | Word (logos) | ✅ | 330 | 8 | 24 | 318 |
| G-L02 | `theos` | God (theos) | ✅ | 1307 | 8 | 27 | 1148 |
| G-L03 | `agape` | Love (agape) | ✅ | 116 | 4 | 24 | 106 |
| G-L04 | `pistis` | Faith (pistis) | ✅ | 242 | 4 | 24 | 226 |
| G-L05 | `christos` | Christ (christos) | ✅ | 528 | 5 | 26 | 498 |
| G-L06 | `pneuma` | Spirit (pneuma) | ✅ | 379 | 6 | 25 | 344 |
| G-L07 | `kyrios` | Lord (kyrios) | ✅ | 0 | 0 | 0 | 0 |
| G-L08 | `anthropos` | Man (anthropos) | ✅ | 550 | 9 | 24 | 497 |
| G-L09 | `kosmos` | World (kosmos) | ✅ | 185 | 4 | 20 | 150 |
| G-L10 | `aletheia` | Truth (aletheia) | ✅ | 109 | 3 | 23 | 98 |
| G-L11 | `zoe` | Life (zoe) | ✅ | 135 | 3 | 22 | 127 |
| G-L12 | `doxa` | Glory (doxa) | ✅ | 165 | 5 | 23 | 148 |
| G-L13 | `charis` | Grace (charis) | ✅ | 155 | 5 | 23 | 147 |
| G-L14 | `eirene` | Peace (eirene) | ✅ | 91 | 3 | 26 | 84 |
| G-L15 | `dikaiosyne` | Righteousness (dikaiosyne) | ✅ | 91 | 3 | 19 | 86 |
| G-L16 | `hamartia` | Sin (hamartia) | ✅ | 172 | 6 | 20 | 149 |
| G-L17 | `thanatos` | Death (thanatos) | ✅ | 120 | 6 | 15 | 106 |
| G-L18 | `soteria` | Salvation (soteria) | ✅ | 46 | 3 | 16 | 45 |
| G-L19 | `basileia` | Kingdom (basileia) | ✅ | 162 | 3 | 17 | 154 |
| G-L20 | `ekklesia` | Church (ekklesia) | ✅ | 114 | 6 | 17 | 111 |
| G-L21 | `euangelion` | Gospel (euangelion) | ✅ | 75 | 3 | 17 | 72 |
| G-L22 | `apostolos` | Apostle (apostolos) | ✅ | 79 | 7 | 21 | 78 |
| G-L23 | `prophetes` | Prophet (prophetes) | ✅ | 144 | 8 | 15 | 138 |
| G-L24 | `martys` | Witness (martys) | ✅ | 35 | 7 | 13 | 35 |
| G-L25 | `didaskalia` | Teaching (didaskalia) | ✅ | 21 | 4 | 8 | 21 |
| G-L26 | `ergon` | Work (ergon) | ✅ | 169 | 6 | 26 | 157 |
| G-L27 | `kardia` | Heart (kardia) | ✅ | 156 | 6 | 22 | 149 |
| G-L28 | `sarx` | Flesh (sarx) | ✅ | 147 | 6 | 22 | 126 |
| G-O01 | `λόγος` | Word | ✅ | 330 | 8 | 24 | 318 |
| G-O02 | `θεός` | God | ✅ | 1307 | 8 | 27 | 1148 |
| G-O03 | `ἀγάπη` | Love | ✅ | 116 | 4 | 24 | 106 |
| G-O04 | `πίστις` | Faith | ✅ | 242 | 4 | 24 | 226 |
| G-O05 | `χριστός` | Christ | ✅ | 528 | 5 | 26 | 498 |
| G-O06 | `πνεῦμα` | Spirit | ✅ | 379 | 6 | 25 | 344 |
| G-O07 | `κύριος` | Lord | ✅ | 713 | 8 | 23 | 656 |
| G-O08 | `ἄνθρωπος` | Man | ✅ | 550 | 9 | 24 | 497 |
| G-O09 | `κόσμος` | World | ✅ | 185 | 4 | 20 | 150 |
| G-O10 | `ἀλήθεια` | Truth | ✅ | 109 | 3 | 23 | 98 |
| G-O11 | `ζωή` | Life | ✅ | 135 | 3 | 22 | 127 |
| G-O12 | `δόξα` | Glory | ✅ | 165 | 5 | 23 | 148 |
| G-O13 | `χάρις` | Grace | ✅ | 155 | 5 | 23 | 147 |
| G-O14 | `εἰρήνη` | Peace | ✅ | 91 | 3 | 26 | 84 |
| G-O15 | `ἁμαρτία` | Sin | ✅ | 172 | 6 | 20 | 149 |
| G-E01 | `` | Empty string | ✅ | 0 | 0 | 0 | 0 |
| G-E02 | `   ` | Whitespace only | ✅ | 0 | 0 | 0 | 0 |
| G-E03 | `G99999` | Non-existent Strong's number | ✅ | 0 | 0 | 0 | 0 |
| G-E04 | `!@#$%` | Special characters | ✅ | 0 | 0 | 0 | 0 |
| G-E05 | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | Very long input (500+ chars) | ✅ | 0 | 0 | 0 | 0 |
| G-E06 | `λόγος logos` | Mixed Greek + Latin | ✅ | 330 | 8 | 24 | 318 |
| G-E07 | `H430` | Hebrew Strong's in Greek search (cross-language) | ✅ | 0 | 0 | 0 | 0 |

## Failed Tests Detail

### H-L03: `elohim`
- **Source:** hebrew_ot
- **Description:** God - divine name
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L05: `ahab`
- **Source:** hebrew_ot
- **Description:** Love - verb
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L08: `dabar`
- **Source:** hebrew_ot
- **Description:** Speak/Word - key term
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L09: `shama`
- **Source:** hebrew_ot
- **Description:** Hear - Shema
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L11: `yada`
- **Source:** hebrew_ot
- **Description:** Know - knowledge
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L14: `yashab`
- **Source:** hebrew_ot
- **Description:** Dwell/Sit - settlement
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L15: `qara`
- **Source:** hebrew_ot
- **Description:** Call - invocation
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L16: `yatsa`
- **Source:** hebrew_ot
- **Description:** Go out - exodus theme
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L21: `shamayim`
- **Source:** hebrew_ot
- **Description:** Heaven - cosmology
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)

### H-L27: `chesed`
- **Source:** hebrew_ot
- **Description:** Lovingkindness - covenant love
- **Root Found:** None (not_found)
- **Total Occurrence:** 0 (expected: None, diff: 0.0%)
- **Unique Words:** 0 (intersection: 0.0%)
- **Books Count:** 0 (expected: None, diff: 0.0%)
- **Verse Count:** 0 (expected: None, diff: 0.0%)
