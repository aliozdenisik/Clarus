# Search Referans ve Tooltip Geliştirme Planı

**Tarih:** 2026-01-28
**Durum:** Onay Bekliyor
**Seçilen Tasarım:** Seçenek A - Tooltip ile Hover Card

---

## 1. Problem Tanımı

### 1.1 Mevcut Sorunlar

| # | Sorun | Etkilenen Alan | Öncelik |
|---|-------|----------------|---------|
| 1 | Bible ayet kartlarında referans gösterilmiyor (Genesis 1:12, John 3:16 vb.) | Search sonuç kartları | Kritik |
| 2 | AI Answer içinde tıklanabilir referans linki yok | AI cevap metni | Kritik |
| 3 | Ayet detayları (verse_details) search endpoint'inde gönderilmiyor | Backend API | Yüksek |
| 4 | Kaynak türü (OT/NT/Apocrypha) badge'i yok | Sonuç kartları | Orta |

### 1.2 Beklenen Davranış (Compare Referans)

Compare sayfası şu özelliklere sahip:
- Her ayet kartında kitap adı, bölüm, ayet numarası görünür
- AI cevabında `[John 3:16]` formatında tıklanabilir referanslar var
- Referansa tıklayınca ilgili ayet kartına scroll yapılır veya yeni sekmede açılır
- Her kaynak için renk kodlu badge (Kuran=yeşil, OT=mavi, NT=turuncu, Apokrifa=mor)

---

## 2. Kök Neden Analizi

### 2.1 Backend Sorunu

**Dosya:** `backend/app/api/stream.py` (satır 145-153)

```python
# Mevcut kod - SORUNLU
results_data.append({
    "source": r.source if hasattr(r, "source") else "quran",
    "reference": r.reference if hasattr(r, "reference") else "",  # ← Boş dönüyor
    "text": r.text if hasattr(r, "text") else str(r),
    "score": r.score if hasattr(r, "score") else 0.0
})
```

**Sorun:** Qdrant sonuçlarında `reference` alanı yok. Alanlar ayrı ayrı mevcut:
- `book_name` = "Genesis"
- `chapter` = 1
- `verse` = 12

Ama bunlar birleştirilip `reference` olarak gönderilmiyor.

### 2.2 Frontend Sorunu

**Dosya:** `frontend/app/search/page.tsx`

- AI Answer düz metin olarak render ediliyor
- `parseCitations()` fonksiyonu kullanılmıyor
- `InlineCitation` bileşeni entegre değil
- `verse_details` state'i yok

---

## 3. Çözüm Mimarisi

### 3.1 Seçenek A: Tooltip ile Hover Card (Seçildi)

```
┌─────────────────────────────────────────────────────────────────┐
│ AI Answer                                                        │
│                                                                  │
│ Verilen ayetler 'evrim' terimini doğrudan tanımlamamaktadır.    │
│ Ancak metinler, yaratılış hakkında şu bilgileri sunar:          │
│ Tanrı insanları yaratılışın başlangıcından itibaren erkek       │
│ ve dişi olarak yaratmıştır [Mark 10:6], [Matthew 19:4].         │
│                          ↑                                       │
│                     hover/click                                  │
│                          ↓                                       │
│              ┌────────────────────────────────┐                  │
│              │ 📖 Mark 10:6                   │                  │
│              │ ─────────────────────────────  │                  │
│              │ "But from the beginning of     │                  │
│              │ the creation God made them     │                  │
│              │ male and female."              │                  │
│              │                                │                  │
│              │ 🏷️ New Testament               │                  │
│              │                                │                  │
│              │ [Ayete Git →]                  │                  │
│              └────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Tooltip Bileşeni Özellikleri

| Özellik | Açıklama |
|---------|----------|
| **Trigger** | Hover (desktop) / Click (mobile) |
| **İçerik** | Referans başlığı, ayet metni (max 200 karakter), kaynak badge'i |
| **Aksiyon** | "Ayete Git" butonu - yeni sekmede açar |
| **Animasyon** | Fade in/out, 150ms delay |
| **Konum** | Otomatik (üst/alt/yan - overflow'a göre) |
| **Stil** | Dark theme, border glow, blur backdrop |

### 3.3 Inline Citation Stili

```css
/* Referans linki stili */
.citation-link {
  color: var(--color-accent-primary);      /* Vurgu rengi */
  text-decoration: underline;
  text-decoration-style: dotted;
  text-underline-offset: 2px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s ease;
}

