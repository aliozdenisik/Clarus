# İbranice "H3789" Ayet Kartları — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

İbranice metin çok büyük (24px+), İngilizce çeviri çok küçük (13-14px). **Hiyerarşi doğru ama orantısız.** İbranice metinde nikkud (sesli harfler) ve cantillation marks (vurgu işaretleri) var, bu iyi — ama iki satırlı İbranice bloklarda satırlar birbirine çok yakın. Üstteki satırın altındaki nikkud, alttaki satırın üstündeki harflere **temas ediyor**.

Vurgu rengi (highlight) mor kutucuk, ama kutu içindeki İbranice harfler çok sıkışık. Horizontal padding 2-4px, harfler nefes alamıyor. **Claustrophobic design.**

Referans (Exodus 17:14) çok soluk (text-gray-600?), koyu arka planda kaybolmuş. Kullanıcı hangi ayeti okuduğunu anlamak için zoom yapmalı.

"Verse Results" başlığı merkezli, ama kartlar içinde başlık (Exodus 17:14) solda, İbranice sağda, İngilizce solda. **Zigzag göz hareketi.** Kullanıcının gözü ping-pong oynuyor.

Sol kenarda mavi dikey accent bar var (focused card indicator), ama hangi kart aktif/seçili belli değil. Tüm kartlar aynı görünüyor.

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Başarılı:** İbranice metin en büyük punto (24px), merkezi odak noktası.
- **Başarısız:** Referans (Exodus 17:14) çok küçük ve soluk, hiyerarşinin dibinde.
- **Başarısız:** "Verse Results" başlığı merkezli ama kartlar soldan hizalı. Görsel denge yok.

### Whitespace (Negatif Alan)
- **Başlık-İbranice Arası:** Referans ile İbranice metin arası 16px, ok.
- **İbranice-İngilizce Arası:** İbranice ile İngilizce çeviri arası 12px, biraz dar. 16px olmalı.
- **Horizontal Rule:** İbranice ve İngilizce arasında çok soluk bir yatay çizgi var (opacity: 0.05?), neredeyse görünmüyor.
- **Kart İç Padding:** Sol ve sağ padding 20px, üst ve alt padding 16px. **Asimetrik.**

### Typography
- **İbranice Font:** Serif font, tam nikkud ve cantillation marks ile. Font-size 24px, okunaklı.
- **Line-Height Hatası:** İki satırlı İbranice bloklarda (Exodus 17:14) satırlar arası line-height çok dar. Üstteki satırın altındaki nikkud, alttaki satırın harflerine temas ediyor.
- **İngilizce Font:** Sans-serif, 13-14px, clean ama text-gray-300 rengi biraz soluk.
- **Referans Typography:** Text-gray-600, 12px. Çok düşük kontrast, WCAG AA standardı altında.

### Renk Paleti
- **Tema:** Koyu (black/zinc-950) zemin, mor (indigo-600) aksan.
- **Vurgu Rengi:** Mor highlight box (`bg-indigo-600` veya `bg-indigo-700`), rounded corners. İyi ama padding yetersiz.
- **Accent Bar:** Sol kenarda mavi dikey bar (indigo-500), focused card indicator olmalı ama tüm kartlarda var gibi görünüyor.

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **İBRANİCE SATIR ARALIĞI (LINE-HEIGHT) ÇOK DAR**  
Exodus 17:14'te iki satır İbranice metin var, satırlar birbirine çok yakın. Nikkud ve cantillation marks overlap ediyor.  
🔧 Fix: `leading-loose` (line-height: 2) kullan.

```tsx
<p className="text-2xl font-hebrew text-right leading-loose"> {/* leading-normal değil */}
  וַיֹּ֨אמֶר יְהוָ֜ה אֶל־מֹשֶׁ֗ה כְּתֹ֨ב זֹ֤את זִכָּרוֹן֙
</p>
```

❌ **VURGU KUTUSU (HIGHLIGHT) PADDING YETERSİZ**  
Mor highlight box içinde İbranice karakterler çok sıkışık, horizontal padding 2-4px.  
🔧 Fix: `px-2 py-0.5` kullan (8px yatay, 2px dikey).

```tsx
<span className="bg-indigo-600/50 px-2 py-0.5 rounded-md"> {/* px-1 değil */}
  כָּתַב
</span>
```

❌ **REFERANS (VERSE NUMBER) ÇOK SOLUK**  
"Exodus 17:14" text-gray-600, koyu arka planda kontrast yetersiz.  
🔧 Fix: `text-gray-400` kullan.

```tsx
<div className="text-sm text-gray-400"> {/* text-gray-600 değil */}
  Exodus 17:14
</div>
```

❌ **KART PADDING ASİMETRİK**  
Sol/sağ 20px, üst/alt 16px.  
🔧 Fix: `p-6` kullan (24px her yönde).

```tsx
<Card className="p-6"> {/* px-5 py-4 değil */}
```

❌ **İBRANİCE VE İNGİLİZCE ARASI BOŞLUK**  
12px, biraz dar.  
🔧 Fix: `space-y-4` kullan (16px).

