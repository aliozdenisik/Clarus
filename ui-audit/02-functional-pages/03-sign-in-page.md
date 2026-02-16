# Sign-In Page — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

**Hissedilen:** Dengesiz bir split-screen. Sol taraf sönük ve minimal, sağ taraf cırtlak bir gradient şov. Hero section sign-in formundan daha baskın. Kullanıcı "giriş yapmaya mı geldim yoksa gradient seyretmeye mi?" diye düşünüyor.

**En büyük hata:** "Welcome Back" + "Sign In" + "Login" butonu = **3 farklı terim** aynı işlem için. Terminoloji kaosu. Bunun üzerine sol alt köşede **Next.js logosu** ve sağ altta **ada emoji'li gizemli ikon** var. Bu development artifact'leri mi yoksa tasarım mı? Belli değil. **Amatör işi.**

---

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Hero baskınlığı:** Sağ taraftaki "Sacred Texts, Modern Search" gradient hero section, sol taraftaki sign-in formundan **daha dikkat çekici**. Primary action (giriş yap) secondary content (marketing copy) tarafından gölgeleniyor.
- **Branding tacizi:** "Clarus" ismi **4 kere** tekrar ediyor:
  1. Sol üst logo
  2. Footer logo
  3. Footer background watermark (DEV BOYUTUNDA)
  4. Hero section açıklama metni
  - Bu bir "branding" değil, bu bir **obsesif tekrar**.
- **Back butonu hayalet:** Sol üstteki "← Back" butonu ultra-ince, çok küçük, arka plan yok. Kullanıcı görmez bile.

### Whitespace (Negatif Alan)
- **Dikey boşluk israfı:** Sign-in kartının altından legal metne kadar **DEV BOŞLUK** var. Bu alan kullanılabilir.
- **Kart pozisyon dengesizliği:** Sign-in kartı sol panelin sol tarafına yaslanmış, sağında ve altında dev boşluk. Ortalanmamış layout = dengesiz hissi.
- **Footer hizalama kopukluğu:** Footer link kolonları ("Pages", "Scriptures", "Links") üstteki içerikle **hiçbir grid hizasına** uymamış. Floating.

### Typography
- **Terminoloji kaosu:**
  - Başlıkta: "Sign In"
  - Butonda: "Login"
  - Altta: "Sign Up"
  - Bu 3 farklı terim = kullanıcı kafası karışıklığı. Standart: ya "Sign In/Sign Up" ya da "Log In/Sign Up".
- **Label orantısızlığı:** "Forgot your password?" metni "Password" label'ından **belirgin şekilde küçük**. Visual hierarchy bozuk.
- **Placeholder kontrast düşük:** Input placeholder'ları ("m@example.com", "Password") dark input arka planına karşı **düşük kontrast**. WCAG fail.

### Renk Paleti
- **Gradient sertliği:** Sağ taraftaki gradient'in ortasında **aşırı parlak** bir mor/pembe spot var. Bu çok fazla visual tension yaratıyor. Left side = sessiz, right side = çığlık atan.
- **Buton kontrast:** "Login" butonu solid beyaz blok, içindeki metin çok ince. Beyaz zemin üzerinde ince yazı = legibility kaybı.

---

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

### ❌ **TERMİNOLOJİ KAOSU:** "Welcome Back" + "Sign In" + "Login" + "Sign Up"
🔧 Fix:
```tsx
// Tutarlı terminoloji:
// Seçenek 1 (daha formal):
<h2>Sign In</h2>
<Button>Sign In</Button>
<p>Don't have an account? <Link>Sign Up</Link></p>

// Seçenek 2 (daha casual):
<h2>Log In</h2>
<Button>Log In</Button>
<p>Don't have an account? <Link>Sign Up</Link></p>

// "Welcome Back" gereksiz, kaldır veya subtitle yap:
<p className="text-sm text-zinc-400 mb-6">Welcome back to Clarus</p>
```

### ❌ **DEVELOPMENT ARTIFACT'LER:** Next.js logosu sol altta, ada emoji sağ altta
🔧 Fix:
```tsx
// Production build'de bunları kaldır:

// Mevcut (muhtemelen):
<div className="fixed bottom-4 left-4">
  <Image src="/next.svg" ... />
</div>
<div className="fixed bottom-4 right-4">
  <div>🏝️</div>
</div>

// Olmalı:
// KALDIR. Bunlar production'da ne işe yarıyor?
```

