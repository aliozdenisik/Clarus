# G1125 (γράφω) Root Info Top — UI/UX Denetim Raporu

## 1. İLK İZLENİM VE "ROAST"

Bu sayfa dua edip çok iyi bir insan olsam belki bir gün ulaşabileceğim seviyede değil — tam tersine, daha şimdiden beni terk etmiş. Sağ taraftaki DEV-ASA grafik container'ı sanki Chernobyl reaktörü gibi patlamış ve geriye sadece %50 ekran alanını kaplayan siyah bir void bırakmış. 

Kullanıcı "Yunanca kelime" araması yapıyor ama ona "Arabic (كتب) and Buckwalter Latin (ktb) destekleriz" diye yardım mesajı gösteriyorsun. **ÇEVİRİCİ Mİ BU, YOKSA BİR TERCÜME HATA MÜZESI Mİ?**

"30 Unique Word" yazıyor. Word. TEK. Dil bilgisi dersi veren bir teoloji aracında gramer hatası. Harika. Gordon Ramsay'in mutfağında donmuş balıkla gelip "Taze efendim" demek gibi.

Transliterasyon "graphō" o kadar sönük ki, kullanıcıyı zoom yapmaya zorluyor. Bu bir accessibility suçu.

---

## 2. HEURISTIC ANALİZ

### Visual Hierarchy

**✅ Başarılı:**
- "γράφω" kelimesi büyük serif font ve beyaz renkle doğru biçimde vurgulanmış
- 190-30-22 istatistik sayıları net ve okunabilir
- "Search Root" / "All Words" toggle butonu kontrast açısından güçlü

**❌ Başarısız:**
- Sağ yarı tamamen boş — sayfanın %50'si değer üretmiyor
- "Derived Words" başlığı üstündeki istatistik kutularına çok yakın, mantıksal grup ayrımı yok
- Turuncu "Experimental Feature" kutusu asıl sonuçları (Derived Words/Verses) aşağı iterek görsel gürültü yaratıyor

### Whitespace (Negatif Alan)

**Komedi çetesi:**
- Sol kısım: Sıkışık, nefes alamıyor, "30 Unique Word" ile "Derived Words" arası 8px
- Sağ kısım: 12.000px boşluk, içinde tek piksel içerik yok, sadece arka plan rengi
- **Denge:** Yok. Sol yoğun bilgi bombardımanı, sağ çöl.

### Typography

