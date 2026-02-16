# Kuran Arapça "ktb" Kök Bilgi (Üst) — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

Sanki bir fintech dashboard'una dini metin arama motoru giydirmişsiniz. Görsel kimlik şizofren: aynı ekranda mor, yeşil, turuncu, sarı — hangi renk ne anlama geliyor, MIT mezunu bile çözemez. Sol kart boğuluyor — scrollbar'ı var ama içerik 4 satır. Arapça kök ortaya bastırılmış ama altındaki Türkçe açıklama sola yaslı. **Karar verin: merkezli mi, soldan mı?**

"Accuracy Verification" butonu, bilgi kartında en göze çarpan şey olmuş. **BU BİR SEÇENEKLİ DERS SAYFASı MI?** Butonun ne işe yaradığını okumak için 3 satır ince metin okumak zorundayım.

Sağdaki grafik temiz, ama barların sonunda **rakam yok**. Kullanıcı gözle mi ölçsün? "Al-Baqarah 67 kez geçiyor" yazmak 5 satır CSS miydi?

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Başarılı:** Arapça kök (كتب) en üstte, 48px+ boyutta, merkezi odak noktası doğru.
- **Başarısız:** Hiyerarşi "Kök → Sayı → Rozet → Tanım → Bilgi Metni → Buton" şeklinde ilerliyor ama "Medium" rozeti turuncu dikkat çekiyor ve sayıyı gölgede bırakıyor. Renk = hiyerarşi olmamalı.
- **Başarısız:** "Accuracy Verification" butonu billboard gibi, bilgi metnini öldürmüş.

### Whitespace (Negatif Alan)
- **Padding Felaketi:** Sol kartın iç kenar boşlukları 12px civarında, metin sol kenara yapışmış. Profesyonel standart minimum 20-24px.
- **Scrollbar Trajedisi:** Kart içeriği 400px, kart yüksekliği 380px mi? Gereksiz scrollbar estetik cinayeti.
- **Dikey Boşluk:** "Accuracy Verification" butonunun altındaki "MORPHOLOGICAL FORMS" başlığı butona yapışmış (margin-bottom: 8px?). Minimum 24px olmalı.
- **Graph Label Gap:** Surah isimleriyle grafik barları arasında 40-50px boşluk var, göz sıçrıyor. 16-20px yeter.

