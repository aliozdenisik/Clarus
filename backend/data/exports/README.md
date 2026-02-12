# Quran Arabic Roots Etymology Database Export

**Export Date:** 2026-02-12  
**Version:** 1.0  
**Total Roots:** 1,651

## Files

### quran_arabic_roots_lane_lexicon_2026-02-12.json (12 MB)
Complete etymology database in JSON format with:
- 1,337 Lane's Lexicon matches (81%)
- 1,623 Turkish translations (98.3%)
- 1,628 Turkish summaries (98.6%)
- 1,628 English summaries (98.6%)
- Morphological forms for all roots
- Quran frequency data

### quran_arabic_roots_lane_lexicon_2026-02-12.xml (12 MB)
Same data in XML format for legacy systems and XML processing tools.

## Data Coverage

| Field | Coverage | Count |
|-------|----------|-------|
| English Definition (Lane's Lexicon) | 81.0% | 1,337 / 1,651 |
| Turkish Translation (Readable) | 98.3% | 1,623 / 1,651 |
| Turkish Summary | 98.6% | 1,628 / 1,651 |
| English Summary | 98.6% | 1,628 / 1,651 |

## Data Fields (20 per root)

Each root entry contains:

1. **id** - Database ID
2. **root** - Arabic root (e.g., كتب)
3. **root_buckwalter** - Buckwalter transliteration (e.g., ktb)
4. **definition_en** - Full Lane's Lexicon definition (19th century English)
5. **definition_tr** - Readable Turkish translation with expanded abbreviations
6. **summary_tr** - Turkish summary (~120-180 chars)
7. **summary_en** - English summary (~100-150 chars)
8. **semantic_field** - Semantic category (currently null)
9. **morphological_forms** - Array of verb/noun patterns with Quran occurrences
10. **related_roots** - Related roots (currently null)
11. **quran_frequency** - Total occurrences in Quran
12. **source** - "lane" or "corpus_only"
13. **lane_match_type** - "exact", "partial", or "transliteration"
14. **lane_volume** - Lane's Lexicon volume number
15. **confidence** - "high", "medium", or "low"
16. **tr_translation_source** - "llm_gemini"
17. **tr_translation_confidence** - 0.0-1.0 score
18. **created_at** - Creation timestamp
19. **updated_at** - Last update timestamp

## Understanding Lane's Section Codes

You will see codes like **-b2-**, **-A2-**, **-b3-** in the English and Turkish definitions. These are **Lane's original reference system** from 1863:

### Code System

| Code | Meaning | Example |
|------|---------|---------|
| **1, 2, 3...** | Root entry number | `1 كَتَبَهُ` = First root entry |
| **-b2-, -b3-** | **Sub-meanings** | Related variations of the main meaning |
| **-A2-, -A3-** | **New main sense** | Completely different meaning category |

### Example: كتب Root

```
1 كَتَبَهُ          → "He wrote it" (primary meaning)

-b2- كَتَبَ عَنْهُ   → "He wrote what he learned from him"
                     (still about writing - subsection)

-A2- كَتَبَ         → "Allah prescribed/ordained it"
                     (NEW CATEGORY - divine command)

-A3- كَتَبَ         → "He sewed/stitched"
                     (ANOTHER NEW CATEGORY - physical action)
```

### Why Keep These Codes?

✅ **Academic Reference** - Links to original Lane's Lexicon pages  
✅ **Semantic Structure** - Shows relationship between meanings  
✅ **Citation Standard** - Used in scholarly papers

> **Note:** These codes appear in both English (original) and Turkish (preserved for academic accuracy). They help distinguish between minor meaning variations (-b-) and major semantic shifts (-A-).

---

## Key Features

### Readable Turkish Translations

**Before (Original Lane's Lexicon):**
```
(K,) (Msb,) aor. صَبِرَ , inf. n. صَبْرٌ
```

**After (In Export):**
```
Kámoos'a göre, Misbáh'a göre, muzari fiili صَبِرَ (sabira) ve mastarı صَبْرٌ (sabr)
```

Abbreviations expanded:
- (S) → Sihâh'a göre (es-Sıhâh sözlüğüne göre)
- (K) → Kámoos'a göre (el-Kâmûs sözlüğüne göre)
- (TA) → Tâcu'l-Arûs'a göre (en kapsamlı kaynak)
- (Msb) → Misbáh'a göre (el-Misbâhu'l-Münîr sözlüğüne göre)
- aor. → muzari fiil (geniş/şimdiki zaman)
- inf. n. → mastar (fiilin isim hali)

### Morphological Forms

Each root includes morphological analysis:
```json
{
  "form_pattern": "form_I",
  "form_arabic": "فَعَلَ",
  "form_name": "fa'ala",
  "form_category": "فعل ثلاثي مجرد",
  "example_word": "نَّصْبِرَ",
  "occurrences": 80
}
```

## Data Sources & Citations

### Quranic Arabic Corpus v0.4
- **Source:** University of Leeds (GNU GPL)
- **Citation:** Dukes, K. & Habash, N. (2010). "Morphological Annotation of Quranic Arabic." LREC 2010.
- **Data:** 77,429 words, 1,651 unique roots

### Lane's Arabic-English Lexicon
- **Author:** Edward William Lane (1863)
- **Digitized by:** Perseus/Tufts University (GPL-3.0)
- **Coverage:** 47,919 entries, 5,160 roots in PostgreSQL
- **Matches:** 1,337 of 1,651 Quranic roots (81%)

### Turkish Translations
- **Generated via:** Google Gemini 2.5 Flash (OpenRouter)
- **Quality:** Readable modern Turkish with expanded abbreviations
- **Note:** LLM-generated, not manually verified by human scholars
- **Confidence scores:** Included per translation (0.0–1.0)

## License

This derived dataset is GPL-licensed due to source licenses:
- Quranic Arabic Corpus: GNU GPL
- Lane's Lexicon: GPL-3.0
- Derivative work must retain GPL licensing

## Usage Examples

### JSON (JavaScript/Python)
```javascript
// Load the JSON file
const data = require('./quran_arabic_roots_lane_lexicon_2026-02-12.json');

// Access metadata
console.log(data.metadata.statistics);

// Find a specific root
const ktb = data.roots.find(r => r.root === 'كتب');
console.log(ktb.summary_tr); // "كتب (keteb) kelimesi, yazmak..."
```

### XML (XSLT/XPath)
```xml
<!-- XPath query -->
//root[root_arabic='كتب']/summary_tr
```

---

## 📖 Lane Bölüm Kodları Rehberi (Turkish Guide)

Türkçe çevirilerde **-b2-**, **-A2-**, **-b3-** gibi kodlar göreceksiniz. Bunlar **Lane'in 1863'teki orijinal referans sistemi**dir:

### Kod Sistemi

| Kod | Anlamı | Örnek |
|-----|--------|-------|
| **1, 2, 3...** | Kök giriş numarası | `1 كَتَبَهُ` = İlk kök girdisi |
| **-b2-, -b3-** | **Alt anlamlar** | Ana anlamla ilgili varyasyonlar |
| **-A2-, -A3-** | **Yeni ana anlam** | Tamamen farklı anlam kategorisi |

### Örnek: كتب Kökü

```
1 كَتَبَهُ          → "O onu yazdı" (temel anlam)

-b2- كَتَبَ عَنْهُ   → "Ondan öğrendiklerini yazdı"
                     (hala yazma ile ilgili - alt bölüm)

-A2- كَتَبَ         → "Allah onu farz kıldı"
                     (YENİ KATEGORİ - ilahi emir)

-A3- كَتَبَ         → "Dikti, birleştirdi"
                     (BAŞKA YENİ KATEGORİ - fiziksel eylem)
```

### Neden Bu Kodları Koruyoruz?

✅ **Akademik Referans** - Orijinal Lane sözlüğü sayfa atıfları  
✅ **Anlamsal Yapı** - Anlamlar arası ilişkiyi gösterir  
✅ **Bilimsel Standart** - Akademik makalelerde kullanılır

> **Not:** Bu kodlar hem İngilizce (orijinal) hem Türkçede (akademik doğruluk için korunmuş) görünür. Küçük anlam değişimlerini (-b-) ve büyük semantik atlamaları (-A-) ayırt etmeye yardımcı olur.

---

## Contact

For questions or corrections regarding this dataset, please open an issue in the Clarus project repository.

---

**Generated:** 2026-02-12  
**Project:** Clarus - Maximum-accuracy RAG search engine for sacred texts  
**Repository:** https://github.com/aliozdenisik/Clarus