.citation-link:hover {
  color: var(--color-accent-hover);
  text-decoration-style: solid;
}
```

---

## 4. Uygulama Adımları

### Aşama 1: Backend Düzeltmeleri

#### 1.1 Reference String Oluşturma

**Dosya:** `backend/app/api/stream.py`

**Değişiklik:** `results_data` oluştururken Bible sonuçları için reference formatla

```
Önce: reference = "" (boş)
Sonra: reference = "Genesis 1:12" (formatlanmış)
```

**Mantık:**
```
if source in ["ot", "nt", "apocrypha"]:
    reference = f"{book_name} {chapter}:{verse}"
else:  # quran
    reference = f"{surah_name} {surah_id}:{verse_id}"
```

#### 1.2 verse_details Objesi Ekleme

**Dosya:** `backend/app/api/stream.py`

**Değişiklik:** Compare endpoint'indeki gibi `verse_details` objesi oluştur ve gönder

**Yapı:**
```json
{
  "verse_details": {
    "Genesis 1:12": {
      "text": "And the earth brought forth grass...",
      "book_name": "Genesis",
      "chapter": 1,
      "verse": 12,
      "source": "bible_ot",
      "translation": "King James Version",
      "book_nr": 1
    },
    "John 3:16": {
      "text": "For God so loved the world...",
      "book_name": "John",
      "chapter": 3,
      "verse": 16,
      "source": "bible_nt",
      "translation": "King James Version",
      "book_nr": 43
    }
  }
}
```

**Gönderim sırası:**
1. `{'status': 'searching'}`
2. `{'status': 'found', 'count': N}`
3. `{'verse_details': {...}}`  ← YENİ
4. `{'status': 'generating'}`
5. `{'type': 'token', 'content': '...'}` (tekrarlı)
6. `{'citations': [...]}`
7. `{'type': 'complete', 'result': {...}}`

---

### Aşama 2: Frontend - Tooltip Bileşeni

#### 2.1 Yeni Bileşen: VerseTooltip

**Dosya:** `frontend/components/search/verse-tooltip.tsx`

**Props:**
```typescript
interface VerseTooltipProps {
  reference: string;           // "John 3:16"
  verseDetail: VerseDetail;    // Tam ayet bilgisi
  children: React.ReactNode;   // Trigger element
  onNavigate?: () => void;     // Opsiyonel navigasyon callback
}
```

**Kullanılacak Kütüphane:** Radix UI `@radix-ui/react-tooltip` veya `@radix-ui/react-hover-card`

**Tercih:** HoverCard (daha zengin içerik için uygun)

#### 2.2 Bileşen Yapısı

```
<HoverCard>
  <HoverCardTrigger>
    <InlineCitation reference="John 3:16" />
  </HoverCardTrigger>
  <HoverCardContent>
    <div class="verse-preview">
      <h4>📖 John 3:16</h4>
      <p>"For God so loved the world..."</p>
      <SourceBadge source="bible_nt" />
      <Button>Ayete Git →</Button>
    </div>
  </HoverCardContent>
</HoverCard>
```

---

### Aşama 3: Frontend - Search Page Entegrasyonu

#### 3.1 State Güncellemeleri

**Dosya:** `frontend/app/search/page.tsx`

**Yeni state'ler:**
```typescript
const [verseDetails, setVerseDetails] = useState<Record<string, VerseDetail>>({});
const [highlightedVerse, setHighlightedVerse] = useState<string | null>(null);
```

#### 3.2 SSE Handler Güncelleme

**Mevcut mesaj tipleri:**
- `status`, `token`, `complete`, `error`

**Eklenen mesaj tipi:**
- `verse_details` → `setVerseDetails(message.verse_details)`

#### 3.3 AI Answer Render

**Mevcut:**
```tsx
<p>{streamedAnswer}</p>
```

**Yeni:**
```tsx
<div>
  {parseCitations(streamedAnswer).map((part, i) => {
    if (typeof part === 'string') {
      return <span key={i}>{part}</span>;
    }

    const verse = verseDetails[part.reference];
    return (
      <VerseTooltip
        key={i}
        reference={part.reference}
        verseDetail={verse}
      >
        <InlineCitation reference={part.reference} />
      </VerseTooltip>
    );
  })}
</div>
```

#### 3.4 Sonuç Kartları Güncelleme

**Mevcut:** Basic `GlowCard` with only text and score

**Yeni:** `SourceReferenceCard` benzeri yapı:
- Referans başlığı (bold)
- Kaynak badge'i (renk kodlu)
- Ayet metni
- Skor göstergesi
- Hover highlight efekti

---

### Aşama 4: Navigasyon ve Scroll

#### 4.1 Verse Navigation

**Fonksiyon:** `navigateToVerse(reference: string)`

**Mantık:**
```
1. verse_details'den ayet bilgisini al
2. Kaynak türüne göre URL oluştur:
   - Quran: /quran/{chapter}?verse={verse}
   - Bible: /bible/{bookNr}?chapter={chapter}&verse={verse}
