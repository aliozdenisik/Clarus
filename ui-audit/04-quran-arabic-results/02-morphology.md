# Kuran Arapça "ktb" Morfoloji Sekmesi — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

Split-pane layout kullanmışsınız ama sol panel Tetris oyunu gibi: kök, istatistikler, rozetler, butonlar, morfolojik formlar — hepsi 320px'lik dar bir alana tıkıştırılmış. Scrollbar sağdaki ayraç çizgisiyle **ÇARPIŞIYOR**. Bu ne, drift yarışı mı?

Ana içerik alanında ayet kartları var ama her kart farklı bir hizalama sistemi kullanıyor: başlık solda, Arapça sağda, Türkçe meal solda. Kullanıcının gözü **zigzag çiziyor**. Bir karar verin: LTR mi, RTL mi, ikisi de mi?

"Accuracy Verification" ve "Total Usage" butonları farklı stillerde — biri outline, biri solid. **Hangi sistem tasarımcı bunu onayladı?** İki buton aynı sidebar'da ama farklı düğün salonlarından gelmiş gibi.

Morfolojik form listesindeki satırlar basık, harfler birbirine temas ediyor. Arapça harflerin harekeri (fetḥa, ḍamma) üstteki satıra çarpacak. **Line-height diye bir şey duydunuz mu?**

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Başarılı:** "ROOT INFORMATION" başlığı uppercase ve küçük punto ile hiyerarşinin üstünde konumlanmış.
- **Başarısız:** "Accuracy Verification" butonu morfolojik form listesinden daha büyük ve daha vurgulu. Aslında form listesi ana içerik olmalıydı.
- **Başarısız:** Sidebar'ın en altındaki istatistik kutuları (319, 47, 61) kartın alt sınırına yapışmış, nefes alamıyor.

### Whitespace (Negatif Alan)
- **Sidebar Padding:** Sol kartın iç kenar boşlukları 12-16px civarında. Profesyonel standart 24-32px.
- **Satır Aralıkları:** Morfolojik form listesindeki satırlar arası dikey padding 4-6px. **Bu ne, Terminal ekranı mı?** Minimum 12px olmalı.
- **Buton Padding:** "Accuracy Verification" ve "Total Usage" butonları horizontal padding ile genişletilmiş, sidebar'ı zorluyor. İçeriği sidebar'a uydurmak yerine sidebar'ı içeriğe uydurmuşsunuz.
- **Ayet Kartları:** Başlık (Al-Hadid: 25) ile Arapça metin bloğu arası boşluk 24px, Türkçe meal ile kartın alt sınırı arası 12px. **Asimetrik.**

### Typography
- **Fontlar:** Arapça için Naskh stili, Latin için modern sans-serif. Okunaklı.
- **Font Ağırlıkları:** "319 Occurrences" medium, "Definition" semi-bold. **Tutarsızlık.**
- **Morfoloji Listesi:** Parantez içindeki etiketler `(اسم)` ile Arapça kelimeler aynı baseline'da değil. Arapça metinler yukarı kaymış.