**Font Choices:**
- Sans-serif UI + Serif Yunanca kelime = **doğru karar**, akademik ve modern dengeyi yakalamış
- "graphō" transliterasyonu (#9CA3AF gibi bir gri) çok sönük — #E5E7EB'ye çıkarılmalı

**Font Size Hierarchy:**
- "γράφω" çok büyük (text-6xl) ama "graphō" çok küçük (text-sm), aralarında adım yok
- Derived Words butonlarındaki kelimeler küçük, aksan işaretleri birbirine giriyor

**Gramer Hatası:**
```
❌ "30 Unique Word"
✅ "30 Unique Words"
```

### Renk Paleti

**Marka Uyumu:**
- Indigo/Mor (#6366F1) vurgu renkleri Clarus'un AI kimliğiyle uyumlu
- Amber (#F59E0B) uyarı kutusu dikkat çekiyor ama çok fazla yer kaplıyor
- Koyu gri (#1F2937) kartlar beyaz metin üzerinde okunabilir

**Kontrast Sorunları:**
- Transliterasyon metni (graphō) arka planla kaynaşıyor — WCAG AA fail
- Sağdaki boş grafik container'ı (#111827 gibi bir ton) arka planla neredeyse aynı, kullanıcı bunun bir bug mu yoksa tasarım tercihi mi olduğunu anlamıyor

---

## 3. KRİTİK HATALAR VE ÇÖZÜMLER

### ❌ **SHOWSTOPPER: Grafik Render Edilmemiş**
Sağ taraftaki "Book Distribution Chart" container'ı tamamen boş. 43,055 vektör içeren bir veritabanında grafik render edilemiyorsa, bu frontend katmanında kritik bir bug.

🔧 **Fix:**
```tsx
// RootBrowser.tsx veya benzer component
{bookDistributionData.length === 0 ? (
  <div className="flex flex-col items-center justify-center h-full text-gray-400">
    <BarChart3 className="w-16 h-16 mb-4 opacity-50" />
    <p className="text-sm">No distribution data available</p>
  </div>
) : (
  <BookChart data={bookDistributionData} />
)}
```

### ❌ **Context Mismatch: Yanlış Yardım Mesajı**
Kullanıcı **Yunanca** aramada, arama kutusunun altında "Arabic (كتب) and Buckwalter Latin (ktb)" yardımı gösteriliyor.

🔧 **Fix:**
```tsx
// KeywordSearchInput.tsx
const helpText = collection === 'greek_nt' 
  ? "Supports Strong's numbers (e.g., G1125) or Greek text (γράφω)"
  : "Supports Arabic (كتب) and Buckwalter Latin (ktb)";
```

### ❌ **Gramer Hatası**
"30 Unique Word" → çoğul olmalı.

🔧 **Fix:**
```tsx
{uniqueWordCount} Unique Word{uniqueWordCount !== 1 ? 's' : ''}
```

### ❌ **Düşük Kontrast: Transliterasyon**
"graphō" metni (#9CA3AF) çok sönük.

🔧 **Fix:**
```tsx
<p className="text-sm text-gray-300 mt-1">{transliteration}</p>
// Değiştir: text-gray-500 → text-gray-300
```

### ❌ **Dengesiz Spacing**
"Derived Words" başlığı istatistik kutularına çok yakın.

🔧 **Fix:**
```tsx
<div className="mt-8 space-y-4">
  <h3 className="text-lg font-semibold">Derived Words</h3>
  {/* İstatistik kutularıyla araya mt-8 ekle */}
</div>
```

### ❌ **Turuncu Uyarı Kutusu Gürültü Yaratıyor**
"Experimental Feature" kutusu çok fazla dikey alan kaplıyor.

🔧 **Fix:**
```tsx
// Kutuyu daha kompakt yap, veya dismissible yap
<Alert className="bg-amber-900/20 border-amber-700/50 py-3">
  <AlertCircle className="h-4 w-4" />
  <AlertDescription className="text-sm">
    Experimental: Results may vary. <button className="underline">Learn more</button>
  </AlertDescription>
</Alert>
```

---

## 4. REÇETE (Nasıl Görünmeliydi?)

### İdeal Layout:
```
┌──────────────────────────────────────────────────────────┐
│  [Back] Greek New Testament                               │
│                                                            │
│  γράφω                    [Book Distribution Chart]       │
│  graphō (açık gri)        ┌───────────────────────┐      │
│                           │ █████ Matthew    45%   │      │
│  190 Occurrences          │ ███ Mark         22%   │      │
│  30 Unique Words          │ ██ Luke          18%   │      │
│  22 Books                 │ █ John           15%   │      │
│                           └───────────────────────┘      │
│  ⚠️ Experimental feature (kompakt, dismissible)          │
│                                                            │
│  Derived Words (mt-8 ile ayrılmış)                        │
│  [gegrammena] [graphein] [graphō] ...                    │
└──────────────────────────────────────────────────────────┘
```

### Renk Paletine Uyum:
- Grafik çubukları: Indigo gradient (#6366F1 → #818CF8)
- Hover: #A5B4FC
- Transliterasyon: #E5E7EB (şu anki #9CA3AF yerine)
- Uyarı kutusu: bg-amber-900/10 (şu anki /20 yerine daha soft)

---

## 5. PUANLAMA

| Kriter | Puan | Açıklama |
|--------|------|----------|
| **Estetik** | 4/10 | Serif+sans mix başarılı ama sağ yarı çöl. Renk paleti tutarlı ancak kontrast sorunları var. |
| **Kullanılabilirlik** | 3/10 | Grafik render olmamış, yardım mesajı yanlış context'te, transliterasyon okunamıyor. |
| **Profesyonellik** | 2/10 | Gramer hatası, boş container, uyarı kutusu gürültü. Üretim ortamına çıkmamalıydı. |
| **Fonksiyonellik** | 1/10 | Ana özellik (grafik) çalışmıyor. Sayfa %50 boşlukla render ediliyor. |

**TOPLAM: 2.5/10**

---

## SONUÇ

Bu sayfa Steve Jobs'un "insanely great" değil, "insanely broken" kategorisinde. Grafik render edilmemiş, yardım mesajı yanlış, gramer hatası var. Sağ yarı ekranın tamamen boş olması, kullanıcıyı gereksiz yere scroll yapmaya zorluyor. 

**Acil Aksiyonlar:**
1. Grafik render bug'ını fix et veya fallback UI ekle (empty state)
2. Context-aware help text yaz (Yunanca için Strong's + Greek text)
3. Gramer hatasını düzelt
4. Transliterasyon kontrastını artır
5. Uyarı kutusunu kompakt yap veya dismissible yap
6. Derived Words başlığına üstten 32px (mt-8) margin ekle

Bu sayfayı beta'dan kaldır. Şu haliyle production'da ne işi var?
