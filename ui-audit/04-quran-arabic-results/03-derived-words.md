# Kuran Arapça "ktb" Türev Kelimeler Sekmesi — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

Sol sidebar hala dolmuş gibi — morfolojik formlar listesi o kadar basık ki Arapça harflerin harekesi (fetḥa, ḍamma) üstteki satıra temas ediyor. **Line-height diye bir kavram yok mu?** 

Ayet kartlarındaki vurgu rengi felaket: **koyu lacivert highlight üzerinde beyaz metin** — kontrast o kadar düşük ki okumak için zoom yapmak gerekiyor. Tasarımcınız renk körlüğü testinden geçti mi?

Başlık (Al-Baqarah: 53) ile Arapça metin arasında 28px boşluk var, Türkçe meal ile kartın alt sınırı arasında 10px. **Asimetri seviyorsanız müzik değil mimarlık yapın.**

"Accuracy Verification" outline buton, "Total Usage" solid buton. **Karar veremediğiniz şey buton stili mi yoksa hayat seçimleriniz mi?**

Sidebar'ın sağ kenarındaki scrollbar o kadar ince ki (1-2px) kullanıcı fareyle tutamıyor. **Bluetooth mouse'unuz var mı yoksa touchpad'le mi tasarım yapıyorsunuz?**

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Başarılı:** "Morphological Forms" başlığı uppercase ve tracking-wide ile üst hiyerarşide.
- **Başarısız:** "Total Usage" butonu morfolojik form listesinden daha dominant. Buton liste öğesinden daha önemli olamaz.
- **Başarısız:** Alt bölümdeki "319 Total", "47 Unique", "61 Derived" istatistik kutuları çok büyük, ama içindeki rakamlar kutunun tam ortasında değil, aşağı kaymış.

### Whitespace (Negatif Alan)
- **Morfolojik Form Listesi:** Satırlar arası padding 4-6px. Arapça metinlerin harekesi üstteki satıra dokunuyor. **Minimum 12px olmalı.**
- **Ayet Kartları:**
  - Başlık ile Arapça metin arası: 28px (excessive)
  - Arapça metin ile Türkçe meal arası: 16px (ok)
  - Türkçe meal ile kart alt sınırı arası: 10px (insufficient)
  
  **Asimetrik padding = amatör iş.**
- **Sidebar Alt Boşluk:** "Compiling..." göstergesi istatistik kutularına 6px mesafede, üst üste biniyormuş hissi veriyor.

### Typography
- **Arapça Font:** Naskh stili, okunaklı ama line-height yetersiz. Çok satırlı ayetlerde (Al-Baqarah: 79) satırlar birbirine çok yakın.
- **Sidebar Clipping:** Sol paneldeki Arapça kelimelerin sağ tarafında (kelime başlangıçları) çok dar margin var, bazı fontlarda harf çıkıntıları taşabilir.
- **Scrollbar Genişlik:** 1-2px, kullanım zorluğu yaratıyor. Minimum 8px olmalı.

### Renk Paleti
- **Vurgu Rengi Felaketi:** Ayet içindeki türemiş kelimelerin highlight rengi koyu mor/lacivert (`bg-indigo-900` veya `bg-indigo-950`). Beyaz metin bu koyu vurgu içinde boğuluyor. **WCAG AA standardı ihlali.**
- **External Link İkonu:** Çok soluk (text-gray-600?), görünmüyor. Hover state yok.
- **Rozet Renkleri:** Yeşil "Definition", turuncu "Medium". Renk kodlaması sistemi yok.

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **MORFOLOJİK FORM LİSTESİ LINE-HEIGHT**  
Satırlar arası 4-6px, hareke (harfin üstündeki işaretler) üstteki satıra çarpıyor.  
🔧 Fix: `py-3` kullan (12px vertical padding).

```tsx
<div className="flex items-baseline justify-between py-3 border-b border-zinc-800/50">
  <span className="text-sm text-gray-400">(اسم)</span>
  <span className="text-xl font-arabic leading-loose">الْكِتَابُ</span>
</div>
```

❌ **AYET KARTI ASİMETRİK PADDING**  
Üst 28px, alt 10px. Görsel denge yok.  
🔧 Fix: `p-6` kullan (24px her yönde).

```tsx
<Card className="p-6 space-y-4"> {/* pt-7 pb-2.5 değil */}
  <div className="text-sm text-gray-400">Al-Baqarah : 53</div>
  <p className="text-2xl text-right font-arabic leading-loose">...</p>
  <p className="text-sm text-gray-300 leading-6">...</p>
</Card>
```

❌ **VURGU RENGİ KONTRAST KRİZİ**  
Koyu mor highlight, beyaz metin okunmuyor.  
🔧 Fix: Açık mor, 40% opacity kullan.

```tsx
<span className="bg-indigo-600/40 px-1.5 py-0.5 rounded-sm"> {/* bg-indigo-900 değil */}
  كِتَابًا
</span>
```

❌ **ÇOKLU SATIRLI ARAPÇA METINLERDE SATIR ARALIĞI**  
Al-Baqarah: 79'da iki satır birbirine çok yakın.  
🔧 Fix: `leading-loose` (line-height: 2) kullan.

```tsx
<p className="text-2xl text-right font-arabic leading-loose"> {/* leading-normal değil */}
```