3. window.open(url, '_blank')
```

#### 4.2 Scroll to Card

**Fonksiyon:** `scrollToVerse(reference: string)`

**Mantık:**
```
1. data-verse-id={reference} attribute'u ile element bul
2. scrollIntoView({ behavior: 'smooth', block: 'center' })
3. setHighlightedVerse(reference)
4. 2 saniye sonra highlight'ı kaldır
```

---

## 5. Dosya Değişiklikleri Özeti

| Dosya | İşlem | Açıklama |
|-------|-------|----------|
| `backend/app/api/stream.py` | Düzenle | Reference formatting + verse_details ekleme |
| `frontend/components/search/verse-tooltip.tsx` | Oluştur | Yeni HoverCard bileşeni |
| `frontend/components/search/verse-card.tsx` | Oluştur | Gelişmiş sonuç kartı |
| `frontend/app/search/page.tsx` | Düzenle | State, handler, render güncellemeleri |
| `frontend/lib/utils/parse-citations.ts` | Mevcut | Import edilecek (değişiklik yok) |
| `frontend/components/compare/inline-citation.tsx` | Mevcut | Import edilecek (değişiklik yok) |
| `frontend/components/compare/source-badge.tsx` | Mevcut | Import edilecek (değişiklik yok) |

---

## 6. Bağımlılıklar

### 6.1 Mevcut Kullanılabilir Bileşenler

Bu bileşenler Compare sayfasında zaten mevcut, yeniden kullanılacak:

- `InlineCitation` - Tıklanabilir referans linki
- `SourceBadge` - Renk kodlu kaynak göstergesi
- `parseCitations()` - Metin içinden referans çıkarma

### 6.2 Gerekli Kütüphaneler

| Kütüphane | Durum | Kullanım |
|-----------|-------|----------|
| `@radix-ui/react-hover-card` | Kontrol gerekli | Tooltip/Popover |
| `framer-motion` | Mevcut | Animasyonlar |
| `tailwindcss` | Mevcut | Styling |

---

## 7. Test Senaryoları

### 7.1 Backend Testleri

| Test | Beklenen Sonuç |
|------|----------------|
| OT araması yap | Reference "Genesis X:Y" formatında |
| NT araması yap | Reference "John X:Y" formatında |
| Apocrypha araması yap | Reference "Wisdom X:Y" formatında |
| verse_details içeriği | Tüm alanlar dolu |

### 7.2 Frontend Testleri

| Test | Beklenen Sonuç |
|------|----------------|
| Hover on citation | Tooltip açılır |
| Click "Ayete Git" | Yeni sekmede ayet açılır |
| Mobile tap | Tooltip açılır/kapanır |
| Scroll to verse | Kart highlight olur |
| Citation parsing | [Ref] formatları doğru ayrıştırılır |

---

## 8. Riskler ve Azaltma

| Risk | Olasılık | Etki | Azaltma |
|------|----------|------|---------|
| HoverCard kütüphanesi eksik | Düşük | Orta | Kurulum komutu hazır |
| Qdrant payload'da eksik alan | Orta | Yüksek | Defensive coding, fallback değerler |
| Mobile UX sorunları | Orta | Orta | Touch event'leri ayrı handle et |
| Performance (çok tooltip) | Düşük | Düşük | Lazy loading, virtualization |

---

## 9. Zaman Çizelgesi (Tahmini)

| Aşama | Süre |
|-------|------|
| Aşama 1: Backend düzeltmeleri | - |
| Aşama 2: Tooltip bileşeni | - |
| Aşama 3: Search page entegrasyonu | - |
| Aşama 4: Test ve ince ayar | - |

---

## 10. Onay Kontrol Listesi

- [ ] Plan incelendi
- [ ] Seçenek A (Tooltip) onaylandı
- [ ] Dosya değişiklikleri onaylandı
- [ ] Uygulamaya başlanabilir

---

**Not:** Bu plan, kullanıcı onayı olmadan uygulanmayacaktır.

---

## 11. İkinci Düzeltme: Citation Range Expansion Fix

**Tarih:** 2026-01-28
**Durum:** ✅ Tamamlandı
**Sorun:** Range citations ("Neml:2-4") ve shorthand ("Enfal:2, 9") mavi link olarak görünmüyor

### 11.1 Kök Neden

**Mimari Uyumsuzluk:** Backend ile LLM'in referans formatı arasında mismatch.

```
Backend verse_details keys:     LLM answer text:
  "Neml:2"                       "[Neml:2-4]"
  "Neml:3"                       "[Enfal:2, 9]"
  "Neml:4"
  "Enfal:2"
  "Enfal:9"

