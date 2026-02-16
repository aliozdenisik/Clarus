# UI/UX Audit Roadmap — Faydacı Lüks Standardına Ulaşma

**Milestone:** #10 (22 issue, 0 closed)
**Tarih:** 2026-02-16
**Strateji:** Dependency-first, paralel wave execution

---

## TL;DR — Yürütme Özeti

```
Wave 0 ──▶ P0 BUGS (2 issue)              ⏱ ~2-3 saat    BLOCKER
Wave 1 ──▶ Design System Tokens (1 issue)  ⏱ ~3-4 saat    FOUNDATION
Wave 2 ──▶ Homepage (6 issue, paralel)     ⏱ ~8-10 saat   PARALLEL
Wave 3 ──▶ App Pages (3 issue, paralel)    ⏱ ~4-6 saat    PARALLEL
Wave 4 ──▶ Keyword Search (10 issue)       ⏱ ~10-14 saat  GROUPED
                                            ──────────────
                                     Toplam: ~27-37 saat
```

---

## Wave 0 — P0 Kritik Buglar 🚨

> **Ön koşul:** Yok. Hemen başlanabilir. Diğer tüm wave'lerden bağımsız.
> **Strateji:** İki bug birbirinden bağımsız → **paralel çözülebilir**.

| # | Issue | Sorun | Dosya(lar) | Efor |
|---|-------|-------|------------|------|
| **#156** | 🚨 Greek NT — Black Void Bug | 12,000px siyah boşluk. Virtualization `itemCount` veya `getItemSize` hatası | `components/keyword-search/root-browser.tsx` | 1-2 saat |
| **#157** | 🚨 Root Detail — Auth Redirect Bug | Read-only `/keyword-search/root/*` sayfaları auth gate arkasında | `middleware.ts` veya auth config | 1 saat |

### Bağımlılık Grafiği
```
#156 ──┐
       ├──▶ (bağımsız, paralel yapılabilir)
#157 ──┘
```

### Notlar
- **#156** çözülmeden Greek NT keyword search'ün hiçbir UI iyileştirmesi (#155, #154, #152) test edilemez
- **#157** çözülmeden kullanıcılar root detail sayfalarına ulaşamaz, yani Wave 4'ün tamamı production'da test edilemez

---

## Wave 1 — Design System Foundation 🎨

> **Ön koşul:** Yok (Wave 0 ile paralel başlanabilir, ama merge sırası: Wave 0 → Wave 1)
> **Strateji:** Tüm 22 issue'da ortak şikayet edilen 4 temel problemi tek seferde çöz.

### Neden Önce?

22 issue'nun **tamamında** tekrar eden sorunlar:

