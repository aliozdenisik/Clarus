# Hero Section — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

İlk bakışta: **Güvenli, sıradan, unutulabilir.**

Bu hero section bir kutsal metin arama uygulaması için mi yoksa bir generic SaaS landing page template'i mi anlamak imkansız. Serif font kullanımı akademik hava katmaya çalışmış ama ortaya çıkan şey "AI startup starter pack #2847" olmuş. 

Gözü kanatan en büyük hata: **TIPOGRAFIK KARAKTER EKSİKLİĞİ.** "Explore Sacred Texts" yazan devasa başlığın hiçbir personality'si yok. Serife vurgu yapılmış ama hangi serif kullanıldığı belli bile değil — muhtemelen Playfair Display gibi overused bir font. Kutsal metinlerle çalışan bir platformun typographic voice'u bu kadar yavan olamaz.

İkinci büyük sorun: **SPATIAL HIERARCHY ÇÖKMÜŞ.** Logo ile başlık arasındaki boşluk, başlık ile alt metin arasındakinden DAHA FAZLA. Bu optik olarak başlığı tavana yapıştırıyor, kullanıcının gözü bir anda aşağıya kayıyor. Visual flow bozuk.

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
**Durum:** 6/10 — İşlevsel ama sığ.

- ✅ "Explore Sacred Texts" ile "with AI" arasındaki kontrast net (beyaz vs. indigo).
- ✅ Primary CTA ("Go to Search") dolgulu buton ile doğru vurgulanmış.
- ❌ Logo çok küçük kalmış. "CLARUS" branding'i kullanıcının 2. bakışında fark ediliyor, 1.'de değil.
- ❌ Alt metin (#9CA3AF) karanlık arka planda kaybolmaya başlıyor. Contrast ratio tehlikeli bölgede (WCAG AA sınırında).
- ❌ İki buton arasındaki visual weight farkı YETERSİZ. Outlined buton çok fazla dikkat çekiyor, primary'den güç çalıyor.

**Optik olarak en güçlü öğe:** "Explore Sacred Texts" ✅  
**İkinci odak:** "Go to Search" butonu ❌ (olması gereken: CTA, olduğu: logo ve secondary button arası kaybolmuş)

### Whitespace (Negatif Alan)
**Durum:** 5/10 — Tutarsız ve gevşek.

- ❌ Logo → Başlık arası: ~120-140px (TAHMİNİ) — FAZLA.
- ❌ Başlık → Alt metin arası: ~32-40px — AZ.
- ❌ Alt metin → CTA'lar arası: ~48-56px — İDARE EDER ama ritmik değil.
- ✅ Yatay kenarlardaki boşluk dengeli, odağı merkeze topluyor.

**Sorun:** Dikey ritim tutarlı değil. Spacer değerleri arasında matematiksel bir oran yok (golden ratio, 8-point grid, vb.). Boşluklar keyfi atılmış gibi duruyor.

**Fix gerektiren spacing değerleri:**
```
Logo-to-Title: 64px'e düşür (mevcut ~120px)
Title-to-Subtitle: 24px'e düşür (mevcut ~40px)
Subtitle-to-CTA: 40px'e çıkar (mevcut ~48px)
```

### Typography
**Durum:** 4/10 — Karaktersiz ve güvensiz.

**Ana Başlık:**
- Font: Muhtemelen Playfair Display veya benzeri bir Google Fonts serif.
  - ❌ SORUN: 2024'ün en overused serif'i. AI slop karakteristiği.
  - ❌ "Explore Sacred Texts" metni GENERIC. Neden buraya gelen biri "kutsal metin" aradığını anlamasın?
  - ❌ Font size çok büyük (~56-64px) ama line-height dar. Metinde hava yok, sıkışık duruyor.

**Alt Metin:**
- Font: Inter/Geist/System sans-serif ailesi (kesin tespit edilemedi).
  - ❌ SORUN: Bu font seçimi başlıkla ZAYIF kontrast oluşturuyor. Serif + generic sans-serif pairing'i 2020 startup aesthetic'i — özgünlük sıfır.
  - ❌ Renk (#9CA3AF) karanlık arka planda zayıf kalıyor. Accessibility riski var.

**Butonlar:**
- ✅ Sans-serif, Medium/Semibold — okunabilir.
- ❌ İkonlar metne göre KÜÇÜK. Büyüteç ikonu metnin x-height'ına göre dengesiz (16px iken metin 14px gibi görünüyor ama ikon optik olarak 12px etkisi yapıyor).

**Font Stack Önerisi:**
```css
/* Ana Başlık — BOLD, DISTINCTIVE */
font-family: 'Cormorant Garamond', 'EB Garamond', serif;
font-weight: 600;
font-size: 52px;
line-height: 1.2;
letter-spacing: -0.02em;

/* Alt Metin — REFINED, CONTRAST */
font-family: 'Manrope', 'DM Sans', sans-serif;
font-weight: 400;
font-size: 16px;
line-height: 1.6;
color: #C4C8CC; /* Daha açık gri */
```

### Renk Paleti
**Durum:** 6/10 — Güvenli ama flat.

**Arka Plan:**
- Koyu lacivert/siyah gradyan (#0A0A0B → #111112) + noise texture.
  - ✅ Derinlik var, tek düze değil.
  - ❌ Gradyan geçişinde hafif **banding** (şeritlenme) gözüküyor. Dither efekti eksik.

**Vurgu Rengi (Indigo #5842F4):**
- ❌ PREDİCTABLE. Neden indigo? Neden mor? 2023-2024'ün her AI landing page'i bu rengi kullandı.
  - Alternatif önerisi: Derin amber (#F59E0B), sıcak emerald (#10B981), ya da cesur crimson (#DC2626) — kutsal metinlerin tarihsel context'ine uygun renk paleti.

**Metin Renkleri:**
- Beyaz (#FFFFFF): ✅ Net.
- Alt metin grisi (#9CA3AF): ❌ Contrast ratio düşük (tahmini 4.2:1, WCAG AA minimum 4.5:1).

**Palette Fix:**
```css
--bg-primary: #0B0B0F; /* Daha zengin siyah */
--bg-gradient: linear-gradient(180deg, #0B0B0F 0%, #16151E 100%);
--accent-primary: #F59E0B; /* Amber — warmth, sacred texts */
--text-primary: #FAFAFA; /* Soft white */
--text-secondary: #D1D5DB; /* Daha yüksek contrast */
```

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **Logo Hizalaması Optik Olarak Bozuk**  
"CLARUS" metni, üstteki kitap ikonu ile merkeze hizalanmış ama "C" ve "S" harflerinin serif çıkıntıları nedeniyle sola yatık duruyor.  
🔧 Fix: 
```css
.logo-text {
  transform: translateX(1px); /* Optik düzeltme */
}
```

❌ **Alt Metin Kontrastı Yetersiz (#9CA3AF)**  
WCAG AA standardının altında. Düşük görüşlü kullanıcılar için accessibility riski.  
🔧 Fix: 
```css
.subtitle {
  color: #D1D5DB; /* Daha açık gri */
}
```

❌ **Başlık-Logo Arası Boşluk Fazla (~120px)**  
Başlık yukarıya "yapışmış" gibi duruyor, spatial rhythm bozuk.  
🔧 Fix:
```css
.hero-container {
  gap: 64px; /* Logo-to-title */
}
.title-to-subtitle {
  margin-top: 24px;
}
```

❌ **Buton İkonları Metne Göre Küçük**  
Büyüteç ve shuffle ikonları metnin x-height'ı ile uyumsuz.  
🔧 Fix:
```tsx
<Search className="w-5 h-5" /> {/* 16px → 20px */}
<Shuffle className="w-5 h-5" />
```

❌ **Serif Font Seçimi Generic (Playfair Display)**  
Overused, karaktersiz. Kutsal metinlere özgü bir personality yok.  
🔧 Fix:
```css
font-family: 'Cormorant Garamond', serif;
/* Ya da: 'EB Garamond', 'Crimson Pro' */
```

❌ **Secondary Button Çok Fazla Dikkat Çekiyor**  
Outlined button'un border'ı çok kalın, primary CTA'dan güç çalıyor.  
🔧 Fix:
```css
.secondary-button {
  border: 1px solid rgba(255, 255, 255, 0.15); /* Daha ince, şeffaf */
  color: #9CA3AF; /* Daha düşük contrast */
}
```

❌ **Gradyan Banding Sorunu**  
Arka plan geçişinde hafif şeritlenme var.  
🔧 Fix:
```css
background: linear-gradient(180deg, #0B0B0F 0%, #16151E 100%);
background-blend-mode: multiply;
/* SVG noise texture ekle: */
background-image: url("data:image/svg+xml,%3Csvg...noise-pattern");
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Adım 1: Typography Overhaul
```css
/* Başlık — BOLD, DISTINCTIVE CHARACTER */
.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 600;
  font-size: clamp(42px, 5vw, 52px);
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #FAFAFA;
}

.hero-title-accent {
  color: #F59E0B; /* Amber yerine indigo */
  font-style: italic; /* Vurgu için */
}

/* Alt Metin — REFINED, READABLE */
.hero-subtitle {
  font-family: 'Manrope', sans-serif;
  font-weight: 400;
  font-size: 17px;
  line-height: 1.65;
  color: #D1D5DB;
  max-width: 540px;
}
```

### Adım 2: Spatial Rhythm Fix
```tsx
<div className="flex flex-col items-center">
  {/* Logo */}
  <Logo className="mb-16" /> {/* 64px spacing */}
  
  {/* Title */}
  <h1 className="mb-6"> {/* 24px spacing */}
    Explore Sacred Texts <span className="accent">with AI</span>
  </h1>
  
  {/* Subtitle */}
  <p className="mb-10"> {/* 40px spacing */}
    Search across 43,055 verses...
  </p>
  
  {/* CTAs */}
  <div className="flex gap-4">...</div>
</div>
```

### Adım 3: Color Palette Upgrade
```css
:root {
  --bg-hero: #0B0B0F;
  --bg-gradient-end: #16151E;
  --accent: #F59E0B; /* Kutsal metinlere uygun sıcak ton */
  --text-primary: #FAFAFA;
  --text-secondary: #D1D5DB;
  --button-primary-bg: #F59E0B;
  --button-primary-text: #0B0B0F;
  --button-secondary-border: rgba(255, 255, 255, 0.12);
}
```

### Adım 4: Button Redesign
```tsx
/* Primary CTA */
<Button className="
  bg-[#F59E0B] 
  text-[#0B0B0F] 
  font-semibold 
  px-6 py-3 
  rounded-lg
  hover:bg-[#FBBF24]
  transition-all duration-200
  shadow-lg shadow-amber-500/20
">
  <Search className="w-5 h-5" />
  Go to Search
</Button>

/* Secondary CTA */
<Button className="
  border border-white/12
  text-gray-400
  hover:text-white
  hover:border-white/24
  px-6 py-3
  rounded-lg
">
  <Shuffle className="w-5 h-5" />
  Go to Compare
</Button>
```

### Adım 5: Noise Texture Ekleme
```tsx
<div className="relative">
  {/* Gradyan background */}
  <div className="absolute inset-0 bg-gradient-to-b from-[#0B0B0F] to-[#16151E]" />
  
  {/* Noise overlay */}
  <div 
    className="absolute inset-0 opacity-[0.03]"
    style={{
      backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
      backgroundRepeat: 'repeat',
    }}
  />
</div>
```

## 5. PUANLAMA

| Kriter | Puan | Gerekçe |
|--------|------|---------|
| Estetik | 5/10 | Generic serif + indigo = 2024 AI startup cliché. Karaktersiz. |
| Kullanılabilirlik | 6/10 | Butonlar net ama alt metin kontrastı düşük. Visual hierarchy zayıf. |
| Profesyonellik | 6/10 | İşlevsel ama unutulabilir. "Kutsal metin" temas missing. |
| **TOPLAM** | **5.7/10** | **Ortalama. Çalışır ama öne çıkmaz.** |

---

## SON SÖZ

Bu hero section bir **B-** landing page. Çalışıyor ama hiç kimse hatırlamayacak. Kutsal metinlerle çalışan bir platformun hero'su **akademik ağırlık, tarihsel derinlik ve typographic zenginlik** taşımalı. 

Şu anki durum: "AI ile bir şeyler yapıyoruz" startup template'i #2847.  
Olması gereken: "Bin yıllık metinlere modern teknoloji ile dokunuyoruz" — cesur, distinctive, memorable.

**Acil aksiyonlar:**
1. Serif font değiştir → Cormorant Garamond / EB Garamond
2. Indigo → Amber (#F59E0B) renk geçişi
3. Spatial rhythm fix (64-24-40px ritmi)
4. Alt metin contrast artır (#D1D5DB)
5. Noise texture ekle (banding gider)

Şu anki tasarım **unutulacak kadar güvenli**. Risk alınmamış. Personality yok.
