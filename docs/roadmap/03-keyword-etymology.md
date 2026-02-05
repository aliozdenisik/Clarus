# Grup 3: Kelime Arama & Etimoloji

## Özet

Mevcut keyword search özelliğini genişletme: etimoloji popup, Türkçe-Arapça öneri, dual mode (AI vs akademik), ve Sami dil bağlantıları.

## Issue Listesi

| # | Başlık | Öncelik | Efor |
|---|--------|---------|------|
| [#60](https://github.com/aliozdenisik/Clarus/issues/60) | Arapça Kelime Etimoloji Popup | HIGH | 3 gün |
| [#67](https://github.com/aliozdenisik/Clarus/issues/67) | Etimoloji ↔ Kelime Arama Çift Yönlü Navigasyon | MEDIUM | 1 gün |
| [#68](https://github.com/aliozdenisik/Clarus/issues/68) | Türkçe → Arapça Kelime Önerisi | MEDIUM | 2 gün |
| [#70](https://github.com/aliozdenisik/Clarus/issues/70) | Arapça Bilgi Seviyesi Kontrolü | LOW | 2 gün |
| [#72](https://github.com/aliozdenisik/Clarus/issues/72) | Word Search Dual Mode (AI vs Akademik) | MEDIUM | 2 gün |
| [#73](https://github.com/aliozdenisik/Clarus/issues/73) | Arapça-İbranice Etimoloji Sözlüğü | LOW | 5 gün |

## Bağımlılık Grafiği

```
#60 (Etimoloji Popup) ◄───────────────────────────────┐
         │                                            │
         ▼                                            │
#67 (Çift Yönlü Nav) ────────────────────────────────►│
                                                      │
#68 (TR→AR Öneri) ───► #72 (Dual Mode) ───────────────┤
                                                      │
#70 (Arapça Seviye) ──────────────────────────────────┤
                                                      │
#73 (AR-HE Sözlük) ◄──────────────────────────────────┘
         │
         ▼
   [Etymology Hub]
```

**Önerilen Sıra:**
1. `#60` - Etimoloji popup (temel altyapı)
2. `#67` - Çift yönlü navigasyon (#60'a bağlı)
3. `#68` - TR→AR öneri (ayrı özellik)
4. `#72` - Dual mode (#68 ile birlikte çalışır)
5. `#70` - Arapça seviye (user preference)
6. `#73` - AR-HE sözlük (en büyük, en son)

## Tahmini Toplam Efor

**15 gün** (1 geliştirici)

## Teknik Notlar

### Paylaşılan Bileşenler
```
frontend/components/keyword-search/
├── etymology-popup.tsx      (#60)
├── etymology-modal.tsx      (#67)
├── arabic-suggestion.tsx    (#68)
├── mode-selector.tsx        (#72)
└── proficiency-adapter.tsx  (#70)

frontend/components/etymology/
└── semitic-connections.tsx  (#73)
```

### Veri Kaynakları
| Issue | Veri |
|-------|------|
| #60 | Mevcut `qm_words` tablosu |
| #68 | Yeni `tr_arabic_mapping.json` veya LLM |
| #73 | Lane's Lexicon + Strong's + custom |

### API Endpoints
```python
# Yeni endpoints
GET  /api/etymology/{word}           # #60
POST /api/search/keyword/suggest     # #68
GET  /api/etymology/semitic/{word}   # #73
```

## Agent Prompt

```
Bu gruptaki 6 issue'yu sırayla uygula:

1. ÖNCE #60'ı yap: Etimoloji popup.
   - GET /api/etymology/{word} endpoint
   - Response: root, transliteration, meaning, morphological_form, occurrences
   - Frontend: ArabicWordPopup component
   - Ayet sayfasında kelimelere tıklanabilirlik
   - Framer Motion ile popup animasyonu

2. SONRA #67'yi yap: Çift yönlü navigasyon.
   - Popup'ta "Bu kökü ara" butonu → /keyword-search?root=X
   - Keyword search'te kelimeye tıklayınca → EtymologyModal
   - Deep link support

3. SONRA #68'i yap: Türkçe → Arapça öneri.
   - POST /api/search/keyword/suggest endpoint
   - tr_arabic_mapping.json (veya LLM fallback)
   - ArabicSuggestion component (radio buttons)
   - "Tümünü Ara" seçeneği

4. SONRA #72'yi yap: Dual mode.
   - ModeSelector component (AI Destekli | Akademik)
   - LocalStorage'da tercih kaydet
   - AI mode: #68'deki öneri sistemi
   - Akademik mode: Direkt arama, YZ yok

5. SONRA #70'i yap: Arapça seviye kontrolü.
   - UserPreferences'a arabic_proficiency ekle
   - Onboarding'de veya settings'te seç
   - Keyword search UI adaptasyonu (input mode, display format)

6. EN SON #73'ü yap: AR-HE sözlük.
   - semitic_roots ve semitic_cognates tabloları
   - Lane's Lexicon + Strong's data import
   - SemiticConnections component
   - Cognate'e tıklayınca ilgili dilde arama

Her issue için test yaz ve commit at.
```

## Kabul Kriterleri Özeti

- [ ] #60: Kelimeye tıklayınca popup açılıyor
- [ ] #67: Popup→Search ve Search→Modal navigasyonu çalışıyor
- [ ] #68: "rahmet" yazınca Arapça öneriler geliyor
- [ ] #72: AI/Akademik mod seçimi var ve çalışıyor
- [ ] #70: Arapça seviyeye göre UI değişiyor
- [ ] #73: שָׁלוֹם için سَلَام cognate'i gösteriliyor