| Sorun | Kaç issue'da geçiyor | Çözüm |
|-------|----------------------|-------|
| Font: Playfair Display → kaliteli serif | 15+ | `globals.css` font import + CSS variable |
| Renk: Indigo (#5842F4) → Amber (#F59E0B) accent | 12+ | CSS custom properties |
| Kontrast: `text-gray-500` WCAG fail | 18+ | `text-gray-300` / `text-gray-200` global fix |
| Footer: Dev watermark, %40 viewport waste | 8+ | Footer component refactor |

### Issue

| # | Issue | Kapsam |
|---|-------|--------|
| **#140** | Homepage — Footer | Tüm sayfalarda paylaşılan footer component'i. Watermark amputation, padding normalize, link contrast, grid alignment |

### Ek Çalışma (issue dışı ama zorunlu)

```
1. globals.css → Font import (Cormorant Garamond + Manrope)
2. tailwind.config → Color palette custom properties
3. CSS variables → --accent-primary, --text-secondary, --bg-hero
4. Footer component → Tüm sayfalara yansır
```

### Bağımlılık Grafiği
```
Wave 0 (P0 bugs) ──▶ Wave 1 (Design System + Footer)
                            │
                            ▼
                     Wave 2, 3, 4 (her şey buraya bağlı)
```

---

## Wave 2 — Homepage Sections 🏠

> **Ön koşul:** Wave 1 (font, renk, footer tamamlanmış olmalı)
> **Strateji:** 6 issue birbirinden **tamamen bağımsız** → **full paralel** çalışılabilir

### Paralel İş Dağılımı

| # | Issue | Bölüm | Karmaşıklık | Dokunulan Component |
|---|-------|-------|-------------|---------------------|
| **#136** | Hero Section | Typography overhaul, spacing rhythm, buton redesign | Orta | `app/[locale]/page.tsx` (hero bölümü) |
| **#138** | Quote Carousel | İtalik serif kaldır, pagination büyüt, spacing fix | Düşük | `components/` carousel component |
| **#141** | CTA Section | Split headline birleştir, contrast artır, buton fix | Düşük | `app/[locale]/page.tsx` (CTA bölümü) |
| **#158** | Features Cards Grid | Glassmorphism düzelt, visual weight hierarchy | Orta | `app/[locale]/page.tsx` (features) |
| **#159** | Agents Section | Hierarchy düzelt, contrast artır, badge fix | Orta | `app/[locale]/page.tsx` (agents) |
| **#160** | How It Works | Serif/sans clash fix, grid gap, WCAG contrast | Düşük | `app/[locale]/page.tsx` (steps) |

### Bağımlılık Grafiği
```
Wave 1 (Design System)
    │
    ├──▶ #136 Hero Section      ─┐
    ├──▶ #138 Quote Carousel     │
    ├──▶ #141 CTA Section        ├── Hepsi PARALEL
    ├──▶ #158 Features Cards     │
    ├──▶ #159 Agents Section     │
    └──▶ #160 How It Works      ─┘
```

### Birlikte Çözülebilecek Doğal Çiftler

Eğer paralel kapasiten 6 değil 3 ise, şu ikilileri grupla:

| Grup | Issues | Neden birlikte? |
|------|--------|-----------------|
| **A** | #136 + #141 | Her ikisi de headline typography + CTA buton redesign |
| **B** | #158 + #159 | Her ikisi de kart-tabanlı layout, glassmorphism + hierarchy |
| **C** | #138 + #160 | Her ikisi de düşük karmaşıklık, typography + spacing fix |

---

## Wave 3 — App Pages (Search, Compare, Sign-In) 🔍

> **Ön koşul:** Wave 1 (font, renk, footer)
> **Strateji:** 3 issue birbirinden **bağımsız** → **paralel**
> **Not:** Wave 2 ile de paralel yapılabilir (bağımlılık yok)

| # | Issue | Sayfa | Ana Sorunlar | Karmaşıklık |
|---|-------|-------|-------------|-------------|
| **#161** | Search Page | `/search` | Empty state yok, dil karmaşası (TR+EN), %70 boşluk, alignment | Orta |
| **#162** | Compare Page | `/compare` | Empty state yok, dil karmaşası, %60 boşluk, alignment | Orta |
| **#145** | Sign-In Page | `/sign-in` | Terminoloji kaosu (Sign In/Login), dev artifacts, kart pozisyonu | Düşük |

### Bağımlılık Grafiği
```
Wave 1 (Design System)
    │
    ├──▶ #161 Search Page   ─┐
    ├──▶ #162 Compare Page    ├── PARALEL (birbirinden bağımsız)
    └──▶ #145 Sign-In Page  ─┘
```

### Birlikte Çözülebilecek Doğal Çift

| Grup | Issues | Neden birlikte? |
|------|--------|-----------------|
| **D** | #161 + #162 | Neredeyse birebir aynı sorunlar: empty state yok, dil karmaşası, boşluk, alignment. Çözümler copy-paste edilebilir |

---

## Wave 4 — Keyword Search Ekosistemi 🔬

> **Ön koşul:** Wave 0 (#156, #157) + Wave 1 (Design System)
> **Strateji:** 10 issue, 4 alt grup. Gruplar arası bağımsız → **gruplar paralel**

### Alt Grup Yapısı

#### 4A — Keyword Search Altyapısı (Önce)

| # | Issue | Kapsam | Karmaşıklık |
|---|-------|--------|-------------|
| **#144** | Keyword Search — Empty State | Empty state redesign, amber alert → nötr bildirim, çift tab ayrımı, CTA büyüt | Orta |
| **#163** | Quran Browse Grid | Arapça font (Scheherazade New), RTL layout, grid gap fix, hover states | Orta |

> **#144 ve #163** birbirine bağlı değil ama ikisi de keyword search'ün "giriş noktası". Paralel yapılabilir.

#### 4B — Quran Root Detail (Birlikte Çözülmeli ⚡)

| # | Issue | Bölüm | Ana Sorun |
|---|-------|-------|-----------|
| **#151** | Quran Root Info | Üst panel (kök bilgi + chart) | Scrollbar, padding, rozet renk kaosu, chart'ta rakam yok |
| **#149** | Quran Derived Words | Sol sidebar (türev kelimeler) | Line-height, vurgu kontrast, scrollbar, buton tutarsızlığı |
| **#164** | Quran Morphology Tab | Aynı sayfa, farklı tab | Scrollbar-border çarpışması, satır aralığı, rozet kaosu |

> ⚡ **Bu 3 issue AYNI SAYFANIN farklı bölümleri** (`/keyword-search/root/ktb`).
> Ayrı ayrı çözmek: 3 × PR, merge conflict riski
> Birlikte çözmek: 1 × PR, tutarlı sonuç

#### 4C — Hebrew Root Detail (Birlikte Çözülmeli ⚡)

| # | Issue | Bölüm | Ana Sorun |
|---|-------|-------|-----------|
| **#148** | Hebrew Root Info | Üst panel (kök bilgi + chart) | **KRİTİK BUG:** Helper text Arapça gösteriyor (İbranice olmalı), tekil/çoğul tutarsızlığı, chart'ta rakam yok |
| **#153** | Hebrew Verse Cards | Ayet kartları | Line-height overlap (nikkud), highlight padding, referans kontrast |

> ⚡ **Aynı sayfa**, aynı component ağacı.

#### 4D — Greek Root Detail (Birlikte Çözülmeli ⚡)

| # | Issue | Bölüm | Ana Sorun |
|---|-------|-------|-----------|
| **#155** | Greek Root Info | Üst panel | **BUG:** Chart render edilmemiş (%50 boşluk), yanlış helper text, gramer hatası ("Word" → "Words") |
| **#154** | Greek Derived Words | Türetilmiş kelimeler | Choice paralysis (30 buton kaos), gruplandırma yok, font küçük |
| **#152** | Greek Verse Results | Ayet kartları | Eksik çeviri fallback, referans kontrast, çeviri boyutu |

> ⚡ **Aynı sayfa**. #155'teki chart bug'ı (boş render) ayrıca #156 ile ilişkili olabilir.

### Wave 4 Bağımlılık Grafiği

```
Wave 0 (#156 Black Void, #157 Auth) ─┐
Wave 1 (Design System)               ─┤
                                       ▼
    ┌──────────────────────────────────────────────┐
    │                  WAVE 4                        │
    │                                                │
    │  #144 Empty State ──┐                         │
    │  #163 Browse Grid ──┤── 4A (paralel, önce)    │
    │                      │                         │
    │                      ▼                         │
    │  #151+#149+#164 ────┐                         │
    │  (Quran Root)        │                         │
    │                      ├── 4B/4C/4D (paralel)   │
    │  #148+#153 ─────────┤                         │
    │  (Hebrew Root)       │                         │
    │                      │                         │
    │  #155+#154+#152 ────┘                         │
    │  (Greek Root)                                  │
    └──────────────────────────────────────────────┘
```

---

## Tam Bağımlılık Grafiği

```
                    ┌─────────────────┐
                    │   WAVE 0: P0    │
                    │  #156  #157     │
                    │  (PARALEL)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  WAVE 1: TOKENS │
                    │  #140 Footer    │
                    │  + CSS vars     │
                    │  + Font import  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐ ┌───▼────────┐ ┌───▼──────────────┐
     │  WAVE 2: HOME  │ │ WAVE 3:    │ │  WAVE 4: KEYWORD │
     │  6 issue       │ │ APP PAGES  │ │  SEARCH (10)     │
     │  (PARALEL)     │ │ 3 issue    │ │                  │
     │                │ │ (PARALEL)  │ │  4A: #144, #163  │
     │  #136 Hero     │ │            │ │       ↓          │
     │  #138 Carousel │ │ #161 Search│ │  4B: #151+149+164│
     │  #141 CTA      │ │ #162 Compr.│ │  4C: #148+153    │
     │  #158 Features │ │ #145 SignIn│ │  4D: #155+154+152│
     │  #159 Agents   │ │            │ │  (GRUPLAR PARALEL│
     │  #160 HowItWrk │ │            │ │   İÇLERİ SEQUENTİAL)│
     └────────────────┘ └────────────┘ └──────────────────┘
```

---

## Çözüm Matrisi — Hızlı Referans

| # | Issue | Wave | Grup | Paralel mi? | Ön Koşul | PR Stratejisi |
|---|-------|------|------|-------------|----------|---------------|
| 156 | 🚨 Black Void Bug | 0 | - | ✅ | - | Tek başına PR |
| 157 | 🚨 Auth Redirect | 0 | - | ✅ | - | Tek başına PR |
| 140 | Footer | 1 | - | ❌ | Wave 0 | Design System PR'ı ile birlikte |
| 136 | Hero Section | 2 | A | ✅ | Wave 1 | #141 ile birleştirilebilir |
| 138 | Quote Carousel | 2 | C | ✅ | Wave 1 | #160 ile birleştirilebilir |
| 141 | CTA Section | 2 | A | ✅ | Wave 1 | #136 ile birleştirilebilir |
| 158 | Features Cards | 2 | B | ✅ | Wave 1 | #159 ile birleştirilebilir |
| 159 | Agents Section | 2 | B | ✅ | Wave 1 | #158 ile birleştirilebilir |
| 160 | How It Works | 2 | C | ✅ | Wave 1 | #138 ile birleştirilebilir |
| 145 | Sign-In Page | 3 | - | ✅ | Wave 1 | Tek başına PR |
| 161 | Search Page | 3 | D | ✅ | Wave 1 | #162 ile birleştirilebilir |
| 162 | Compare Page | 3 | D | ✅ | Wave 1 | #161 ile birleştirilebilir |
| 144 | KW Empty State | 4 | 4A | ✅ | Wave 1 | #163 ile paralel ama ayrı PR |
| 163 | Quran Browse Grid | 4 | 4A | ✅ | Wave 1 | Tek başına PR (font import) |
| 151 | Quran Root Info | 4 | 4B | ⚡ | Wave 1 | **#149 + #164 ile TEK PR** |
| 149 | Quran Derived Words | 4 | 4B | ⚡ | Wave 1 | **#151 + #164 ile TEK PR** |
| 164 | Quran Morphology | 4 | 4B | ⚡ | Wave 1 | **#151 + #149 ile TEK PR** |
| 148 | Hebrew Root Info | 4 | 4C | ⚡ | Wave 1 | **#153 ile TEK PR** |
| 153 | Hebrew Verse Cards | 4 | 4C | ⚡ | Wave 1 | **#148 ile TEK PR** |
| 155 | Greek Root Info | 4 | 4D | ⚡ | Wave 0+1 | **#154 + #152 ile TEK PR** |
| 154 | Greek Derived Words | 4 | 4D | ⚡ | Wave 0+1 | **#155 + #152 ile TEK PR** |
| 152 | Greek Verse Results | 4 | 4D | ⚡ | Wave 0+1 | **#155 + #154 ile TEK PR** |

> ✅ = Bağımsız, paralel yapılabilir
> ⚡ = Aynı sayfa, birlikte çözülmeli (ayrı PR riskli)
> ❌ = Sıralı, ön koşulu var

---

## PR Stratejisi — Minimum Merge Conflict

22 issue'yı en az PR sayısıyla, en az conflict riskiyle kapatma planı:

| PR # | İçerik | Kapatılan Issues | Dosya Kapsamı |
|------|--------|------------------|---------------|
| **PR 1** | Black Void Bug fix | #156 | `components/keyword-search/` |
| **PR 2** | Auth route protection fix | #157 | `middleware.ts` |
| **PR 3** | Design System Foundation + Footer | #140 | `globals.css`, `tailwind.config`, `components/layout/footer` |
| **PR 4** | Homepage: Hero + CTA | #136, #141 | `app/[locale]/page.tsx` (hero + CTA sections) |
| **PR 5** | Homepage: Features + Agents | #158, #159 | `app/[locale]/page.tsx` (features + agents) |
| **PR 6** | Homepage: Carousel + How It Works | #138, #160 | `app/[locale]/page.tsx` (carousel + steps) |
| **PR 7** | Search + Compare empty state & i18n | #161, #162 | `app/[locale]/search/`, `app/[locale]/compare/` |
| **PR 8** | Sign-In page polish | #145 | `app/[locale]/sign-in/` |
| **PR 9** | Keyword Search empty state | #144 | `components/keyword-search/` |
| **PR 10** | Quran Browse Grid + Arabic font | #163 | `components/keyword-search/`, `globals.css` |
| **PR 11** | Quran Root Detail overhaul | #151, #149, #164 | `components/keyword-search/root-browser`, verse-card, sidebar |
| **PR 12** | Hebrew Root Detail overhaul | #148, #153 | Same components, Hebrew-specific logic |
| **PR 13** | Greek Root Detail overhaul | #155, #154, #152 | Same components, Greek-specific logic |

**Toplam: 13 PR ile 22 issue kapatılır.**

---

## Tahmini Zamanlama (Tek Geliştirici)

| Wave | İş Günü | Notlar |
|------|---------|--------|
| Wave 0 | 0.5 gün | P0 buglar, acil |
| Wave 1 | 0.5 gün | CSS tokens + footer |
| Wave 2 | 2 gün | 6 homepage section (3 PR) |
| Wave 3 | 1 gün | 3 app page (2 PR) |
| Wave 4 | 2-3 gün | 10 keyword search issue (5 PR) |
| **Toplam** | **6-7 iş günü** | ~1.5 hafta |

### Paralel Çalışma ile (2 Geliştirici)

| Geliştirici 1 | Geliştirici 2 |
|---------------|---------------|
| Wave 0: #156 | Wave 0: #157 |
| Wave 1: Design System + Footer | Wave 2 prep: Component audit |
| Wave 2: PR 4 (Hero+CTA) | Wave 2: PR 5 (Features+Agents) |
| Wave 2: PR 6 (Carousel+HowItWorks) | Wave 3: PR 7 (Search+Compare) |
| Wave 3: PR 8 (Sign-In) | Wave 4A: PR 9+10 (Empty State + Browse) |
| Wave 4B: PR 11 (Quran Root) | Wave 4C: PR 12 (Hebrew Root) |
| Wave 4D: PR 13 (Greek Root) | QA + final review |
| **~4 iş günü** | **~4 iş günü** |

---

## Riskler ve Dikkat Noktaları

| Risk | Etki | Mitigasyon |
|------|------|------------|
| Font değişikliği tüm sayfaları etkiler | Yüksek | Wave 1'de tek seferde, regression test |
| Footer component tüm sayfalarda paylaşılıyor | Yüksek | Wave 1'de çöz, sonraki wave'lerde dokunma |
| Keyword search component'leri birbirine bağlı | Orta | Aynı sayfanın issue'larını TEK PR'da çöz |
| WCAG kontrast fix'leri 18+ issue'da geçiyor | Orta | CSS variable ile global çöz, sayfa sayfa uğraşma |
| Arapça font import bundle size artırır | Düşük | `display=swap` + subset kullan |
| #155 Greek chart bug #156 ile ilişkili olabilir | Orta | #156 çözüldükten sonra #155'i tekrar test et |

---

## Checklist — Wave Tamamlanma Kriterleri

### Wave 0 ✅
- [ ] Greek NT sayfasında 12,000px void yok
- [ ] `/keyword-search/root/*` sayfaları auth gerektirmiyor (read-only)

### Wave 1 ✅
- [ ] Cormorant Garamond + Manrope font'ları yüklü
- [ ] CSS custom properties tanımlı (accent, text, bg)
- [ ] Footer: Watermark küçültülmüş/kaldırılmış
- [ ] Footer: Link kontrast WCAG AA geçiyor
- [ ] Footer: Grid alignment düzgün

### Wave 2 ✅
- [ ] Hero: Yeni font, amber accent, spacing fix
- [ ] Carousel: İtalik kaldırılmış, pagination büyütülmüş
- [ ] CTA: Headline birleştirilmiş, kontrast artırılmış
- [ ] Features: Glassmorphism backdrop-filter eklendi
- [ ] Agents: Hierarchy düzeltildi, kontrast artırıldı
- [ ] How It Works: Serif/sans clash çözüldü, gap fix

### Wave 3 ✅
- [ ] Search: Empty state eklendi, dil birliği sağlandı
- [ ] Compare: Empty state eklendi, dil birliği sağlandı
- [ ] Sign-In: Terminoloji birliği, dev artifacts kaldırıldı

### Wave 4 ✅
- [ ] Empty State: Örnek aramalar eklendi, amber alert → nötr
- [ ] Browse Grid: Arapça font (Scheherazade New), RTL layout
- [ ] Quran Root: Scrollbar fix, padding, rozet renk birliği
- [ ] Hebrew Root: Helper text bug fix, chart label, line-height
- [ ] Greek Root: Chart render fix, helper text, derived words gruplandırma
