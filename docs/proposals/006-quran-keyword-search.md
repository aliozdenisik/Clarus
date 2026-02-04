# RFC-006: Kur'an Anahtar Kelime Arama

**Status**: Proposed
**Created**: 2026-02-01
**Effort**: High
**Hedef Kitle**: Akademisyenler ve araştırmacılar

---

> **⚠️ ZORUNLU ÖN OKUMA — BU ADIM ATLANAMAZ**
>
> Bu RFC'yi planlama veya uygulamaya geçirmeden önce aşağıdaki iki belge **baştan sona** okunmalıdır.
> Belgeler okunmadan yapılan plan veya uygulama **geçersiz** kabul edilir.
> İki belge farklı mimari yaklaşımlar sunmaktadır; çelişki tablosu bu RFC içinde yer almaktadır.
> Uygulama kararları bu çelişkilerin çözümüne bağlıdır.
>
> **Klasör yolu (repo kökünden):** `Kuran-Arapça-Morfolojik-Arama-Çözümleri/`
>
> | # | Belge | Dosya Yolu (repo kökünden) | Odak |
> |---|-------|---------------------------|------|
> | **Belge A** | [`Kuran Arapça Morfolojik Arama Çözümleri.md`](../../Kuran-Arapça-Morfolojik-Arama-Çözümleri/Kuran%20Arapça%20Morfolojik%20Arama%20Çözümleri.md) | `Kuran-Arapça-Morfolojik-Arama-Çözümleri/Kuran Arapça Morfolojik Arama Çözümleri.md` | PostgreSQL-merkezli deterministik morfolojik arama |
> | **Belge B** | [`Kur'an Arapçası Arama Motoru Geliştirme.md`](../../Kuran-Arapça-Morfolojik-Arama-Çözümleri/Kur'an%20Arapçası%20Arama%20Motoru%20Geliştirme.md) | `Kuran-Arapça-Morfolojik-Arama-Çözümleri/Kur'an Arapçası Arama Motoru Geliştirme.md` | Çok katmanlı hibrit mimari (morfolojik + semantik + ontoloji) |

---

## Summary

Kur'an-ı Kerim içinde morfolojik kök tabanlı anahtar kelime araması yapılabilmesini sağlayan, akademisyenlere ve araştırmacılara yönelik bir araştırma aracı. Sistem, Latin harfleriyle girilen bir kelimeden Arapça kökü tespit ederek, o kökten türeyen tüm kelimelerin geçtiği ayetleri, frekans analizini ve sure dağılımını sunar.

## Motivation

Akademisyenler ve ilahiyat araştırmacıları, Kur'an üzerinde kavram bazlı çalışmalar yürütürken belirli bir kelimenin Kur'an genelinde kaç kez ve hangi bağlamlarda geçtiğini tespit etme ihtiyacı duyuyor. Şu anda sistem yalnızca anlamsal (semantic) arama desteklediğinden, kesin frekans analizi ve kelime bazlı istatistiksel sorgulama yapılamıyor.

Arapça, "kök ve vezin" (root and pattern) sistemine dayalı bükümlü bir dildir. Basit metin eşleştirme (LIKE sorguları) bu yapıda başarısız olur. Örneğin K-T-B kökünden hem "Kitab" (kitap), hem "Kataba" (yazdı), hem "Kâtib" (yazıcı) türer. Kullanıcı bunlardan birini aratınca diğerlerine de ulaşabilmeli — bu ancak morfolojik kök bazlı aramayla mümkündür.

Araştırmacıların büyük çoğunluğu Arap alfabesiyle doğrudan giriş yapamıyor. Latin harfleriyle arama yapabilmeleri, aracın uluslararası akademik çevrelerde kullanılabilirliğini önemli ölçüde artıracaktır.

## Proposal

Kullanıcı, Latin harfleriyle bir anahtar kelime veya kavram girerek Kur'an metni üzerinde araştırma yapabilmeli. Sistem şu bilgileri sunmalı:

- **Frekans analizi**: Kelimenin (ve tüm kök türevlerinin) Kur'an genelinde toplam kaç kez geçtiği
- **Ayet listesi**: Kelimenin geçtiği ayetlerin sure adı, ayet numarası ve tam metin ile birlikte listelenmesi
- **Sure dağılımı**: Kelimenin hangi surelerde ve kaçar kez geçtiğine dair dağılım bilgisi
- **Referans formatı**: Akademik atıf yapılabilecek şekilde sure:ayet formatında sonuçlar
- **Morfolojik kök bağlantısı**: Aranan kelimenin hangi kökten türediği ve aynı kökten türeyen diğer kelimeler

---

## Referans Belgeler Arası Karşılaştırma

İki belge aynı problemi (Kur'an'da morfolojik arama) ele alır ancak **farklı mimari felsefeler** sunar. Aşağıdaki tablo, uygulayıcının kararlarını şekillendirmesi gereken çelişki ve ayrışma noktalarını belgeler.

### Karşılaştırma Tablosu

| # | Konu | Belge A (PostgreSQL-Merkezli) | Belge B (Hibrit Mimari) | Çelişki Seviyesi |
|---|------|-------------------------------|--------------------------|------------------|
| 1 | **Arama Motoru** | PostgreSQL tek başına yeterli. GIN + B-Tree + RUM indeksleri ile tüm arama ihtiyaçları karşılanır. | Elasticsearch veya Whoosh önerilir. PostgreSQL arama motoru olarak ele alınmaz. | 🔴 **Doğrudan çelişki** |
| 2 | **Semantik Arama** | Açıkça **reddeder**: "Vektör veritabanlarına ihtiyaç yoktur. Kuran'ın kelime türetim sistemi yeterli bir ağ sağlar." | Açıkça **savunur**: AraBERT/FAISS ile semantik vektör araması önerir. "Kelime geçmese bile konuyu bulur." | 🔴 **Doğrudan çelişki** |
| 3 | **Veri Kaynağı (Referans Metin)** | `mustafa0x/quran-morphology` tek kaynak olarak yeterli. Metin + morfoloji aynı kaynaktan. | Çift kaynak: Tanzil.net (referans metin) + Quranic Arabic Corpus (morfoloji). İki ayrı katman. | 🟡 **Yaklaşım farkı** |
| 4 | **Kök Çıkarım Aracı (Birincil)** | Tashaphyne (hafif stemmer) birincil algoritmik yedek. Veritabanı lookup'ı asıl çözüm. | CAMeL Tools (ağır siklet akademik çözüm) birincil öneri. Farasa segmentasyon için. Tashaphyne sadece hafif alternatif. | 🟡 **Öncelik farkı** |
| 5 | **Normalizasyon Katmanı** | PostgreSQL seviyesinde: özel `arabic.rules` dosyası + `unaccent` eklentisi ile veritabanı içi normalizasyon. | Python seviyesinde: PyArabic ile uygulama katmanında 5 aşamalı normalizasyon pipeline'ı. | 🟡 **Uygulama katmanı farkı** |
| 6 | **Metin Gösterimi** | `content_uthmani` (görüntüleme) ve `content_clean` (arama) aynı PostgreSQL tablosunda iki sütun. | `quran-uthmani.xml` (görüntüleme) ve `quran-simple-clean.xml` (arama) Tanzil'den ayrı dosyalar olarak. | 🟢 **Aynı prensip**, farklı kaynak |
| 7 | **Ontoloji Desteği** | Ele alınmaz. Kapsam dışı. | Önerir: RDF/OWL ile Kur'an ontolojisi, kavram hiyerarşisi ("Su" → "Yağmur", "Nehir", "Deniz"), query expansion. | 🟡 **Kapsam farkı** |
| 8 | **Bulanık Arama (Fuzzy)** | PostgreSQL `pg_trgm` eklentisi ile trigram benzerliği. `token_clean % 'mumin'` sorgusu. | Elasticsearch synonym graph filter ile eş anlamlılar grafiği. Modern → Kur'an karşılığı yönlendirmesi. | 🟡 **Mekanizma farkı** |
| 9 | **ETL Veri Hassasiyeti** | Açık ve kesin: agresif normalizasyon betikleri (cinsiyet silen fonksiyonlar) **engellenecek**. Kayıpsız aktarım. "Müminat" ile "Mümin" ayrımı korunacak. | Belirtilmez. Genel normalizasyon kuralları verilir ama veri kaybı riski ele alınmaz. | 🟡 **Detay farkı** |
| 10 | **NLTK ISRI Stemmer** | Bahsedilmez. | Açıkça **uyarır**: "Kaçınılması gereken tuzak. Kök harfleriyle ek harfleri karıştırır. Kutsal metin hassasiyeti için önerilmez." | 🟢 **Tamamlayıcı** |
| 11 | **Performans Tahmini** | Somut: "77.430 kelime küçük veri. Tümü RAM'e sığar. Kök sorgusu 1-2ms. Toplam 50-100MB." | Belirtilmez. Elasticsearch/FAISS için performans tahmini yok. | 🟡 **Detay farkı** |
| 12 | **Lemma vs Kök Ayrımı** | Hem root hem lemma sütunu tutar, ancak lemma bazlı aramayı derinlemesine ele almaz. | Açıkça vurgular: "Kök her zaman yeterli değildir. K-T-B kökü hem 'yazmak' hem 'kitap' üretir." Al-Fanous örneğini verir. Lemma bazlı arama "morfolojik aramanın zirvesi" olarak tanımlanır. | 🟡 **Derinlik farkı** |

### Özet Yorum

- **Belge A**, bu RFC'nin PostgreSQL gereksinimi ile doğrudan uyumludur ve deterministik, ölçülebilir bir mimari sunar.
- **Belge B**, daha geniş bir vizyon çizer (semantik + ontoloji) ve bazı konularda (lemma ayrımı, ISRI uyarısı, CAMeL Tools) Belge A'yı tamamlar.
- İki belge **kök bazlı arama zorunluluğu, hibrit kök çıkarımı (DB lookup + algoritmik yedek) ve çift katmanlı metin mimarisi (görüntüleme + arama)** konularında mutabıktır.

---

## Tasarım Kararları (Referans Belgelerden)

Aşağıdaki kararlar, yukarıdaki iki belgenin mutabık olduğu noktalar ve bu RFC'nin gereksinimleri doğrultusunda belirlenmiştir:

### 1. Morfolojik Kök Bazlı Arama — Zorunlu
*Her iki belge mutabık.* Basit metin eşleştirme yeterli değildir. Arama, kelimenin **morfolojik kökü** ve **lemması** üzerinden yapılacaktır. "İnsanlar" araması "insan" kökünü kapsamalı. "Kitab" araması "Yazdı", "Yazılan", "Kâtib" sonuçlarını da getirmeli.

### 2. Arapça Orijinal Metin Üzerinde Arama — Evet
*Her iki belge mutabık (çift katmanlı mimari).* Hem Türkçe meal hem Arapça orijinal metin üzerinde arama yapılacak. Çift katmanlı veri mimarisi:
- **Görüntüleme katmanı**: Harekeli orijinal metin (Resm-i Osmani)
- **Arama katmanı**: Harekesiz normalize edilmiş metin + kök/lemma indeksleri

### 3. Latin Girdi — Türkçe Meal Üzerinde Doğrudan Arama
Kullanıcının Latin harfleriyle girdiği kelime öncelikle Türkçe meal metinleri üzerinde aranacak. Arapça metin araması için Python tarafında normalizasyon ve kök çıkarımı katmanları devreye girecek.

### 4. Veri Kaynağı — mustafa0x/quran-morphology
*Belge A'nın seçimi.* Quranic Arabic Corpus'un iyileştirilmiş fork'u. 77.430 kelimenin her biri için insan tarafından doğrulanmış morfolojik etiketler, kökler ve lemmalar içerir. Agresif normalizasyon betikleri (cinsiyet silen fonksiyonlar) devre dışı bırakılacak — kayıpsız veri aktarımı.

### 5. PostgreSQL Şeması — Hiyerarşik Normalize Model
*Belge A'nın mimarisi.* Bu RFC PostgreSQL kullanımını şart koşar.
```
surahs (114 sure) → ayahs (6.236 ayet) → words (77.430 kelime)
```
`words` tablosunda `root`, `lemma`, `pos_tag` sütunları. B-Tree indeks kök aramaları için, GIN indeks tam metin araması için.

### 6. Hibrit Kök Çıkarımı
*Her iki belge mutabık (DB lookup önce, algoritma yedek).*
1. Önce kullanıcının kelimesi `words.token_clean` sütununda aranır (exact match → %100 doğruluk)
2. Bulunursa veritabanındaki insan-doğrulamalı kök kullanılır
3. Bulunamazsa algoritmik kök tahmini yapılır

---

## Expected Outcome

- Akademisyen "insan" yazıp aradığında, bu kelimenin Kur'an mealinde geçtiği tüm ayetleri, toplam sayıyı ve sure dağılımını görebilir.
- Kök bazlı arama sayesinde bir kelimenin tüm morfolojik türevleri de sonuçlara dahil olur.
- Tüm aramalar Latin alfabesiyle yapılır; Arapça karakter girişi gerekmez.
- Sonuçlar akademik referans formatında (sure adı + ayet numarası) listelenir.
- PostgreSQL üzerinde B-Tree ve GIN indeksleri ile milisaniye düzeyinde sorgu performansı.
- Araştırmacılar sonuçları akademik çalışmalarında kaynak olarak kullanabilir.

## Open Questions

- Sonuçların dışa aktarımı (CSV, BibTeX) desteklenecek mi?
- POS filtreleme (sadece fiiller, sadece isimler) kullanıcıya sunulacak mı?
- Karşılaştırma tablosundaki çelişki #1 (PostgreSQL vs Elasticsearch): Bu RFC PostgreSQL'i şart koşar, ancak gelecekte Elasticsearch katmanı eklenecek mi?
- Karşılaştırma tablosundaki çelişki #2 (Semantik arama): Mevcut Qdrant altyapısı ile semantik katman da entegre edilecek mi, yoksa bu RFC yalnızca deterministik morfolojik aramayı mı kapsar?
- Algoritmik kök çıkarımda Tashaphyne mi (Belge A) yoksa CAMeL Tools mu (Belge B) tercih edilecek?