❌ **SCROLLBAR ÇOK İNCE**  
1-2px, kullanıcı tutamıyor.  
🔧 Fix: 8px yap, hover'da belirginleştir.

```css
.sidebar::-webkit-scrollbar {
  width: 8px; /* 2px değil */
}

.sidebar::-webkit-scrollbar-thumb {
  background: theme('colors.zinc.700');
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: theme('colors.zinc.600');
}
```

❌ **EXTERNAL LINK İKONU GÖRÜNMÜYOR**  
Text-gray-600, koyu arka planda kaybolmuş.  
🔧 Fix: Text-gray-300, hover'da indigo-400.

```tsx
<ExternalLinkIcon className="w-4 h-4 text-gray-300 hover:text-indigo-400 transition-colors" />
```

❌ **BUTON STİL TUTARSIZLIĞI**  
"Accuracy Verification" outline, "Total Usage" solid.  
🔧 Fix: İkisini de outline yap.

```tsx
<Button variant="outline" className="w-full mb-2">
  Accuracy Verification ↗
</Button>
<Button variant="outline" className="w-full">
  Total Usage ↗
</Button>
```

❌ **İSTATİSTİK KUTULARI DENGESIZ**  
Rakamlar kutunun içinde aşağı kaymış (bottom-heavy).  
🔧 Fix: `flex items-center justify-center` kullan.

```tsx
<div className="flex flex-col items-center justify-center p-4 bg-zinc-900 rounded-lg">
  <span className="text-3xl font-bold">319</span>
  <span className="text-xs text-gray-400 uppercase">Total</span>
</div>
```

❌ **"COMPILING..." SAHİPSİZ**  
İstatistik kutularına 6px mesafede, üst üste biniyormuş hissi.  
🔧 Fix: `mt-6` ekle veya fixed position kullan.

```tsx
<div className="mt-6 flex items-center gap-2 text-sm text-gray-400">
  <Loader2 className="w-4 h-4 animate-spin" />
  Compiling...
</div>
```

❌ **SIDEBAR ARAPÇA KELİME SAĞ MARGIN**  
Kelime başlangıçları sağ kenara çok yakın, harf çıkıntıları taşabilir.  
🔧 Fix: `pr-2` ekle.

```tsx
<div className="pr-2"> {/* Arapça kelime container */}
  <span className="text-xl font-arabic">الْكِتَابُ</span>
</div>
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Sidebar (Morfolojik Formlar)
```
┌────────────────────────────────┐
│  MORPHOLOGICAL FORMS           │ ← 12px, uppercase, mb-4
│                                │
│  (اسم)            الْكِتَابُ   │ ← py-3, leading-loose
│  ────────────────────────────  │ ← Border-b
│  (فعل)            كَتَبَ        │
│  ────────────────────────────  │
│  (اسم)            كَاتِبٌ       │
│                                │
│  [Accuracy Verification ↗]     │ ← Outline, mb-2
│  [Total Usage ↗]               │ ← Outline
│                                │
│  ┌────────┐ ┌────────┐ ┌─────┐│
│  │  319   │ │   47   │ │ 61  ││ ← Centered
│  │  Total │ │ Unique │ │ Der ││
│  └────────┘ └────────┘ └─────┘│
│                                │
│  [Compiling... ⟳]              │ ← mt-6
└────────────────────────────────┘

Scrollbar: 8px, zinc-700
Line-height: leading-loose (2)
Padding: py-3 (12px)
```

### Ayet Kartları
```
┌────────────────────────────────────┐
│  Al-Baqarah : 53          [↗]     │ ← Text-gray-400, 12px
│                                    │ ← 16px gap
│     وَأَنزَلْنَا مَعَهُ الْكِتَابَ   │ ← 24px, right, leading-loose
│                                    │ ← 16px gap
│  And We sent down with him the    │ ← 14px, left, leading-6
│  Book that you may judge...       │
│                                    │
└────────────────────────────────────┘

Padding: 24px (p-6) — uniform
Highlight: bg-indigo-600/40 (koyu değil)
External Link: text-gray-300
Line-height Arabic: leading-loose
Line-height English: leading-6
```

### Renk Paleti
```
Primary: Indigo-600 (#4F46E5)
Highlight: Indigo-600/40 (40% opacity)
Text: Gray-100 (başlık), Gray-300 (body)
Borders: Zinc-800/50
Scrollbar: Zinc-700 (hover: Zinc-600)
```

## 5. PUANLAMA

| Kriter            | Puan | Neden                                                                           |
|-------------------|------|---------------------------------------------------------------------------------|
| Estetik           | 3/10 | Vurgu rengi felaket, asimetrik padding, scrollbar görünmüyor.                  |
| Kullanılabilirlik | 4/10 | Highlight kontrast düşük, line-height yetersiz, external link ikonu soluk.     |
| Profesyonellik    | 3/10 | Buton stil tutarsızlığı, istatistik kutularında hizalama hatası, RTL clipping.|

**TOPLAM: 3.3/10**

---

**SON SÖZ:** Bu ekran bir kitabın sayfalarını yırtıp duvara yapıştırmak gibi — her şey var ama düzen yok. Line-height'ları ikiye katlayın. Vurgu rengini açın. Padding'leri simetrik yapın. Scrollbar'ı kalınlaştırın. External link ikonunu görünür yapın. **O zaman belki 5/10 olur.**
