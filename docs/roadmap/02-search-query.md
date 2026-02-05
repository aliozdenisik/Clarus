# Grup 2: Arama & Query İyileştirmeleri

## Özet

Arama deneyimini geliştiren özellikler: direkt ayet araması, multi-keyword parallel query, ve kullanıcı kontrolü için keyword seçimi.

## Issue Listesi

| # | Başlık | Öncelik | Efor |
|---|--------|---------|------|
| [#52](https://github.com/aliozdenisik/Clarus/issues/52) | Direkt Ayet Araması (Bakara 183) | HIGH | 2 gün |
| [#63](https://github.com/aliozdenisik/Clarus/issues/63) | Multi-Keyword Parallel Query | MEDIUM | 3 gün |
| [#66](https://github.com/aliozdenisik/Clarus/issues/66) | Query Enhancer Keyword Seçimi | MEDIUM | 2 gün |
| [#61](https://github.com/aliozdenisik/Clarus/issues/61) | Farklı Çevirileri Karşılaştırma | LOW | 5 gün |

## Bağımlılık Grafiği

```
#52 (Direkt Ayet) ─────────────────────────────────────┐
                                                       │
#63 (Multi-Keyword) ───► #66 (Keyword Seçimi)          │
                                                       │
#61 (Çeviri Karşılaştırma) ────────────────────────────┘
                                                       │
                                                       ▼
                                            [Arama Deneyimi]
```

**Önerilen Sıra:**
1. `#52` - Direkt ayet araması (bağımsız, hızlı win)
2. `#63` - Multi-keyword (search pipeline değişikliği)
3. `#66` - Keyword seçimi (#63'e bağlı)
4. `#61` - Çeviri karşılaştırma (bağımsız, daha büyük)

## Tahmini Toplam Efor

**12 gün** (1 geliştirici)

## Teknik Notlar

### #52 - Direkt Ayet Araması
```python
# backend/src/reference_parser.py (YENİ)
def parse_reference(query: str) -> Optional[VerseReference]:
    """
    "Bakara 183" → VerseReference(surah=2, ayah=183)
    "John 3:16" → VerseReference(book="John", chapter=3, verse=16)
    """
```

### #63 - Multi-Keyword Query
```python
# backend/src/keyword_extractor.py (YENİ)
def extract_keywords(query: str) -> List[str]:
    """
    "sabır ve namaz" → ["sabır", "namaz"]
    """

# Parallel execution
keywords = extract_keywords(query)
tasks = [search(kw) for kw in keywords]
results = await asyncio.gather(*tasks)
```

### #66 - Keyword Seçimi
```typescript
// frontend/components/search/keyword-selector.tsx (YENİ)
// Chip-based keyword selection UI
```

### #61 - Çeviri Karşılaştırma
- Tanzil.net API entegrasyonu (Kuran çevirileri)
- Yeni `translations` tablosu
- Side-by-side comparison UI

## Agent Prompt

```
Bu gruptaki 4 issue'yu sırayla uygula:

1. ÖNCE #52'yi yap: Reference parser modülü oluştur.
   - Regex patterns: "Bakara 183", "2:183", "John 3:16"
   - Türkçe sure adları mapping (Bakara→2, Fatiha→1)
   - UltimateRAG.search_quran() içinde early return
   - Test: 10+ reference format

2. SONRA #63'ü yap: Multi-keyword extraction ve parallel search.
   - LLM-based keyword extraction (veya rule-based "ve", "and")
   - Her keyword için ayrı search task
   - asyncio.gather ile parallel execution
   - RRF fusion with keyword coverage boost

3. SONRA #66'yı yap: Keyword selection UI.
   - POST /api/search/enhance endpoint (sadece keywords döner)
   - KeywordSelector component (chips)
   - Selected keywords ile arama
   - "Tümünü Seç" / "Hiçbirini Seçme" butonları

4. EN SON #61'i yap: Translation comparison.
   - translations tablosu (source, translation_code, text)
   - Tanzil.net data import script
   - GET /api/translations/{source}/{reference}
   - TranslationComparison component (side-by-side)

Her issue için test yaz ve commit at.
```

## Kabul Kriterleri Özeti

- [ ] #52: "Bakara 183" direkt ayeti getiriyor
- [ ] #63: "sabır ve namaz" → 2 ayrı search, merged results
- [ ] #66: Keyword chips seçilebilir, arama çalışır
- [ ] #61: En az 3 Kuran çevirisi yan yana gösterilir
