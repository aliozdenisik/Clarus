# İbranice Eski Ahit "H3789" Kök Bilgi (Üst) — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

**KRİTİK BUG:** Helper text "Supports Arabic (كتب) and Buckwalter Latin (ktb)" yazıyor. **BU İBRANİCE SEKMESI!** Arapça helper text burada ne arıyor? Copy-paste'ten sonra kontrol etmeyi unutmuşsunuz. Kullanıcı İbranice Strong's Number arıyor, ekran "Arapça destekliyorum" diyor. **Profesyonel intihar.**

Türev kelime chip'lerinde İbranice karakterler üstten ve alttan kırpılmış — özellikle alt satırdaki son mem (ם) harfi kesik görünüyor. **Font-size ve container height uyumsuz.**

"Unique Word" yazıyor, "Books" yazıyor. **Biri tekil, biri çoğul.** Hangi dil standardı? "Unique Words" olmalı.

Grafik temiz ama yine aynı sorun: barlarda **rakam yok**. Kullanıcı "2 Kings" 45 kez mi 48 kez mi geçiyor diye gözle mi ölçsün? X-axis scale yok, grid çizgileri o kadar soluk ki görünmüyor.

Alt bölümdeki "Search Results" başlığı ile kartlar arası boşluk 8px. **Nefes almak yasak mı?**

## 2. HEURISTIC ANALİZ

### Visual Hierarchy
- **Başarılı:** İbranice kök (כָּתַב) en üstte, 48px+ boyutta, merkezi odak noktası doğru.
- **Başarısız:** "Derived Words" başlığındaki elmas (diamond) ayracı metin baseline'ından yukarı kaymış, ortada değil.
- **Başarısız:** İstatistik kartları (Total Usage, Unique Word, Books) çok sıkışık, aralıkları dar.

### Whitespace (Negatif Alan)
- **Search Bar Helper Text:** 12px, mor renkli, okunaklı. Ama **yanlış metin** — Arapça helper text İbranice tab'da.
- **Dikey Boşluk:**
  - "Search Results" başlığı ile kartlar arası: 8px (çok dar)
  - İstatistik kartları arası gap: 12px (ok)
  - Grafik barları ile kitap isimleri arası: 16px (ok)
- **Türev Kelime Chip'leri:** Chip içinde padding yetersiz, İbranice karakterler üstten ve alttan kırpılıyor.

### Typography
- **İbranice Font:** Serif font, nikkud (sesli harfler) ile okunaklı.
- **Tutarsızlık:** "Unique Word" tekil, "Books" çoğul. Standart yok.
- **Transliterasyon:** "ka.tav" formatı açık ve okunaklı, parantez içinde güzel yerleşmiş.