### ❌ **BACK BUTONU GÖRÜNMEZ:** Ultra-ince, küçük, arka plan yok
🔧 Fix:
```tsx
// Mevcut (tahmin):
<button className="text-sm text-zinc-400">
  ← Back
</button>

// Olmalı:
<button className="inline-flex items-center gap-2 px-4 py-2
                   text-sm font-medium text-zinc-300
                   hover:text-white hover:bg-zinc-800
                   rounded-lg transition-colors">
  <svg>...</svg> {/* Daha kalın ok ikonu */}
  <span>Back</span>
</button>
```

### ❌ **KART POZİSYONU DENGESİZ:** Sol panelin sol tarafına yaslanmış
🔧 Fix:
```tsx
// Mevcut (tahmin):
<div className="flex items-start justify-start">
  <Card>...</Card>
</div>

// Olmalı - Ortala:
<div className="flex items-center justify-center min-h-screen">
  <Card className="w-full max-w-md">...</Card>
</div>
```

### ❌ **DİKEY BOŞLUK İSRAFI:** Kart altından legal metne kadar dev boşluk
🔧 Fix:
```tsx
// Legal text'i karta daha yakınlaştır:
<div className="space-y-6"> {/* Mevcut space-y-16 yerine */}
  <Card>...</Card>
  <p className="text-xs text-zinc-500">By signing in...</p>
</div>
```

### ❌ **PLACEHOLDER KONTRAST DÜŞÜK:** WCAG accessibility fail
🔧 Fix:
```css
/* Mevcut (tahmin): */
input::placeholder { color: rgba(255, 255, 255, 0.3); }

/* Olmalı (WCAG AA uyumlu): */
input::placeholder {
  color: #71717a; /* zinc-500 */
}

input {
  background: #18181b; /* zinc-900 */
  border: 1px solid #27272a; /* zinc-800 */
}
```

### ❌ **"FORGOT PASSWORD" SIKIŞIK:** Password label'ının yanında, cramped
🔧 Fix:
```tsx
// Mevcut (muhtemelen):
<div className="flex items-center justify-between">
  <label>Password</label>
  <a href="#">Forgot your password?</a>
</div>

// Olmalı - Input altına taşı:
<div className="space-y-2">
  <label>Password</label>
  <input type="password" />
  <div className="flex justify-end">
    <a href="#" className="text-sm text-purple-400 hover:text-purple-300">
      Forgot your password?
    </a>
  </div>
</div>
```

### ❌ **LOGIN BUTONU KONTRAST:** Beyaz zemin + ince yazı = legibility kaybı
🔧 Fix:
```tsx
// Mevcut (tahmin):
<Button className="bg-white text-black font-normal">Login</Button>

// Olmalı:
<Button className="bg-purple-600 hover:bg-purple-700 text-white font-medium
                   px-6 py-3 rounded-lg transition-colors">
  Sign In
</Button>
```

### ❌ **BRANDING OVERKILL:** "Clarus" 4 kere tekrar ediyor
🔧 Fix:
```tsx
// Footer watermark'ı KALDıR veya %70 küçült:
.footer-watermark {
  font-size: 6rem;    /* Mevcut 12rem yerine */
  opacity: 0.015;     /* Mevcut 0.03 yerine */
  display: none;      /* Veya tamamen kaldır */
}
```

### ❌ **GRADIENT SERT:** Sağ taraf çok parlak mor spot, left side sessiz
🔧 Fix:
```css
/* Mevcut (tahmin): */
background: linear-gradient(135deg, #6366f1 0%, #ec4899 50%, #f59e0b 100%);

/* Olmalı - Daha soft, balanced: */
background: linear-gradient(
  135deg,
  #18181b 0%,
  #3730a3 30%,
  #7c3aed 60%,
  #a855f7 100%
);
opacity: 0.8;
```

### ❌ **FOOTER KOLONLARI KOPUK:** Grid hizasına uymamış
🔧 Fix:
```tsx
// Footer'ı container'a al, grid'e uygun hizala:
<footer className="border-t border-zinc-800 mt-auto">
  <div className="container mx-auto px-8 py-12">
    <div className="grid grid-cols-4 gap-8"> {/* Düzenli grid */}
      <div>...</div> {/* Logo */}
      <div>...</div> {/* Pages */}
      <div>...</div> {/* Scriptures */}
      <div>...</div> {/* Links */}
    </div>
  </div>
</footer>
```

---

## 4. REÇETE (Nasıl Görünmeliydi?)

**Vizyon:** Sign-in sayfası = kapı. Kullanıcıyı içeri almalı, dikkatini dağıtmamalı. Hero section destekleyici olmalı, baskın değil.

