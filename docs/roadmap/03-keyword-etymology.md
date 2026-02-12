# Grup 3: Kelime Arama & Etimoloji

## Özet

Mevcut keyword search özelliğini genişletme: etimoloji popup, Türkçe-Arapça öneri, dual mode (AI vs akademik), ve Sami dil bağlantıları.

## Issue Listesi

| # | Başlık | Öncelik | Efor | Durum |
|---|--------|---------|------|-------|
| [#60](https://github.com/aliozdenisik/Clarus/issues/60) | Arapça Kelime Etimoloji Popup | HIGH | 3 gün | ✅ Tamamlandı |
| ~~[#67](https://github.com/aliozdenisik/Clarus/issues/67)~~ | ~~Etimoloji ↔ Kelime Arama Çift Yönlü Navigasyon~~ | ~~MEDIUM~~ | ~~1 gün~~ | ✅ Kapatıldı (aşağıya bak) |
| [#68](https://github.com/aliozdenisik/Clarus/issues/68) | Türkçe → Arapça Kelime Önerisi | MEDIUM | 2 gün | 🔴 Yapılmadı |
| [#70](https://github.com/aliozdenisik/Clarus/issues/70) | Arapça Bilgi Seviyesi Kontrolü | LOW | 2 gün | 🔴 Yapılmadı |
| [#72](https://github.com/aliozdenisik/Clarus/issues/72) | Word Search Dual Mode (AI vs Akademik) | MEDIUM | 2 gün | 🔴 Yapılmadı |
| [#73](https://github.com/aliozdenisik/Clarus/issues/73) | Arapça-İbranice Etimoloji Sözlüğü | LOW | 5 gün | 🔴 Yapılmadı |

---

## Issue Durum Analizi (2026-02-12)

### #67 — Kapatıldı (completed)

İleri yön (Etimoloji → Kelime Arama) zaten implement edilmiş:
- `etymology-popup.tsx` → "Detaylı Analiz" butonu → `/keyword-search/root/{root}` ✅
- `/keyword-search/root/[root]/page.tsx` deep link route'u ✅
- `/api/etymology/{root}` backend endpoint (Redis cache'li) ✅

Ters yön (Kelime Arama → Etimoloji modalı) **gereksiz** bulundu:
- `rich-root-card.tsx` zaten `/api/etymology/{root}` verisini çekip keyword search sayfasında gösteriyor
- Türetilmiş kelimeye tıklayıp etimoloji modalı açmak, kullanıcının zaten baktığı kök bilgisini tekrar sunmak olur (döngüsel UX)

### #68, #70, #72 — Birlikte Planlanmalı

Bu 3 issue arasında güçlü bağımlılık ve örtüşme var. **Ayrı ayrı yapılmamalı, tek bir "Akıllı Keyword Search" paketi olarak planlanmalı.**

#### Bağımlılık Analizi

```
#68 Türkçe → Arapça Önerisi (backend temeli)
 │
 │  #72'nin "AI Destekli" modu = #68'in kendisi
 │
 ▼
#72 Dual Mode (AI vs Akademik)
 │
 │  "Akademik" mod = şu anki mevcut keyword search davranışı
 │  Hangi modun varsayılan olacağı = #70'in sorduğu soru
 │
 ▼
#70 Arapça Bilgi Seviyesi
```

| Gözlem | Sonuç |
|--------|-------|
| #72'nin AI modu = #68'in suggest özelliği | #68 yapılmadan #72'nin AI tarafı çalışamaz |
| #72'nin Akademik modu = mevcut keyword search | Zaten var, sadece sarmalamak lazım |
| #70'in seviye seçimi ≈ #72'nin mod seçimi | `none/basic` → AI mod, `advanced` → Akademik mod |

#### Önerilen Birleşik Uygulama

**Faz 1 — Backend temeli (#68)**
- `POST /api/search/keyword/suggest` endpoint
- Türkçe → Arapça mapping (`qm_words.translation` verisinden çıkarılabilir)
- Bu olmadan diğerleri anlamsız

**Faz 2 — Birleşik UI (#70 + #72)**
- Preferences'a `arabic_proficiency` ekle (none / basic / intermediate / advanced)
- Seviyeye göre keyword search modunu otomatik belirle:
  - `none` / `basic` → AI Destekli mod (Türkçe yaz → öneri al → seç)
  - `intermediate` / `advanced` → Akademik mod (direkt Arapça/Buckwalter)
- Header'da manual override toggle (kullanıcı isterse mod değiştirebilsin)

Bu sayede kullanıcıya hem "Arapça seviyen ne?" hem "Hangi modu istersin?" diye iki ayrı soru sormak yerine, **tek soru** ile ikisini çözmüş olursun.

---

## Güncellenmiş Bağımlılık Grafiği

```
#60 (Etimoloji Popup) ✅ TAMAMLANDI
         │
         ▼
#67 (Çift Yönlü Nav) ✅ KAPATILDI — ileri yön var, ters yön gereksiz

#68 (TR→AR Öneri) ──┐
                    ├──► BİRLEŞİK PAKET: "Akıllı Keyword Search"  # codespell:ignore paket
#70 (Arapça Seviye) ┤    Faz 1: #68 backend
                    │    Faz 2: #70+#72 birleşik frontend
#72 (Dual Mode) ────┘

#73 (AR-HE Sözlük) ◄── bağımsız, en son
```

**Güncellenmiş Sıra:**
1. ~~`#60` - Etimoloji popup~~ ✅ Tamamlandı
2. ~~`#67` - Çift yönlü navigasyon~~ ✅ Kapatıldı
3. `#68` → `#70+#72` — Akıllı Keyword Search paketi (Faz 1: backend, Faz 2: UI)
4. `#73` - AR-HE sözlük (bağımsız, en son)

## Tahmini Toplam Efor (Güncellenmiş)

**~9 gün** (1 geliştirici) — #60 ve #67 tamamlanmış, kalan: #68+#70+#72 birleşik (~4 gün) + #73 (~5 gün)

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

## Agent Prompt (Güncellenmiş)

```
Bu gruptaki kalan issue'ları 2 fazda uygula:

=== FAZ 1: Backend Temeli (#68) ===

1. POST /api/search/keyword/suggest endpoint oluştur
   - Input: Türkçe kelime (ör. "rahmet")
   - Output: Eşleşen Arapça kelimeler + kök + transliterasyon + occurrence count
   - Veri kaynağı: qm_words.translation alanından Türkçe-Arapça mapping çıkar
   - Alternatif: LLM fallback (Gemini 2.5 Flash) + Redis cache
   - ArabicSuggestion schema (Pydantic)

2. Frontend API client'ı güncelle (OpenAPI regenerate)

=== FAZ 2: Birleşik UI (#70 + #72) ===

3. UserPreferences modeline arabic_proficiency ekle (none/basic/intermediate/advanced)
   - Backend: models.py + preferences API + Alembic migration
   - Frontend: preferences-store.ts + settings sayfası

4. Keyword search sayfasını seviyeye göre uyarla:
   - none/basic → AI Destekli mod (Türkçe yaz → suggest API → seçim → arama)
   - intermediate/advanced → Akademik mod (mevcut Arapça/Buckwalter davranışı)
   - Header'da manual mod toggle

5. Mode tercihini persist et (Zustand preferences store, backend sync)

=== AYRI: #73 (bağımsız, en son) ===

6. AR-HE sözlük
   - semitic_roots ve semitic_cognates tabloları
   - Lane's Lexicon + Strong's data import
   - SemiticConnections component
   - Cognate'e tıklayınca ilgili dilde arama

Her faz için test yaz ve commit at.
```

## Kabul Kriterleri Özeti

- [x] #60: Kelimeye tıklayınca popup açılıyor ✅
- [x] #67: Popup→Search navigasyonu çalışıyor (ters yön gereksiz, issue kapatıldı) ✅
- [ ] #68: "rahmet" yazınca Arapça öneriler geliyor
- [ ] #70+#72: Arapça seviyeye göre mod otomatik seçiliyor, manual override var
- [ ] #73: שָׁלוֹם için سَلَام cognate'i gösteriliyor