```tsx
<Card className="p-6 space-y-4"> {/* space-y-3 değil */}
```

❌ **YATAY ÇİZGİ (SEPARATOR) GÖRÜNMÜYOR**  
İbranice ve İngilizce arasında çok soluk bir çizgi var, opacity çok düşük.  
🔧 Fix: Opacity'yi artır veya border kullan.

```tsx
<div className="border-t border-zinc-800 my-4"></div>
```

Ya da:
```tsx
<hr className="border-zinc-800 opacity-30" /> {/* opacity-5 değil */}
```

❌ **"VERSE RESULTS" MERKEZLİ, KARTLAR SOLDAN**  
Başlık center, kartlar left-aligned. Görsel denge yok.  
🔧 Fix: Başlığı da sola al.

```tsx
<h2 className="text-xl font-semibold text-left mb-6"> {/* text-center değil */}
  Verse Results
</h2>
```

❌ **ACCENT BAR BELİRSİZ**  
Sol kenardaki mavi bar tüm kartlarda var gibi görünüyor, hangisi aktif/seçili belli değil.  
🔧 Fix: Sadece hover veya selected state'te göster.

```tsx
<Card className="relative group">
  <div className="absolute left-0 top-0 bottom-0 w-1 bg-indigo-500 rounded-l-lg opacity-0 group-hover:opacity-100 transition-opacity"></div>
</Card>
```

❌ **ALIGNMENT DISCORD (ZİGZAG GÖZ HAREKETİ)**  
Referans solda, İbranice sağda, İngilizce solda. Kullanıcının gözü sağa-sola sıçrıyor.  
🔧 Fix: Referansı sağa al (RTL için doğal), İngilizce'yi solda bırak.

```tsx
<div className="flex justify-between items-start mb-4">
  <div className="text-sm text-gray-400">Exodus 17:14</div>
  <ExternalLinkIcon className="w-4 h-4 text-gray-300" />
</div>
```

Veya referansı İbranice metnin hizasına al:
```tsx
<div className="text-sm text-gray-400 text-right mb-4">
  Exodus 17:14
</div>
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Ayet Kartı
```
┌────────────────────────────────────────────┐
│  Exodus 17:14                      [↗]     │ ← Text-gray-400, 12px, solda
│                                            │ ← 16px gap
│        וַיֹּ֨אמֶר יְהוָ֜ה אֶל־מֹשֶׁ֗ה         │ ← 24px, right, leading-loose
│        כְּתֹ֨ב זֹ֤את זִכָּרוֹן֙              │ ← Line-height: 2
│                                            │
│  ─────────────────────────────────────     │ ← Border-zinc-800, opacity-30
│                                            │ ← 16px gap
│  And the LORD said unto Moses, Write      │ ← 14px, left, text-gray-300
│  this for a memorial in a book...         │
│                                            │
└────────────────────────────────────────────┘

Padding: 24px (p-6) — uniform
Highlight: bg-indigo-600/50, px-2 py-0.5
External Link: text-gray-300, hover:text-indigo-400
Separator: border-t border-zinc-800, my-4
Accent Bar: left-0, w-1, opacity-0, group-hover:opacity-100
```

### Vurgu Kutusu (Highlight Box)
```tsx
<span className="bg-indigo-600/50 px-2 py-0.5 rounded-md">
  כָּתַב
</span>

Background: bg-indigo-600/50 (50% opacity)
Padding: px-2 (8px), py-0.5 (2px)
Border-radius: rounded-md (6px)
```

### İbranice Metin Line-Height
```tsx
<p className="text-2xl font-hebrew text-right leading-loose">
  {/* leading-loose = line-height: 2 */}
</p>
```

### Referans Kontrast
```tsx
<div className="text-sm text-gray-400"> {/* text-gray-600 değil */}
  Exodus 17:14
</div>
```

### Başlık Hizalama
```tsx
<h2 className="text-xl font-semibold text-left mb-6"> {/* text-center değil */}
  Verse Results
</h2>
```

## 5. PUANLAMA

| Kriter            | Puan | Neden                                                                           |
|-------------------|------|---------------------------------------------------------------------------------|
| Estetik           | 4/10 | Line-height overlap, highlight padding yetersiz, accent bar belirsiz.          |
| Kullanılabilirlik | 5/10 | Referans soluk, zigzag göz hareketi, separator görünmüyor.                    |
| Profesyonellik    | 4/10 | Nikkud overlap, asimetrik padding, alignment tutarsızlığı.                    |

**TOPLAM: 4.3/10**

---

**SON SÖZ:** İbranice metin güzel render edilmiş ama satırlar birbirine çarpıyor. Nikkud ve cantillation marks overlap ediyor, bu **amatör bir hata**. Highlight box içindeki harfler boğuluyor. Referans soluk, separator görünmüyor. Zigzag göz hareketi kullanıcıyı yoruyor. **Line-height'ı ikiye katlayın, highlight padding'ini artırın, referans kontrastını yükseltin, separator'ı belirgin yapın. O zaman belki 6/10 olur.**