### Renk Paleti
- **Tema:** Koyu (black/zinc-950) zemin, mor (indigo-600) aksan.
- **Rozet Kaosu:**
  - Yeşil (#10B981 - "Definition")
  - Turuncu (#F59E0B - "Medium")
  - Mor (indigo-600 - butonlar, tab indicator)

  **3 farklı aksan rengi sidebar'da.** "Definition" niye yeşil? "Medium" niye turuncu? Renk kodlaması sistemi yok.
- **Vurgu Rengi:** Ayet kartlarındaki Arapça kelimelerin highlight rengi koyu mor (indigo-900?). Beyaz metin bu koyu vurgu içinde boğuluyor, kontrast düşük.

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **SCROLLBAR BORDER'A ÇARPIYOR**  
Sidebar scrollbar'ı sağdaki ayraç çizgisiyle çakışıyor. Görsel karmaşa.  
🔧 Fix: Scrollbar'ı border'dan 4px içeri kaydır veya border'ı scrollbar genişliği kadar sola taşı.

```css
.sidebar {
  padding-right: 12px; /* scrollbar için alan */
  border-right: 1px solid theme('colors.zinc.800');
}

.sidebar::-webkit-scrollbar {
  width: 8px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: theme('colors.zinc.700');
  border-radius: 4px;
}
```

❌ **MORFOLOJİK FORM LİSTESİ BASIK**  
Satırlar arası padding 4-6px, Arapça harflerin harekeri birbirine temas ediyor.  
🔧 Fix: `py-3` (12px vertical padding) kullan.

```tsx
<div className="flex items-center justify-between py-3"> {/* py-1.5 değil */}
  <span className="text-gray-400 text-sm">(اسم)</span>
  <span className="text-xl font-arabic">الْكِتَابُ</span>
</div>
```

❌ **BUTON STİL TUTARSIZLIĞI**  
"Accuracy Verification" outline, "Total Usage" solid. Aynı sidebar'da.  
🔧 Fix: İkisini de outline yap.

```tsx
<Button variant="outline" className="w-full">
  Accuracy Verification ↗
</Button>
<Button variant="outline" className="w-full">
  Total Usage ↗
</Button>
```

❌ **ROZET RENK KAOSU**  
Yeşil "Definition", turuncu "Medium". Renk kodlaması sistemi yok.  
🔧 Fix: Hepsini mor yap.

```tsx
<Badge className="bg-indigo-600">Definition</Badge>
<Badge className="bg-indigo-400">Medium</Badge>
```

❌ **AYET KARTI ASİMETRİK PADDING**  
Üst padding 24px, alt padding 12px.  
🔧 Fix: `p-6` kullan (24px her yönde).

```tsx
<Card className="p-6"> {/* pt-6 pb-3 değil */}
```

❌ **AYET İÇİNDE VURGU KONTRASTI DÜŞÜK**  
Koyu mor highlight, beyaz metin boğuluyor.  
🔧 Fix: Daha açık mor kullan (`bg-indigo-600/40` gibi).

```tsx
<span className="bg-indigo-600/40 px-1 rounded"> {/* bg-indigo-900 değil */}
  كِتَابٌ
</span>
```

❌ **SIDEBAR ALT İSTATİSTİKLER SIKIŞIK**  
"319", "47", "61" kutuları kartın alt sınırına yapışmış.  
🔧 Fix: `mb-6` ekle.

```tsx
<div className="grid grid-cols-3 gap-2 mb-6"> {/* mb-2 değil */}
```

❌ **EXTERNAL LINK İKONU ÇOK SİLİK**  
Ayet kartlarındaki dış link ikonu soluk gri, görünmüyor.  
🔧 Fix: `text-gray-400` yerine `text-gray-300` veya hover'da `text-indigo-400`.

```tsx
<ExternalLinkIcon className="w-4 h-4 text-gray-300 hover:text-indigo-400" />
```

❌ **MORFOLOJİ LİSTESİ BASELINE HİZALAMASI**  
Parantezli etiket ile Arapça kelime aynı baseline'da değil.  
🔧 Fix: `items-baseline` kullan.

```tsx
<div className="flex items-baseline justify-between py-3"> {/* items-center değil */}
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Sidebar (Sol Panel)
```
┌────────────────────────────────┐
│  ROOT INFORMATION              │ ← 12px, uppercase
│                                │
│  كتب                           │ ← 48px, center
│  (keteb - to write)            │ ← 14px, center
│                                │
│  ┌──────────┐ ┌──────────────┐│
│  │ 319      │ │ Definition   ││
│  └──────────┘ └──────────────┘│
│                                │
│  [Medium]                      │ ← Badge
│                                │
│  MORPHOLOGICAL FORMS           │ ← 12px, mb-4
│                                │
│  (اسم)            الْكِتَابُ   │ ← py-3, items-baseline
│  (فعل)            كَتَبَ        │
│  (اسم)            كَاتِبٌ       │
│                                │
│  [Accuracy Verification ↗]     │ ← Outline, mb-4
│  [Total Usage ↗]               │ ← Outline
│                                │
│  ┌────┐ ┌────┐ ┌────┐         │
│  │319 │ │ 47 │ │ 61 │         │ ← mb-6
│  └────┘ └────┘ └────┘         │
└────────────────────────────────┘

Padding: 24px (p-6)
Scrollbar: 8px, 4px içeride
Border: 1px solid zinc-800, scrollbar'ın sağında
```

### Ayet Kartları
```
┌────────────────────────────────────┐
│  Al-Hadid : 25            [↗]     │ ← Başlık, 12px, gray-400
│                                    │ ← 16px gap
│         أَنزَلْنَا مَعَهُمُ الْكِتَابَ │ ← Arapça, 24px, right
│                                    │ ← 12px gap
│  We sent down with them the Book  │ ← İngilizce, 14px, left
│                                    │
└────────────────────────────────────┘

Padding: 24px (p-6)
Highlight: bg-indigo-600/40 (koyu mor değil)
External Link: text-gray-300
```

### Renk Paleti (Unified)
```
Primary: Indigo-600 (#4F46E5)
Secondary: Indigo-400 (#818CF8)
Text: Gray-100 (başlıklar), Gray-300 (body)
Borders: Zinc-800
Highlights: Indigo-600/40 (40% opacity)
```

## 5. PUANLAMA

| Kriter            | Puan | Neden                                                                      |
|-------------------|------|----------------------------------------------------------------------------|
| Estetik           | 3/10 | Scrollbar çarpışması, rozet renk kaosu, asimetrik padding.                |
| Kullanılabilirlik | 4/10 | Morfoloji listesi basık, vurgu kontrast düşük, buton stil tutarsızlığı.   |
| Profesyonellik    | 3/10 | Sidebar tıkış tıkış, line-height hatası, external link ikonu görünmüyor.  |

**TOPLAM: 3.3/10**

---

**SON SÖZ:** Bu ekran bir dolaba çamaşır tıkıştırmak gibi — her şey var ama hiçbir şey rahat değil. Sidebar'ı rahatlatın. Scrollbar'ı border'dan ayırın. Satır aralıklarını ikiye katlayın. Buton stillerini birleştirin. Rozet renklerini tek aksan rengine indirgeyin. **O zaman belki 5/10 olur.**