### Renk Paleti
- **Tema:** Koyu (black/zinc-950) zemin, mor (indigo-600) aksan.
- **Tutarlı:** Bütün renkler mor temasında, renk kaosu yok (Arapça tab'daki gibi yeşil/turuncu rozet karmaşası yok).
- **Experimental Uyarı:** Turuncu (amber-500) banner, dikkat çekiyor ama çok iri.

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

❌ **HELPER TEXT BUG — KRİTİK**  
İbranice tab'da Arapça helper text: "Supports Arabic (كتب) and Buckwalter Latin (ktb)".  
🔧 Fix: İbranice için doğru helper text yaz.

```tsx
{collection === 'hebrew_old_testament' && (
  <p className="text-xs text-indigo-400">
    Supports Hebrew characters (כתב) or Strong's numbers (H3789)
  </p>
)}
```

❌ **"UNIQUE WORD" TEKİL/ÇOĞUL TUTARSIZLIĞI**  
"Unique Word" tekil, "Books" çoğul.  
🔧 Fix: "Unique Words" yap.

```tsx
<div className="text-xs text-gray-400 uppercase tracking-wider">
  Unique Words {/* "Word" değil */}
</div>
```

❌ **TÜREV KELİME CHIP'LERİNDE CLIPPING**  
İbranice karakterler üstten ve alttan kırpılıyor, özellikle final mem (ם).  
🔧 Fix: `py-2` ve `leading-relaxed` kullan.

```tsx
<div className="inline-flex flex-col items-center gap-1 px-3 py-2 bg-zinc-900 rounded-lg">
  <span className="text-lg font-hebrew leading-relaxed">כְּתָבְנָה</span>
  <span className="text-xs text-gray-400">ktbnh</span>
</div>
```

❌ **GRAFİK BARLARDA RAKAM YOK**  
"2 Kings" barının uzunluğu ne kadar? Kullanıcı tahmin etmeli.  
🔧 Fix: Barların sonuna değer ekle.

```tsx
<Bar dataKey="occurrences">
  <LabelList dataKey="occurrences" position="right" fill="#E4E4E7" fontSize={12} />
</Bar>
```

❌ **"SEARCH RESULTS" BAŞLIĞI KARTLARA ÇOK YAKIN**  
Başlık ile kartlar arası 8px, nefes yok.  
🔧 Fix: `mb-6` kullan (24px).

```tsx
<h2 className="text-xl font-semibold mb-6"> {/* mb-2 değil */}
  Search Results
</h2>
```

❌ **ELMAS (DIAMOND) AYRACININ HİZALAMASI**  
"Derived Words" başlığındaki elmas baseline'dan yukarı kaymış.  
🔧 Fix: `inline-flex items-center` kullan.

```tsx
<h3 className="inline-flex items-center gap-2 text-sm font-medium">
  <DiamondIcon className="w-3 h-3" />
  Derived Words
  <DiamondIcon className="w-3 h-3" />
</h3>
```

❌ **SCROLLBAR SIDEBAR VE CHART ARASINDA**  
Sol sidebar ile sağ grafik alanı arasında ince bir scrollbar görünüyor. Sol kolon fixed-height, overflow bağımsız. Layout jumping riski.  
🔧 Fix: `h-auto` kullan, scrollbar'ı kaldır.

```tsx
<div className="flex gap-6">
  <div className="flex-1 space-y-6"> {/* h-[600px] overflow-y-auto değil */}
```

❌ **GRAFİK GRID ÇİZGİLERİ ÇOK SOLUK**  
Noktalı grid çizgileri neredeyse görünmüyor, değer takibi zor.  
🔧 Fix: Opacity'yi artır.

```tsx
<CartesianGrid 
  strokeDasharray="3 3" 
  stroke="#3F3F46" 
  opacity={0.3} // 0.1 değil
/>
```

## 4. REÇETE (Nasıl Görünmeliydi?)

### Helper Text (İbranice Tab)
```tsx
<p className="text-xs text-indigo-400">
  Supports Hebrew characters (כתב) or Strong's numbers (H3789)
</p>
```

### Türev Kelime Chip
```
┌──────────────┐
│   כְּתָבְנָה  │ ← 18px, leading-relaxed
│   ktbnh       │ ← 12px, text-gray-400
└──────────────┘

Padding: px-3 py-2 (12px yatay, 8px dikey)
Background: bg-zinc-900
Border-radius: rounded-lg
```

### İstatistik Kartları
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│     225      │ │      46      │ │      25      │
│ Total Usage  │ │ Unique Words │ │    Books     │
└──────────────┘ └──────────────┘ └──────────────┘

Gap: 16px (gap-4)
Tekil/Çoğul: "Unique Words" (çoğul)
```

### Grafik (Book Distribution)
```
2 Kings      ████████████████ 48
2 Chronicles ██████████████ 41
Jeremiah     ████████████ 35
Psalms       ██████████ 29

Bar Labels: LabelList position="right", fontSize={12}
Grid: stroke="#3F3F46", opacity={0.3}
```

### Başlık Hiyerarşisi
```
Word Search                       ← H1, 32px, mb-6
  Search Results                  ← H2, 20px, mb-6 (8px değil)
    Derived Words                 ← H3, 14px, inline-flex items-center
```

## 5. PUANLAMA

| Kriter            | Puan | Neden                                                                      |
|-------------------|------|----------------------------------------------------------------------------|
| Estetik           | 4/10 | Chip clipping, elmas hizalama hatası, scrollbar layout jumping riski.     |
| Kullanılabilirlik | 3/10 | Helper text bug (KRİTİK), grafik barlarında rakam yok, grid çok soluk.    |
| Profesyonellik    | 2/10 | Yanlış helper text, tekil/çoğul tutarsızlığı, testing eksikliği açık.     |

**TOPLAM: 3/10**

---

**SON SÖZ:** Arapça tab'daki helper text'i İbranice tab'a kopyalamışsınız ve **test etmemişsiniz**. Bu tek başına profesyonellik puanını çöpe atar. Chip'lerdeki clipping, tekil/çoğul tutarsızlığı, grafikteki rakam eksikliği — hepsi "acele ettik, kontrol etmedik" diyor. **Helper text'i düzeltin, chip padding'ini artırın, grafik barlarına rakam ekleyin. O zaman belki 5/10 olur.**
