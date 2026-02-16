# Compare Page — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

**Hissedilen:** Ekranın %60'ı siyah bir void. Tüm fonksiyonel elementler üste tıkış tıkış yığılmış, geri kalanı boş. Bu bir "karşılaştırma motoru" değil, bu bir **fonksiyonel klaustrofobi** örneği.

**En büyük hata:** "Comparative Analysis" başlığı altında ne yapılacağına dair **SIFIR** rehberlik var. Empty state yok, örnek sorgular yok, "nasıl çalışır" bölümü yok. Kullanıcı gelip input alanına bakıp "şimdi ne?" diyor. Bu bir UX felaketi.

---

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Top-heavy iskelet:** Tüm UI elementleri ekranın üst %25'inde. Bu bir "focused design" değil, bu bir **layout hatası**.
- **Ölçek çelişkisi:** Footer'daki "Clarus" watermark **DEV BOYUTUNDA** (ekranın yarısını kaplıyor), ama asıl fonksiyonel etiketler ("Kaynaklar:", "Gelişmiş Arama") **okunamayacak kadar küçük**.
- **Floating aliens:** Sol alttaki "Compiling..." göstergesi ve sağ alttaki kullanıcı avatarı köşelerde yalnız başına, ana UI flow'dan kopuk. Bunlar ne işe yarıyor?

### Whitespace (Negatif Alan)
- **Void çölü:** Input alanı ile footer arasında **hiçbir şey yok**. Bu kadar boşluk ancak bir product hero section'da kabul edilir. Burada sadece kullanıcı kafasını karıştırıyor.
- **Gelişmiş Arama satırı gerginliği:** "Gelişmiş Arama" checkbox solda, açıklama metni sağda. Aralarında dev bir boşluk var, sanki birbirleriyle ilgili değilmiş gibi görünüyorlar.
- **Header sıkışması:** "Comparative Analysis" başlığı üst navigasyona **çok yakın**. Nefes alamıyor.

### Typography
- **Başlık kafa karışıklığı:** 
  - Ana başlık: "Comparative Analysis" (Title Case)
  - Alt başlık: "Comparative analysis across..." (Sentence case)
  - Bu tutarsızlık amatör işi.
- **Okunamayan context:** "Comparative analysis across 43,055 verses..." metni navigasyondan **daha küçük**. Bu uygulamanın en önemli bilgisi neden en okunamaz şekilde yazılmış?
- **Contrast çöküşü:** Input alanı ve dropdown'ların arka planı (`#1a1a1a` gibi) ana arka plan siyahına karşı **çok düşük kontrast**. Interaktif sınırlar "muddy".

### Renk Paleti
- **Turuncu uyarı:** "Compiling..." göstergesindeki turuncu nokta genelde "warning" anlamına gelir. Bu sadece bir arka plan işlemiyse neden turuncu? **Yanlış semantic renk kullanımı**.
- **Tag-Footer çelişkisi:** Kaynak etiketlerinde "Kuran, Eski Ahit, Yeni Ahit" yazıyor (Türkçe), ama footer'da "Quran, Old Testament, New Testament" yazıyor (İngilizce). **Dil tutarsızlığı**.

---

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

### ❌ **DİL KAOSU:** Türkçe tag'ler (Kuran) ama İngilizce footer (Quran)
🔧 Fix:
```tsx
// Tutarlılık seç. Ya hep TR:
const SOURCES_TR = {
  quran: "Kuran",
  old_testament: "Eski Ahit",
  new_testament: "Yeni Ahit",
  apocrypha: "Apokrif Kitaplar"
};

// Ya hep EN:
const SOURCES_EN = {
  quran: "Quran",
  old_testament: "Old Testament",
  new_testament: "New Testament",
  apocrypha: "Apocrypha"
};

// Footer ve tag'lerde AYNI dil kullan
```

