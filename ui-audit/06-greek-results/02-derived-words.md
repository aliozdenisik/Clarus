# Derived Words (Türetilmiş Kelimeler) — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

30 tane Yunanca kelime butonu var. Hepsi aynı görsel ağırlıkta, hepsi sıkışık, hepsi kaos. Kullanıcı "gegrammenon mu arıyordum, gegraptai mi?" diye düşünürken gözleri bulanıyor.

**BU BİR WORD CLOUD DEĞİL, BİR MORFOLOJİK REFERANS ARACI.** Ama tasarım word cloud gibi. Kelimeler alfabetik mi, gramatik formlarına göre mi, yoksa rastgele mi sıralanmış — Allah bilir. Gruplandırma yok, hiyerarşi yok, sadece "işte 30 tane buton, uğraş bakalım" mantığı.

"All Words" butonu parlak mavi, diğerleri koyu gri — sanki diğer butonlar tıklanamaz gibi duruyorlar. Hover state'i görselden anlaşılmıyor ama eğer bu contrast seviyesi hover'da da korunuyorsa, kullanıcı "bu tıklanabilir mi?" sorusunu kendine 30 kere soracak.

Sol taraf dar bir kolona hapsedilmiş. Sağ tarafta geniş alan var ama bu 30 buton sol tarafa sıkışmış. **Neden?** Çünkü birisi "sidebar tasarımı" deyip aklını kapatmış.

---

## 2. HEURISTIC ANALİZ

### Visual Hierarchy

**✅ Başarılı:**
- "All Words" butonu aktif durumdayken belirgin (mavi arka plan)

**❌ Başarısız:**
- Diğer 29 buton aynı görsel ağırlıkta, hiçbiri öne çıkmıyor
- Gruplandırma yok (fiil çekimleri, zaman formları, aorist/present/perfect gibi kategoriler görünmüyor)
- Kullanıcı hangi kelimeyi seçeceğini bilemiyor — "choice paralysis" (seçim felci)

### Whitespace (Negatif Alan)

**Yatay Sıkışıklık:**
- Butonlar arası yatay boşluk (gap-x) çok dar, kelimeler birbirine giriyor
- Kelimenin padding'i (px-3 gibi) yetersiz, metinler buton sınırlarına çok yakın

**Dikey Boşluk:**
- Dikey gap (gap-y) yatay gap'den fazla olmalıydı ama burada da yetersiz
- Satır sonları düzensiz (ragged edge), bazı satırlar dolmuş, bazıları yarım kalmış

**Layout Hatası:**
- Sol kenar çubuğu benzeri dar bir kolona hapsedilmiş
- Sağda geniş alan varken 30 kelime sol tarafa sıkışmış
- Sonuç: 30 buton çok uzun bir dikey liste oluşturuyor, kullanıcı scroll yapmak zorunda

### Typography

**Font Boyutu:**
- Yunanca karakterler için font boyutu **çok küçük** (text-sm veya daha küçük)
- Aksan işaretleri (diacritics) bu boyutta birbirine karışıyor — özellikle ὰ, ῆ, ῶ gibi karakterlerde

**Font Ağırlığı:**
- Buton içindeki metinler light/regular ağırlıkta, koyu gri arka plan üzerinde sönük kalıyor
- Uzun süreli okumada göz yorucu

**Case Consistency:**
- Kelimelerin tamamı küçük harf (lowercase)
- Sözlük standardı veya büyük/küçük harf ayrımı gözetilmemiş

### Renk Paleti