Frontend lookup:                 Result:
  verseDetails["Neml:2-4"]  →   undefined ❌
  verseDetails["Enfal:2"]   →   found ✅
  verseDetails["9"]         →   undefined ❌
```

**Problem:**
1. Backend gönderir: Individual verse keys (`"Neml:2"`, `"Neml:3"`, `"Neml:4"`)
2. LLM üretir: Range citations (`"[Neml:2-4]"`) ve shorthand (`"[Enfal:2, 9]"`)
3. parseCitations extracts: `"Neml:2-4"` (single reference)
4. Frontend looks up: `verseDetails["Neml:2-4"]` → NOT FOUND → gray text

### 11.2 Çözüm: Frontend Range Expansion (Seçenek A)

**Avantaj:** Backend değişikliği gerektirmez, hızlı deploy
**Dosya:** `frontend/lib/utils/parse-citations.ts`

**Değişiklikler:**

1. **`expandRangeReference(ref: string): string[]`**
   - "Neml:2-4" → ["Neml:2", "Neml:3", "Neml:4"]
   - Range regex: `/^(.+):(\d+)-(\d+)$/`
   - Validation: start <= end, start >= 1

2. **`expandCommaReferences(citations: string[]): string[]`**
   - "Enfal:2, 9" → ["Enfal:2", "Enfal:9"]
   - Tracks last surah name
   - Prepends surah to bare numbers

3. **Updated `parseCitations(content: string): CitationPart[]`**
   - Expands all citations before creating parts
   - Returns individual verses as separate citation objects
   - Preserves brackets and commas as string parts

**Output örneği:**
```typescript
// Input: "[Neml:2-4]"
// Output: [
//   "[",
//   { type: 'citation', reference: 'Neml:2' },
//   ", ",
//   { type: 'citation', reference: 'Neml:3' },
//   ", ",
//   { type: 'citation', reference: 'Neml:4' },
//   "]"
// ]
```

### 11.3 Implementation Summary

**Files Modified:**
- ✅ `frontend/lib/utils/parse-citations.ts` - Added expansion logic
- ✅ `frontend/app/search/page.tsx` - No changes needed (already handles expanded arrays)
- ✅ `frontend/app/compare/page.tsx` - No changes needed (already handles expanded arrays)

**Test Results:**
```bash
✅ "Neml:2-4" → ["Neml:2", "Neml:3", "Neml:4"]
✅ "Enfal:2, 9" → ["Enfal:2", "Enfal:9"]
✅ "Bakara:45" → ["Bakara:45"] (single citation)
✅ "Bakara:1, 2, 3" → ["Bakara:1", "Bakara:2", "Bakara:3"]
✅ Multiple citations in same text work correctly
```

**Lines of Code:** ~120 lines in parse-citations.ts
**Build Status:** ✅ No TypeScript errors
**Deployment:** Ready for production

### 11.4 Why Existing Render Logic Didn't Need Changes

Both `search/page.tsx` and `compare/page.tsx` already handle mixed arrays of strings and citation objects:

```typescript
parseCitations(text).map((part, i) => {
  if (typeof part === 'string') {
    return <span key={i}>{part}</span>;  // Brackets, commas, text
  }
  // Citation object - lookup and render
  const verse = verseDetails[part.reference];
  return verse ? <VerseTooltip>...</VerseTooltip> : <span>...</span>;
})
```

**Key insight:** parseCitations now returns individual citations that match verse_details keys → existing lookup logic "just works"™

### 11.5 Edge Cases Handled

- ✅ Invalid ranges (start > end): Return as-is
- ✅ Missing surah in comma list: Keep as-is
- ✅ Single digit without context: Keep as-is
- ✅ Mixed ranges and singles: Both work
- ✅ Multiple ranges in one text: All expand correctly

### 11.6 Performance Impact

**Negligible:** Expansion happens once during parsing, adds ~O(n) where n = verses in range (typically 2-5).

### 11.7 Future Improvements

- **Backend optimization:** Pre-compute range keys in verse_details for even faster lookup
- **Visual indicator:** Show range citations as grouped instead of comma-separated
- **LLM prompt tuning:** Reduce range usage if causing issues

---

**Status:** ✅ Deployed and tested. All citations now render as clickable blue links.