### ❌ **EMPTY STATE YOK:** Sayfa yüklenince kullanıcıya hiçbir yönlendirme yok
🔧 Fix:
```tsx
// Input boşken göster:
<div className="max-w-3xl mx-auto mt-20 text-center space-y-8">
  {/* Hero Section */}
  <div>
    <h3 className="text-2xl font-semibold mb-3">
      Kutsal Metinlerde Karşılaştırmalı Analiz
    </h3>
    <p className="text-zinc-400 max-w-2xl mx-auto">
      Bir konu veya kavram girin, 43,055 ayet arasında 5 ajanlı karşılaştırma yapın.
    </p>
  </div>

  {/* Suggested Queries */}
  <div className="grid grid-cols-2 gap-3">
    {[
      "Yaratılış hikayesi",
      "Adalet kavramı",
      "Merhamet ve affetme",
      "Peygamberlerin ortak öğretileri"
    ].map(query => (
      <button 
        onClick={() => setQuery(query)}
        className="p-4 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg text-left
                   transition-colors group"
      >
        <div className="flex items-center justify-between">
          <span className="font-medium">{query}</span>
          <span className="text-zinc-600 group-hover:text-purple-500 
                           transition-colors">→</span>
        </div>
      </button>
    ))}
  </div>

  {/* How it works */}
  <div className="mt-12 p-6 bg-purple-500/5 border border-purple-500/20 rounded-xl">
    <h4 className="font-semibold mb-4 text-purple-300">Nasıl Çalışır?</h4>
    <div className="grid grid-cols-3 gap-4 text-sm">
      <div>
        <div className="text-purple-400 text-2xl mb-2">1</div>
        <p className="text-zinc-400">Konu veya kavram girin</p>
      </div>
      <div>
        <div className="text-purple-400 text-2xl mb-2">2</div>
        <p className="text-zinc-400">5 ajan paralel analiz yapar</p>
      </div>
      <div>
        <div className="text-purple-400 text-2xl mb-2">3</div>
        <p className="text-zinc-400">Karşılaştırmalı rapor alın</p>
      </div>
    </div>
  </div>
</div>
```

### ❌ **HİZALAMA FELAKETI:** "Kaynaklar:" etiketi tag'leriyle hizalı değil
🔧 Fix:
```tsx
// Mevcut (muhtemelen):
<div className="flex items-start gap-2">
  <label>Kaynaklar:</label>
  <div className="flex flex-wrap gap-2">
    {sources.map(...)}
  </div>
</div>

// Olmalı:
<div className="flex items-center gap-3">
  <label className="text-sm font-medium text-zinc-400">Kaynaklar:</label>
  <div className="flex flex-wrap gap-2">
    {sources.map(...)}
  </div>
</div>
```

### ❌ **GELİŞMİŞ ARAMA YANLIZLIĞI:** Checkbox solda, açıklama sağda, ortada çöl
🔧 Fix:
```tsx
// Tek grup olarak ortala:
<label className="inline-flex items-center gap-2 cursor-pointer text-sm">
  <input type="checkbox" className="rounded" />
  <span className="font-medium">Gelişmiş Arama</span>
  <span className="text-zinc-500">(Anahtar kelime bazlı arama)</span>
</label>
```

### ❌ **INPUT DAR:** Desktop'ta arama alanı çok kısa, uzun sorgular gözükmüyor
🔧 Fix:
```tsx
// Mevcut (tahmin):
<input className="max-w-2xl" />

// Olmalı:
<input className="w-full max-w-4xl px-6 py-4 text-base" />
```

### ❌ **CONTRAST DÜŞÜK:** Input ve dropdown'ların arka planı siyahla karışıyor
🔧 Fix:
```css
/* Mevcut (tahmin): */
.input-bg { background: #1a1a1a; }

/* Olmalı: */
.input-bg { 
  background: #18181b; /* zinc-900 */
  border: 1px solid #27272a; /* zinc-800 */
}

/* Hover/Focus state: */
.input-bg:focus {
  border-color: #a855f7; /* purple-500 */
  ring: 2px solid rgba(168, 85, 247, 0.2);
}
```

### ❌ **BAŞLIK SIKIŞIK:** "Comparative Analysis" üst nav'a çok yakın
🔧 Fix:
```css
.page-header {
  @apply mt-12 mb-6; /* Mevcut mt-4 yerine */
}
```

### ❌ **STATUS İKONU YANLIŞ:** "Compiling..." turuncu nokta → warning gibi görünüyor
🔧 Fix:
```tsx
// Turuncu yerine nötr renk:
<span className="inline-flex items-center gap-2 text-sm text-zinc-400">
  <span className="w-2 h-2 bg-zinc-500 rounded-full animate-pulse"></span>
  Compiling...
</span>
```

### ❌ **FOOTER WATERMARK DEV:** "Clarus" arka plan metni ekranın yarısını kaplıyor
🔧 Fix:
```css
/* Mevcut (tahmin): */
.footer-watermark { font-size: 12rem; opacity: 0.05; }

/* Olmalı: */
.footer-watermark { 
  font-size: 8rem; 
  opacity: 0.02; 
  transform: translateY(2rem); /* Yukarı kaydır */
}
```