### Layout Önerisi:
```
┌────────────────┬────────────────┐
│                │                │
│  [Logo]  [Back]│                │
│                │                │
│  ┌──────────┐  │   Gradient     │
│  │ Sign In  │  │   Hero         │
│  │ Form     │  │   (Soft,       │
│  │ (Center) │  │   Supporting)  │
│  └──────────┘  │                │
│                │                │
│  Legal text    │                │
│                │                │
├────────────────┴────────────────┤
│  Footer (Compact, 4-col grid)  │
└────────────────────────────────┘
```

### Form Component Anatomy:
```tsx
<Card className="w-full max-w-md p-8">
  {/* Header */}
  <div className="text-center mb-8">
    <h1 className="text-2xl font-bold mb-2">Sign In</h1>
    <p className="text-sm text-zinc-400">Welcome back to Clarus</p>
  </div>

  {/* OAuth */}
  <Button variant="outline" className="w-full mb-6">
    <GoogleIcon /> Continue with Google
  </Button>

  <Divider>or</Divider>

  {/* Form */}
  <form className="space-y-4 mt-6">
    <div>
      <label className="text-sm font-medium mb-2 block">Email</label>
      <input
        type="email"
        placeholder="you@example.com"
        className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800
                   rounded-lg focus:border-purple-500 focus:ring-2
                   focus:ring-purple-500/20 transition-colors"
      />
    </div>

    <div>
      <label className="text-sm font-medium mb-2 block">Password</label>
      <input type="password" />
      <div className="flex justify-end mt-2">
        <a href="#" className="text-sm text-purple-400">Forgot password?</a>
      </div>
    </div>

    <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700">
      Sign In
    </Button>
  </form>

  {/* Footer */}
  <p className="text-center text-sm text-zinc-400 mt-6">
    Don't have an account? <a href="#" className="text-purple-400">Sign Up</a>
  </p>
</Card>
```

### Renk Sistemi:
```css
:root {
  /* Backgrounds */
  --bg-page: #09090b;         /* zinc-950 */
  --bg-card: #18181b;         /* zinc-900 */
  --bg-input: #18181b;        /* zinc-900 */

  /* Borders */
  --border-default: #27272a;  /* zinc-800 */
  --border-focus: #a855f7;    /* purple-500 */

  /* Text */
  --text-primary: #fafafa;    /* zinc-50 */
  --text-secondary: #a1a1aa;  /* zinc-400 */
  --text-muted: #71717a;      /* zinc-500 */

  /* Accent */
  --accent: #a855f7;          /* purple-500 */
  --accent-hover: #9333ea;    /* purple-600 */
}
```

---

## 5. PUANLAMA

| Kriter | Puan | Yorum |
|--------|------|-------|
| **Estetik** | 5/10 | Gradient güzel ama çok agresif. Branding overkill (4x Clarus). Dev artifacts (Next.js logo, ada emoji) amatör işi. |
| **Kullanılabilirlik** | 4/10 | Terminoloji kaosu (Sign In/Login/Sign Up). "Forgot password" yanlış yerde. Placeholder kontrast düşük. |
| **Profesyonellik** | 4/10 | Development artifact'leri production'da. Footer watermark dev boyutunda. Back butonu görünmez. |
| **Layout Dengesi** | 4/10 | Hero section sign-in'den baskın. Kart dengesiz pozisyonda (sola yaslanmış). Dikey boşluk israfı. |
| **Accessibility** | 3/10 | Placeholder kontrast WCAG fail. Back butonu çok küçük. Legal text çok küçük/uzak. |

**GENEL ORTALAMA: 4.0/10**

---

## SON SÖZ

Bu sayfa bir "giriş kapısı" ama kullanıcıyı karşılamak yerine **dikkatini dağıtıyor**. Hero section çok baskın, sign-in formu gölgede kalıyor.

Terminoloji kaosu kabul edilemez. "Sign In" başlığı altında "Login" butonu = tutarsızlık. Ya "Sign In" ya "Log In", ikisi birden değil.

**Development artifact'leri production'da ne arıyor?** Next.js logosu ve ada emoji sol/sağ altta yalnız başına duruyor. Bu amatör işi. Production build'de bunlar olmamalı.

Branding overkill: "Clarus" 4 kere tekrar ediyor. Footer watermark ekranın yarısını kaplıyor. Bu bir branding değil, bu bir **obsesyon**.

**Acil müdahale:**
1. Terminoloji birliği (Sign In VEYA Log In, ikisi değil)
2. Development artifact'leri kaldır (Next.js logo, ada emoji)
3. Back butonunu görünür yap
4. Kart pozisyonunu ortala
5. Placeholder kontrast artır (WCAG AA)
6. Footer watermark küçült veya kaldır
7. "Forgot password" input altına taşı
8. Login butonu renk/kontrast düzelt

Bu sayfa production'a hazır değil. Beta olarak bile kabul edilemez.