**Aktif Buton:**
- Mavi (#3B82F6) arka plan, beyaz metin — kontrast yüksek ✅

**Pasif Butonlar:**
- Koyu gri (#374151 veya benzeri) arka plan, açık gri (#D1D5DB) metin
- Kontrast çok düşük, butonlar "devre dışı" gibi görünüyor
- Hover state'i görselden anlaşılmıyor ama eğer hover'da da bu contrast seviyesi korunuyorsa, UX felaketi

---

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

### ❌ **Choice Paralysis: 30 Buton Kaos**
30 buton aynı görsel ağırlıkta, gruplandırma yok, kullanıcı hangisini seçeceğini bilemiyor.

🔧 **Fix: Kategorilere Ayır**
```tsx
<div className="space-y-6">
  <div>
    <h4 className="text-xs uppercase tracking-wider text-gray-400 mb-2">
      Present Tense
    </h4>
    <div className="flex flex-wrap gap-2">
      <Chip>γράφω</Chip>
      <Chip>γράφεις</Chip>
      <Chip>γράφει</Chip>
    </div>
  </div>

  <div>
    <h4 className="text-xs uppercase tracking-wider text-gray-400 mb-2">
      Aorist
    </h4>
    <div className="flex flex-wrap gap-2">
      <Chip>ἔγραψα</Chip>
      <Chip>ἔγραψας</Chip>
    </div>
  </div>

  {/* Perfect, Passive, vb. */}
</div>
```

### ❌ **Layout Hatası: Sol Tarafa Sıkışık**
30 kelime dar bir kolona hapsedilmiş, sağda geniş alan boşta.

🔧 **Fix: Grid Layout Kullan**
```tsx
<div className="grid grid-cols-3 gap-3">
  {derivedWords.map(word => (
    <Button
      key={word.id}
      variant={selected === word.id ? 'default' : 'ghost'}
      className="justify-start text-left"
    >
      {word.greek}
    </Button>
  ))}
</div>

// Tailwind config:
// grid-cols-3: Üç kolon, geniş alandan faydalanır
// gap-3: 12px boşluk, nefes alır
```

### ❌ **Düşük Kontrast: Pasif Butonlar**
Koyu gri arka plan + açık gri metin = butonlar "devre dışı" gibi görünüyor.

🔧 **Fix: Kontrast Artır**
```tsx
// Pasif butonlar için:
<Button
  variant="ghost"
  className="bg-gray-800 hover:bg-gray-700 text-gray-200"
>
  {word}
</Button>

// Renkler:
// Arka plan: #1F2937 (gray-800)
// Hover: #374151 (gray-700)
// Metin: #E5E7EB (gray-200)
```

### ❌ **Küçük Font Boyutu: Yunanca Aksan İşaretleri**
text-sm veya daha küçük, aksan işaretleri birbirine giriyor.

🔧 **Fix: Font Boyutunu Artır**
```tsx
<Button className="text-base">
  {word.greek}
</Button>

// text-sm (14px) → text-base (16px)
// Yunanca için minimum okunabilir boyut
```

### ❌ **Filtreleme Eksikliği: Manuel Arama**
30+ kelime formu içinde manuel arama yapmak yerine, filtreleme input'u eksik.

🔧 **Fix: Mini Search Input Ekle**
```tsx
<div className="mb-4">
  <Input
    placeholder="Filter forms..."
    value={filter}
    onChange={(e) => setFilter(e.target.value)}
    className="h-9 text-sm"
  />
</div>

<div className="grid grid-cols-3 gap-3">
  {derivedWords
    .filter(w => w.greek.includes(filter))
    .map(word => ...)}
</div>
```

### ❌ **Asymmetrik Scrolling: Sol Liste Uzun**
Sol taraftaki uzun liste, sağ taraftaki ayet sonuçları ile asimetrik bir kaydırma deneyimi yaratıyor.

🔧 **Fix: Sticky Positioning veya Tabs**
```tsx
// Opsiyon 1: Sticky container
<div className="sticky top-4 max-h-[80vh] overflow-y-auto">
  {/* Derived Words butonları */}
</div>

// Opsiyon 2: Tabs yerine Dropdown
<Select value={selectedForm} onValueChange={setSelectedForm}>
  <SelectTrigger>
    <SelectValue placeholder="Select form" />
  </SelectTrigger>
  <SelectContent className="max-h-[400px]">
    {derivedWords.map(word => (
      <SelectItem key={word.id} value={word.id}>
        {word.greek}
      </SelectItem>
    ))}
  </SelectContent>
</Select>
```

---

## 4. REÇETE (Nasıl Görünmeliydi?)

### İdeal Layout (Opsiyon A: Grid):
```
┌────────────────────────────────────────────────────────────┐
│  Derived Words (30 forms)           [Filter: _______]      │
│                                                              │
│  PRESENT TENSE                                               │
│  [γράφω]      [γράφεις]     [γράφει]                       │
│  [γράφομεν]   [γράφετε]     [γράφουσι]                     │
│                                                              │
│  AORIST                                                      │
│  [ἔγραψα]     [ἔγραψας]     [ἔγραψε]                        │
│  [ἐγράψαμεν]  [ἐγράψατε]    [ἔγραψαν]                       │
│                                                              │
│  PERFECT                                                     │
│  [γέγραφα]    [γέγραφας]    [γέγραφε]                       │
└────────────────────────────────────────────────────────────┘
```

### İdeal Layout (Opsiyon B: Dropdown):
```
┌────────────────────────────────────────────────────────────┐
│  Derived Words                                               │
│  ┌──────────────────────────────────────────────┐          │
│  │ [All Words (190)]                        ▼ │          │
│  └──────────────────────────────────────────────┘          │
│  ↓ Click to see:                                            │
│    • Present Tense (6 forms)                                │
│    • Aorist (6 forms)                                       │
│    • Perfect (6 forms)                                      │
│    • Passive (12 forms)                                     │
└────────────────────────────────────────────────────────────┘
```

### Renk Paletine Uyum:
- **Aktif buton:** bg-indigo-600 (#4F46E5), hover:bg-indigo-500
- **Pasif buton:** bg-gray-800 (#1F2937), hover:bg-gray-700, text-gray-200
- **Kategori başlıkları:** text-gray-400, uppercase, text-xs, tracking-wider

---

## 5. PUANLAMA

| Kriter | Puan | Açıklama |
|--------|------|----------|
| **Estetik** | 3/10 | Word cloud gibi görünüyor, hiyerarşi yok. Renk paleti tutarlı ama kontrast düşük. |
| **Kullanılabilirlik** | 2/10 | 30 buton kaos, gruplandırma yok, filtreleme yok, kullanıcı kaybolmuş. |
| **Profesyonellik** | 3/10 | Font boyutu küçük, layout dar bir kolona sıkışmış, asymmetrik scrolling. |
| **Fonksiyonellik** | 4/10 | Butonlar çalışıyor ama choice paralysis yaratıyor, UX optimize edilmemiş. |

**TOPLAM: 3/10**

---

## SONUÇ

Bu bölüm "derived words" değil, "derived chaos". 30 buton aynı görsel ağırlıkta, gruplandırma yok, kullanıcı hangisini seçeceğini bilemiyor. Sol tarafa sıkışık, sağda geniş alan boşta. Font boyutu küçük, aksan işaretleri birbirine giriyor.

**Acil Aksiyonlar:**
1. **Kategorilere ayır** (Present, Aorist, Perfect, Passive)
2. **Grid layout kullan** (3 kolon, gap-3)
3. **Kontrast artır** (pasif butonlar bg-gray-800, text-gray-200)
4. **Font boyutunu artır** (text-sm → text-base)
5. **Filtreleme input ekle** (30+ kelime için)
6. **Sticky positioning** veya **dropdown** kullan (asymmetrik scrolling'i fix et)

Bu tasarım beta'dan kalktığında kullanıcılar "morphology browser" değil "Where's Waldo" oynuyor sanacaklar.