---

## 4. REÇETE (Nasıl Görünmeliydi?)

**Vizyon:** Karşılaştırma motoru = güçlü araç. Boş sayfa = güçsüz deneyim. Kullanıcı "ne yapabilirim?" sorusunu kendisi cevaplayamamalı, sayfa **göstermeli**.

### Layout Önerisi:
```
┌─────────────────────────────────────┐
│  Header + Nav                        │
├─────────────────────────────────────┤
│  Comparative Analysis                │
│  43,055 verses across 4 collections  │ ← Daha büyük, daha okunur
│                                      │
│  [Search Input - Geniş, Centered]   │ ← %70 genişlik
│  [Kaynaklar: ■ Kuran ■ OT ■ NT]     │ ← Hizalı, ortalı
│  [☑ Gelişmiş Arama (Açıklama)]      │ ← Tek satır, ortalı
│                                      │
│  ┌─────────────────────────────┐   │
│  │ EMPTY STATE                  │   │
│  │ • Örnek Sorgular (4 kart)   │   │
│  │ • Nasıl Çalışır (3 adım)    │   │
│  │ • Son Karşılaştırmalarım    │   │
│  └─────────────────────────────┘   │
│                                      │
├─────────────────────────────────────┤
│  Footer (compact, watermark küçük)  │
└─────────────────────────────────────┘
```

### Tipografi Hiyerarşisi:
```css
h1.page-title { 
  font-size: 2rem;    /* 32px */
  font-weight: 700;
  margin-bottom: 0.5rem;
}

p.subtitle { 
  font-size: 1rem;    /* 16px */
  font-weight: 400;
  color: #a1a1aa;     /* zinc-400 */
  margin-bottom: 2rem;
}

.example-query {
  font-size: 0.9375rem; /* 15px */
  font-weight: 500;
}
```

### Renk Sistemi (Tutarlı):
```css
:root {
  --bg-page: #09090b;         /* zinc-950 */
  --bg-elevated: #18181b;     /* zinc-900 */
  --bg-input: #18181b;        /* zinc-900 */
  --border-default: #27272a;  /* zinc-800 */
  --border-focus: #a855f7;    /* purple-500 */
  --text-primary: #fafafa;    /* zinc-50 */
  --text-secondary: #a1a1aa;  /* zinc-400 */
  --accent: #a855f7;          /* purple-500 */
  --accent-hover: #9333ea;    /* purple-600 */
}
```

---

## 5. PUANLAMA

| Kriter | Puan | Yorum |
|--------|------|-------|
| **Estetik** | 4/10 | Dark theme tutarlı ama %60 boşluk felaketi. Footer watermark ekranı boğuyor. |
| **Kullanılabilirlik** | 3/10 | Empty state yok = kullanıcı ne yapacağını bilmiyor. Input dar, kontrastlar düşük. |
| **Profesyonellik** | 3/10 | Dil karışıklığı (TR tag + EN footer), başlık casing tutarsızlığı, tamamlanmamış hissi. |
| **Boşluk Kullanımı** | 2/10 | %60 ekran boş = %60 kayıp. |
| **Hizalama/Tutarlılık** | 3/10 | "Gelişmiş Arama" satırı kopuk, tag-label hizasız. |

**GENEL ORTALAMA: 3.0/10**

---

## SON SÖZ

Bu sayfa bir "karşılaştırma motoru" olduğunu iddia ediyor ama kullanıcıya **hiçbir şey göstermiyor**. Empty state yok, örnek sorgular yok, rehberlik yok. Bu bir UX felaketi.

Dil karışıklığı kabul edilemez. Tag'lerde "Kuran" yazıp footer'da "Quran" yazmak = tutarsızlık. Ya Türkçe ya İngilizce, ikisi birden değil.

%60 boş alan = %60 başarısızlık. Bu kadar ekran emlak var, neden kullanılmıyor?

**Acil müdahale gerekli:**
1. Empty state ekle (örnek sorgular + "nasıl çalışır" bölümü)
2. Dil birliği (ya TR ya EN, karışık HAYIR)
3. Hizalama düzelt (Gelişmiş Arama + Kaynaklar)
4. Contrast artır (input/dropdown arka planları)
5. Footer watermark küçült (%50 boyut azalt)

Bu sayfa production'da olamaz. Bu haliyle bu bir **beta** bile değil, bu bir **alpha**.