### Typography
- **Font Seçimi:** Arapça font okunaklı ve geleneksel (muhtemelen Amiri ya da Traditional Arabic). Latin metin sans-serif, tutarlı.
- **Font Ağırlıkları:** "319 Occurrences" medium, "Definition" semi-bold görünüyor. **Tutarsızlık.**
- **Kontrast Hatası:** "ROOT INFORMATION" altındaki açıklama metni gri (#71717A benzeri), koyu arka planda okunabilirlik eşiği sınırda. WCAG AA standartı için kontrast oranı en az 4.5:1 olmalı.

### Renk Paleti
- **Tema:** Koyu (black/zinc-950) zemin, mor (indigo-600/500) aksan rengi.
- **Renk Kaosu:**
  - Mor (butonlar, grafik barları)
  - Yeşil (#10B981 - "Definition")
  - Turuncu (#F59E0B - "Medium")
  - Sarı (#FCD34D - "Experimental" uyarı banner'ı)
  
  **4 farklı aksan rengi aynı görünümde.** Görsel dil yok, renk kodlaması sistemi yok. "Definition" niye yeşil? Yeşil başarı mı, tanım mı ifade ediyor?

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **GEREKSIZ SCROLLBAR**  
Sol kart scrollbar gösteriyor ama içerik sığıyor. Fixed height verilmiş (`h-96` ya da `max-h-[400px]`).  
🔧 Fix: `h-auto min-h-[320px]` kullan, scrollbar sadece gerektiğinde görünsün. Alternatif: `overflow-y: auto` yerine `overflow-y: hidden` kullan ve kartı içeriğe göre genişlet.

```css
.root-info-card {
  height: auto;
  min-height: 320px;
  overflow-y: hidden; /* veya auto */
}
```

❌ **PADDING İHMALİ**  
Sol kartın iç kenar boşlukları 12px, metin duvara çarpıyor.  
🔧 Fix: `p-6` (24px) veya `p-8` (32px) kullan.

```tsx
<Card className="p-8"> {/* 12px değil, 32px */}
```

❌ **BUTON ALTINDA NEFES YOK**  
"Accuracy Verification" ile "MORPHOLOGICAL FORMS" arası 8px.  
🔧 Fix: `mb-8` ekle.

```tsx
<Button className="mb-8"> {/* mb-4 yerine mb-8 */}
```

❌ **ARAPÇA VE TÜRKÇE HİZALAMA ÇATIŞMASI**  
Arapça kök merkez, altındaki Türkçe metin sol. Göz zigzag çiziyor.  
🔧 Fix: İkisini de merkeze al ya da ikisini de sola al. Kararsızlık kabul edilemez.

```tsx
<div className="text-center"> {/* hem kök hem açıklama */}
  <p className="text-6xl">كتب</p>
  <p className="text-center text-sm text-gray-400">...</p>
</div>
```

❌ **ARAPÇA-PARANTEZ KERNING**  
"كتب (keteb)" ifadesinde parantez Arapça harfe yapışık.  
🔧 Fix: Arapça ve Latin karakterler arası boşluk ekle.

```tsx
<span dir="rtl">كتب</span> <span>(keteb)</span>
```

❌ **GRAFIK BARLARDA RAKAM YOK**  
Kullanıcı Al-Baqarah'ın 67 kez geçtiğini tahmin etmeli.  
🔧 Fix: Barların sonuna değer ekle.

```tsx
<Bar dataKey="occurrences">
  <LabelList dataKey="occurrences" position="right" fill="#fff" />
</Bar>
```

❌ **RENK KODLAMASI SİSTEMİ YOK**  
Yeşil, turuncu, mor, sarı — ne anlama geliyor?  
🔧 Fix: Tek aksan rengi (mor) kullan. Yeşil rozeti `bg-indigo-600` yap, turuncu rozeti kaldır ya da `bg-indigo-400` kullan.

```tsx
<Badge className="bg-indigo-600">Definition</Badge>
<Badge className="bg-indigo-400">Medium</Badge>
```

❌ **"DETECTED: BUCKWALTER..." SAHİPSİZ**  
Yeşil "Detected: Buckwalter Latin..." metni iki kart arasında asılı, hangi bölüme ait belli değil.  
🔧 Fix: Sol kartın içine taşı, başlık olarak kullan veya search bar'ın altına yapıştır.

```tsx
<div className="mb-2 text-sm text-emerald-500">
  Detected: Buckwalter Latin...
</div>
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Sol Kart (Root Information)
```
┌──────────────────────────────────┐
│  [DETECTED: Buckwalter]          │ ← Yeşil, 12px, üstte
│                                  │
│          كتب                     │ ← 56px, center, bold
│       (keteb - to write)         │ ← 14px, center, gray-400
│                                  │
│  ┌────────────┐ ┌──────────────┐│
│  │ 319        │ │ Definition   ││ ← Yan yana, eşit genişlik
│  │ Occurrences│ │ [icon]       ││
│  └────────────┘ └──────────────┘│
│                                  │
│  [Medium] ← Badge, 16px solda    │
│                                  │
│  [4 satır açıklama metni]        │ ← 14px, text-gray-300, leading-6
│                                  │
│  [Accuracy Verification ↗]       │ ← Outline, mb-8
│                                  │
│  MORPHOLOGICAL FORMS             │ ← 12px, uppercase, tracking-wider
└──────────────────────────────────┘

Padding: 32px (p-8)
Height: auto (min-h-[320px])
Overflow: hidden
```

### Sağ Kart (Surah Distribution)
```
┌────────────────────────────────────┐
│  SURAH DISTRIBUTION                │
│                                    │
│  Al-Baqarah     ████████████ 67    │ ← Değerler bar sonunda
│  Ali 'Imran     ████████ 43        │
│  Al-Ma'idah     ██████ 32          │
│  An-Nisa'       █████ 26           │
│  ...                               │
└────────────────────────────────────┘

Label-Bar Gap: 16px (değil 40px)
Bar Labels: LabelList position="right"
```

### Renk Paleti (Tek Aksan)
```
Primary: Indigo-600 (#4F46E5)
Secondary: Indigo-400 (#818CF8)
Success/Info: Emerald-500 (#10B981) — sadece bilgi mesajları için
Warning: Amber-500 (#F59E0B) — sadece experimental banner için
```

## 5. PUANLAMA

| Kriter            | Puan | Neden                                                                 |
|-------------------|------|-----------------------------------------------------------------------|
| Estetik           | 4/10 | Renk kaosu, scrollbar felaketi, hizalama tutarsızlığı.              |
| Kullanılabilirlik | 5/10 | Grafik barlarında rakam yok, buton bilgi metnini öldürmüş.          |
| Profesyonellik    | 3/10 | Gereksiz scrollbar, padding ihmali, renk kodlaması sistemi yok.      |

**TOPLAM: 4/10**

---

**SON SÖZ:** Bu sayfa bir aile fotoğrafı gibi — herkes farklı tarafa bakıyor, kimse aynı ışıkta değil. Tek bir görsel dil seçin ve ona sadık kalın. Scrollbar'ı çıkarın. Barların sonuna rakam ekleyin. Padding'leri ikiye katlayın. **O zaman belki 6/10 olur.**
