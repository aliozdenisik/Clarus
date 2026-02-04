# RFC-008: Bible Keyword Search Expansion

**Status**: Proposed
**Created**: 2026-02-02
**Effort**: High
**Depends on**: RFC-006 (Quran Keyword Search), RFC-007 (Quran Keyword Search Frontend)

---

> **⚠️ ZORUNLU ÖN OKUMA — BU ADIM ATLANAMAZ**
>
> Bu RFC'yi planlama veya uygulamaya geçirmeden önce aşağıdaki belge **baştan sona** okunmalıdır.
> Belge okunmadan yapılan plan veya uygulama **geçersiz** kabul edilir.
>
> | # | Belge | Dosya Yolu (repo kökünden) | Odak |
> |---|-------|---------------------------|------|
> | **Kaynak Raporu 1** | Kutsal Kitap Metinleri Dijital Kaynak Araştırması | `Araştırmalar/Tevrat-incil-orjinal/Kutsal Kitap Metinleri Dijital Kaynak Araştırması.md` | Metinsel kaynaklar, lisanslama, veri formatları, entegrasyon stratejileri |
> | **Kaynak Raporu 2** | Kutsal Kitap Metinleri Morfolojik | `Araştırmalar/Tevrat-incil-orjinal/Kutsal Kitap Metinleri Morfolojik.md` | WLC/UXLC, SBLGNT, MorphGNT, Rahlfs LXX, 1941 Türkçe çeviri telif analizi, Codex Sinaiticus, SWORD Engine, teknik mimari |

---

## Summary

Şu an yalnızca Kur'an için çalışan morfolojik kök bazlı anahtar kelime arama sistemini, Kitab-ı Mukaddes'in **orijinal dillerine** (İbranice Eski Ahit, Yunanca Yeni Ahit, Yunanca Septuagint) genişletmek. Sistem, Kur'an Arapça kök aramasının birebir karşılığı olarak İbranice kök ve Yunanca lemma bazlı deterministik arama yapabilmeli; Strong's Concordance numaraları üzerinden diller arası çapraz referans sunabilmelidir.

İngilizce metin araması bu RFC'nin kapsamında **değildir** — mevcut semantik arama (Qdrant hybrid search) İngilizce metin erişimini zaten karşılamaktadır. Bu RFC'nin odağı, yalnızca orijinal dil kaynak metinleri üzerinde morfolojik kök bazlı akademik arama altyapısı kurmaktır.

## Motivation

Kur'an anahtar kelime araması (RFC-006), PostgreSQL üzerinde 77.430 kelime ve 1.651 Arapça kök ile morfolojik kök bazlı bir araştırma aracı sunuyor. Araştırmacı Arapça bir kök girdiğinde, o kökten türeyen tüm kelimeleri, frekans analizini ve sure dağılımını görebiliyor.

Kitab-ı Mukaddes tarafında ise bu derinlikte bir araç yok. Bir araştırmacı İbranice "כתב" (k-t-b, yazmak) kökünün Eski Ahit'te kaç kez, hangi kitaplarda ve hangi biçimlerde (כָּתַב, כְּתָב, מִכְתָּב...) geçtiğini tespit edemiyor. Yunanca "ἀγάπη" (agape, sevgi) kelimesinin Yeni Ahit'teki tüm morfolojik formlarını ve dağılımını göremiyorlar.

Mevcut semantik arama İngilizce çeviri üzerinden anlam bazlı sonuçlar verse de, **orijinal dil kök eşleştirmesi, morfolojik form analizi ve frekans dağılımı** gibi akademik gereksinimleri karşılayamaz — çünkü bunlar deterministik, kesin eşleşme gerektiren işlemlerdir.

## Mevcut Durum Analizi

### Clarus'un Şimdiki Mimarisi

| Bileşen | Kur'an Keyword Search | Bible |
|---------|----------------------|-------|
| **Veri Deposu** | PostgreSQL (`qm_surahs → qm_ayahs → qm_words`) | Yalnızca Qdrant (vektör) |
| **Kelime Sayısı** | 77.430 (morfolojik etiketli) | ~730.000 (İngilizce düz metin, etiketsiz) |
| **Orijinal Dil** | Arapça (Uthmani + Simple Clean) | Yok (İbranice/Yunanca orijinal metin indekslenmemiş) |
| **Kök Sistemi** | 1.651 Arapça kök + lemma | Yok |
| **Arama Tipi** | Morfolojik kök bazlı (deterministik) | Yalnızca semantik + BM25 (İngilizce çeviri üzerinden) |
| **Giriş** | Arapça + Latin/Buckwalter | — |
| **API** | `POST /api/keyword-search/`, `GET /roots`, `GET /root/{root}` | — |
| **Veritabanı Şeması** | `qm_surahs`, `qm_ayahs`, `qm_words` (B-Tree + GIN indeks) | — |

### Mevcut KJVA Verisi — Yalnızca İngilizce Çeviri Referansı

`bible_kjva.json` dosyası İngilizce KJVA çevirisini içerir. Bu RFC kapsamında **arama hedefi değil**, yalnızca orijinal dil ayetlerinin yanında İngilizce karşılık (`text_english`) olarak kullanılacaktır.

```json
{
  "chapter": 1,
  "verse": 1,
  "name": "Genesis 1:1",
  "text": "In the beginning God created the heaven and the earth."
}
```

Keyword search, bu İngilizce metin üzerinde değil, OSHB İbranice ve MorphGNT Yunanca orijinal metinler üzerinde çalışacaktır.

### Araştırma Raporlarından Kritik Bulgular

Kaynak raporları (bkz. Zorunlu Ön Okuma) aşağıdaki açık erişimli veri kaynaklarını tespit etmiştir:

| Kaynak | İçerik | Lisans | Clarus İçin Değer |
|--------|--------|--------|-------------------|
| **WLC/UXLC** (tanach.us / openscriptures) | Leningrad Kodeksi İbranice metin — Unicode XML, kantilyasyon, Kethiv/Qere varyantları | Metin: Kamu Malı | Eski Ahit İbranice ham metni — BHS'nin dayandığı aynı el yazması, telif sorunu yok |
| **OSHB** (openscriptures/morphhb) | WLC üzerine morfolojik etiketler + Strong's H numaraları + lemmalar | Morfoloji: CC BY 4.0 | Eski Ahit kelimelerini İbranice köklere bağlama, interlinear okuma |
| **SBLGNT** (logosbible/SBLGNT) | SBL Yunanca Yeni Ahit — Michael W. Holmes editörlüğü, NA28 ile %90+ uyum | CC BY 4.0 | ✅ Yunanca Yeni Ahit ana metin kaynağı — telif sorunu yok (NA28'den bağımsız) |
| **MorphGNT** | SBLGNT üzerine morfolojik etiketler, lemmalar, POS | CC BY 4.0 | ✅ **Mevcut** — SBLGNT morfolojik etiketlemesi olarak erişilebilir |
| **Strong's Concordance** (openscriptures/strongs) | H1-H8674 (İbranice, 8.674 giriş) + G1-G5624 (Yunanca, 5.624 giriş) → tanımlar | Kamu Malı | İngilizce ↔ orijinal dil köprüsü |
| **Rahlfs LXX (1935)** | Septuagint — CCAT morfolojik etiketli Yunanca, Deuterokanonik kitaplar dahil | Kamu Malı | Apokrif/Deuterokanonik metinlerin Yunanca orijinali + morfolojik analiz |
| **1941 Türkçe Çeviri** (seven1m/open-bibles) | Tam Kitab-ı Mukaddes Türkçe — OSIS XML (`tur-turkish.osis.xml`) | Kamu Malı (MacCallum ✝1945, 70 yıl kuralı → 1 Ocak 2016'da telif sona ermiştir) | Türkçe metin katmanı — varsayılan "Klasik Çeviri" |
| **Codex Sinaiticus** (codexsinaiticus.org) | MS 4. yy tam İncil el yazması dijital transkripsiyonu — TEI XML | CC BY-NC-SA 3.0 | İleri araştırma: orijinal el yazması katmanı (ticari olmayan) |
| **Sefaria** (Sefaria-Export) | Tanah + Yahudi yorum geleneği (Midraş, Talmud, Rashi) — JSON API + bulk export | Metin: Kamu Malı / Çeviriler: karışık (API'da `license` alanı belirtir) | Bağlamsal zenginleştirme: Yahudi yorum katmanı |

---

## Genişletilmiş Metin Külliyatı — Apokrif, Pseudepigrapha ve Gnostik Metinler

> **Hedef: Maksimum kaynak ile maksimum doğruluk.**
> Mevcut KJVA'daki 14 apokrif kitabın ötesinde, tüm erişilebilir Deuterokanonik, Pseudepigrapha, Gnostik ve Havari Babaları metinleri keyword search'e dahil edilecektir.

### Mevcut Durum (KJVA Apocrypha — 14 kitap, 5.717 ayet)

| # | Kitap | Durum |
|---|-------|-------|
| 1 | 1 Esdras | ✅ Mevcut |
| 2 | 2 Esdras | ✅ Mevcut |
| 3 | Tobit | ✅ Mevcut |
| 4 | Judith | ✅ Mevcut |
| 5 | Additions to Esther | ✅ Mevcut |
| 6 | Wisdom of Solomon | ✅ Mevcut |
| 7 | Sirach (Ecclesiasticus) | ✅ Mevcut |
| 8 | Baruch + Letter of Jeremiah | ✅ Mevcut |
| 9 | Prayer of Azariah | ✅ Mevcut |
| 10 | Susanna | ✅ Mevcut |
| 11 | Bel and the Dragon | ✅ Mevcut |
| 12 | Prayer of Manasseh | ✅ Mevcut (1 ayet — format sorunu olabilir) |
| 13 | 1 Maccabees | ✅ Mevcut |
| 14 | 2 Maccabees | ✅ Mevcut |

### Eklenecek Metinler — Tam Liste

Aşağıdaki metinlerin tamamı keyword search PostgreSQL tablosuna (`bm_books → bm_verses → bm_words`) indekslenecektir.

#### Kategori 1: Eksik Deuterokanonik Kitaplar

| Metin | Birincil Kaynak | Format | Lisans |
|-------|----------------|--------|--------|
| 3 Maccabees | Scrollmapper | JSON | PD/CC0 |
| 4 Maccabees | Scrollmapper | JSON | PD/CC0 |
| Psalm 151 | Scrollmapper | JSON | PD/CC0 |
| 2 Baruch (Syriac Baruch) | Scrollmapper | JSON | PD/CC0 |
| 3 Baruch (Greek Baruch) | Scrollmapper | JSON | PD/CC0 |
| 4 Baruch | Scrollmapper | JSON | PD/CC0 |

#### Kategori 2: Eski Ahit Pseudepigrapha

| Metin | Birincil Kaynak | Format | Lisans |
|-------|----------------|--------|--------|
| 1 Enoch (Ethiopic Enoch) | Scrollmapper / OCP | JSON / TEI XML | PD/CC0 |
| 2 Enoch (Slavonic Enoch) | Scrollmapper | JSON | PD/CC0 |
| Book of Jubilees | Scrollmapper | JSON | PD/CC0 |
| Testament of Reuben | Scrollmapper | JSON | PD/CC0 |
| Testament of Simeon | Scrollmapper | JSON | PD/CC0 |
| Testament of Levi | Scrollmapper | JSON | PD/CC0 |
| Testament of Judah | Scrollmapper | JSON | PD/CC0 |
| Testament of Issachar | Scrollmapper | JSON | PD/CC0 |
| Testament of Zebulun | Scrollmapper | JSON | PD/CC0 |
| Testament of Dan | Scrollmapper | JSON | PD/CC0 |
| Testament of Naphtali | Scrollmapper | JSON | PD/CC0 |
| Testament of Gad | Scrollmapper | JSON | PD/CC0 |
| Testament of Asher | Scrollmapper | JSON | PD/CC0 |
| Testament of Joseph | Scrollmapper | JSON | PD/CC0 |
| Testament of Benjamin | Scrollmapper | JSON | PD/CC0 |
| Psalms of Solomon | Scrollmapper | JSON | PD/CC0 |
| Odes of Solomon | Scrollmapper | JSON | PD/CC0 |
| Apocalypse of Abraham | Scrollmapper | JSON | PD/CC0 |
| Apocalypse of Elijah | Scrollmapper | JSON | PD/CC0 |
| Assumption of Moses | Scrollmapper | JSON | PD/CC0 |
| Sibylline Oracles | Scrollmapper | JSON | PD/CC0 |
| Visions of Amram | Scrollmapper | JSON | PD/CC0 |
| Testament of Isaac | Scrollmapper | JSON | PD/CC0 |
| Testament of Jacob | Scrollmapper | JSON | PD/CC0 |
| Testament of Kohath | Scrollmapper | JSON | PD/CC0 |
| Ladder of Jacob | Scrollmapper | JSON | PD/CC0 |
| Joseph and Aseneth | Scrollmapper | JSON | PD/CC0 |
| History of the Rechabites | Scrollmapper | JSON | PD/CC0 |
| Wisdom of Ahikar | Scrollmapper | JSON | PD/CC0 |
| Jannes and Jambres | Scrollmapper | JSON | PD/CC0 |
| Book of Giants | Scrollmapper | JSON | PD/CC0 |
| Genesis Apocryphon | Scrollmapper | JSON | PD/CC0 |
| Apocryphon of Joshua | Scrollmapper | JSON | PD/CC0 |
| Apocalypse of Sedrach | Scrollmapper | JSON | PD/CC0 |
| Lives of the Prophets | Scrollmapper | JSON | PD/CC0 |
| Gad the Seer | Scrollmapper | JSON | PD/CC0 |
| Book of Nathan the Prophet | Scrollmapper | JSON | PD/CC0 |
| Balaam Inscription | Scrollmapper | JSON | PD/CC0 |
| Five Psalms of David | Scrollmapper | JSON | PD/CC0 |
| Songs of the Sabbath Sacrifice | Scrollmapper | JSON | PD/CC0 |
| Book of Jasher | Scrollmapper | JSON | PD/CC0 |
| 1 Adam and Eve | Scrollmapper | JSON | PD/CC0 |
| 2 Adam and Eve | Scrollmapper | JSON | PD/CC0 |
| Testament of Abraham | Scrollmapper | JSON | PD/CC0 |
| Testament of Job | Scrollmapper | JSON | PD/CC0 |
| Testament of Solomon | Scrollmapper | JSON | PD/CC0 |
| Letter of Aristeas | Scrollmapper | JSON | PD/CC0 |
| Apocalypse of Zephaniah | Scrollmapper | JSON | PD/CC0 |
| Life of Adam and Eve | Scrollmapper | JSON | PD/CC0 |
| Martyrdom of Isaiah | Scrollmapper | JSON | PD/CC0 |

#### Kategori 3: Yeni Ahit Apokrifası

| Metin | Birincil Kaynak | Format | Lisans |
|-------|----------------|--------|--------|
| Gospel of Nicodemus (Acts of Pilate) | Scrollmapper | JSON | PD/CC0 |
| Epistle of Barnabas | Scrollmapper | JSON | PD/CC0 |
| Shepherd of Hermas (Book 1) | Scrollmapper | JSON | PD/CC0 |
| Shepherd of Hermas (Book 2) | Scrollmapper | JSON | PD/CC0 |
| Shepherd of Hermas (Book 3) | Scrollmapper | JSON | PD/CC0 |
| Gospel of Thomas | Coptic Scriptorium / Gnosis Archive | TEI XML / HTML | CC BY / PD |
| Gospel of Philip | Gnosis Archive | HTML | PD |
| Gospel of Mary | Gnosis Archive | HTML | PD |
| Gospel of Judas | Gnosis Archive | HTML | PD |
| Gospel of Peter | Gnosis Archive | HTML | PD |
| Gospel of Truth | Gnosis Archive | HTML | PD |
| Gospel of the Egyptians | Gnosis Archive | HTML | PD |
| Protevangelium of James | Gnosis Archive | HTML | PD |
| Infancy Gospel of Thomas | Gnosis Archive | HTML | PD |
| Acts of Thomas | Gnosis Archive | HTML | PD |
| Acts of Peter | Gnosis Archive | HTML | PD |
| Acts of Paul and Thecla | Gnosis Archive | HTML | PD |
| Apocalypse of Peter | Gnosis Archive | HTML | PD |
| Apocalypse of Paul | Gnosis Archive | HTML | PD |

#### Kategori 4: Gnostik Metinler (Nag Hammadi)

| Metin | Birincil Kaynak | Format | Lisans |
|-------|----------------|--------|--------|
| Apocryphon of John | Gnosis Archive / Coptic Scriptorium | HTML / TEI XML | PD / CC BY |
| Treatise on the Resurrection | Gnosis Archive | HTML | PD |
| Tripartite Tractate | Gnosis Archive | HTML | PD |
| On the Origin of the World | Gnosis Archive | HTML | PD |
| Hypostasis of the Archons | Gnosis Archive | HTML | PD |
| Thunder, Perfect Mind | Gnosis Archive | HTML | PD |
| Pistis Sophia | Coptic Scriptorium / Gutenberg | TEI XML / TXT | CC BY / PD |
| Prayer of the Apostle Paul | Gnosis Archive | HTML | PD |
| Secret Book of James | Gnosis Archive | HTML | PD |
| Exegesis on the Soul | Gnosis Archive | HTML | PD |
| Book of Thomas the Contender | Gnosis Archive | HTML | PD |
| Eugnostos the Blessed | Gnosis Archive | HTML | PD |
| Wisdom of Jesus Christ | Gnosis Archive | HTML | PD |
| Dialogue of the Savior | Gnosis Archive | HTML | PD |
| Marsanes | Gnosis Archive | HTML | PD |
| Allogenes | Gnosis Archive | HTML | PD |
| Melchizedek | Gnosis Archive | HTML | PD |
| Thought of Norea | Gnosis Archive | HTML | PD |
| Testimony of Truth | Gnosis Archive | HTML | PD |
| Paraphrase of Shem | Gnosis Archive | HTML | PD |
| Second Treatise of the Great Seth | Gnosis Archive | HTML | PD |
| Apocalypse of Adam | Gnosis Archive | HTML | PD |
| Acts of Peter and Twelve Apostles | Gnosis Archive | HTML | PD |
| Authoritative Teaching | Gnosis Archive | HTML | PD |
| Interpretation of Knowledge | Gnosis Archive | HTML | PD |
| Valentinian Exposition | Gnosis Archive | HTML | PD |

#### Kategori 5: Havari Babaları (Apostolic Fathers)

| Metin | Birincil Kaynak | Format | Lisans |
|-------|----------------|--------|--------|
| Didache | Patristics.info / CCEL | HTML | PD |
| 1 Clement | Patristics.info / CCEL | HTML | PD |
| 2 Clement | Patristics.info / CCEL | HTML | PD |
| Ignatius — Ephesians | Patristics.info | HTML | PD |
| Ignatius — Magnesians | Patristics.info | HTML | PD |
| Ignatius — Trallians | Patristics.info | HTML | PD |
| Ignatius — Romans | Patristics.info | HTML | PD |
| Ignatius — Philadelphians | Patristics.info | HTML | PD |
| Ignatius — Smyrnaeans | Patristics.info | HTML | PD |
| Ignatius — Polycarp | Patristics.info | HTML | PD |
| Polycarp to the Philippians | Patristics.info / CCEL | HTML | PD |
| Martyrdom of Polycarp | Patristics.info / CCEL | HTML | PD |
| Letter to Diognetus | Patristics.info / CCEL | HTML | PD |
| Fragments of Papias | Patristics.info | HTML | PD |

### Özet İstatistikler

| Kategori | Metin Sayısı | Birincil Format |
|----------|-------------|-----------------|
| Mevcut KJVA Apocrypha | 14 | JSON (bible_kjva.json) |
| Eksik Deuterokanonikler | 6 | JSON (Scrollmapper) |
| OT Pseudepigrapha | ~50 | JSON (Scrollmapper) |
| NT Apocrypha | ~19 | JSON (Scrollmapper) + HTML (Gnosis Archive) |
| Gnostik (Nag Hammadi) | ~26 | HTML (Gnosis Archive) + TEI XML (Coptic Scriptorium) |
| Havari Babaları | ~14 | HTML (Patristics.info / CCEL) |
| **TOPLAM** | **~129 metin** | — |

### Veri Edinme Stratejisi

| Öncelik | Kaynak | Format | Metin Sayısı | ETL Karmaşıklığı |
|---------|--------|--------|-------------|-------------------|
| **1 (kolay)** | Scrollmapper JSON | JSON (verse-indexed) | 69 ✅ doğrulandı | **Çok düşük** — `bible_kjva.json` ile birebir aynı şema |
| **2 (orta)** | Gnosis Archive | HTML | ~40 | Orta — HTML scraping + temizleme |
| **3 (orta)** | Patristics.info / CCEL | HTML | ~14 | Orta — HTML scraping + temizleme |
| **4 (zor)** | Coptic Scriptorium | TEI XML | ~5 | Yüksek — TEI parser, Kıptice/İngilizce hizalama |
| **5 (zor)** | OCP | TEI XML | ~40 | Yüksek — TEI parser, kritik aygıt |

> **✅ Scrollmapper JSON Yapısı Doğrulandı** (`scrollmapper/bible_databases_deuterocanonical`)
>
> Dosya konumu: `sources/en/{metin-adı}/{metin-adı}.json` (69 dosya)
>
> JSON şeması `bible_kjva.json` ile **birebir aynıdır** — aynı parser tekrar kullanılabilir:
> ```json
> {
>   "verse": 1,
>   "chapter": 1,
>   "name": "I Enoch 1:1",
>   "text": "The words of the blessing of Enoch..."
> }
> ```

### PostgreSQL Şema Genişletmesi

Mevcut `bm_books` tablosuna `category` sütunu eklenerek metin kategorisi izlenecektir:

```sql
ALTER TABLE bm_books ADD COLUMN category VARCHAR(20) 
  CHECK (category IN ('ot', 'nt', 'apocrypha', 'pseudepigrapha', 'gnostic', 'apostolic_fathers'));
```

Bu sayede kullanıcı keyword search'te kategori bazında filtreleme yapabilir (mevcut OT/NT/Apocrypha filtresinin genişletilmiş hali).

---

## Proposal

Sistem, Kur'an keyword search ile **aynı mimari deseni** (PostgreSQL hiyerarşik tablo yapısı, B-Tree + GIN indeksler, morfolojik kök araması) izlemeli, ancak orijinal dillere (İbranice/Yunanca) ve Kitab-ı Mukaddes yapısına uyarlanmalıdır. Üç aşamalı bir yol haritası önerilmektedir:

> **⚠️ BHS Telif Duvarı**: Biblia Hebraica Stuttgartensia (BHS), Leningrad Kodeksi'nin aynısını kullansa da, editoryal kararları ve kritik aygıtı Deutsche Bibelgesellschaft tarafından teliflidir. Proje, BHS yerine **UXLC/OSHB** kombinasyonunu kullanmalıdır — aynı el yazması, telif sorunu olmadan. *(Kaynak Raporu 2, Bölüm 2.3)*

### Faz 1 — İbranice Eski Ahit Keyword Search (MVP)

Kur'an Arapça kök aramasının birebir karşılığı. Kullanıcı İbranice bir kök girdiğinde (örn: "כתב" k-t-b, yazmak), sistem o kökten türeyen tüm kelimeleri (כָּתַב, כְּתָב, מִכְתָּב, כָּתוּב...), frekans analizini ve kitap dağılımını sunar.

**Veri Kaynakları**:
- **Metin**: WLC/UXLC (Unicode/XML Leningrad Codex) — MS 1008, eksiksiz en eski İbranice Kitab-ı Mukaddes el yazması (Firkovich B19a). Kamu Malı.
- **Morfoloji**: OSHB (`openscriptures/morphhb`) — her İbranice kelimeye Strong's H numarası + morfolojik etiket + lemma. CC BY 4.0.
- **Format**: OSIS XML — her ayet, kelime ve kantilyasyon işareti ayrı düğüm olarak tanımlı.
- **Özel özellikler**: Kethiv/Qere (yazılan ama okunmayan / okunan ama yazılmayan) varyantları XML yapısında ayrıntılı.

**OSHB XML Yapısı** *(Kaynak Raporu 2, Bölüm 2.2)*:

```xml
<w lemma="strong:H07225" morph="Hebrew:Noun">rēʾšîṯ</w>
```

Her kelime: orijinal İbranice form + Strong's H numarası + morfolojik etiket + lemma. Bu, Kur'an'daki QAC morfoloji verisinin İbranice karşılığıdır.

**PostgreSQL Şeması** (Kur'an `qm_*` modelini yansıtır):

```
bm_books → bm_verses → bm_words
```

| Tablo | Sütunlar | Kaynak |
|-------|----------|--------|
| `bm_books` | `id`, `name`, `name_hebrew`, `testament` (OT/NT/Apocrypha), `category`, `total_chapters`, `total_verses` | OSHB kitap listesi |
| `bm_verses` | `id`, `book_id` (FK), `chapter`, `verse`, `text_original` (İbranice/Yunanca), `text_english` (KJVA çeviri), `reference` | OSHB ayetler + KJVA eşleştirme |
| `bm_words` | `id`, `verse_id` (FK), `position`, `word` (orijinal form — İbranice Unicode), `word_clean` (hareke/nikud temizlenmiş), `lemma`, `root`, `strong_number` (H07225), `morph_tag`, `pos_tag`, `transliteration`, `language` (hebrew/greek) | OSHB morfoloji parse |

**İndeksler**:
- `ix_bm_words_root` — B-Tree (kök bazlı exact match — ana arama yolu)
- `ix_bm_words_lemma` — B-Tree (lemma bazlı exact match)
- `ix_bm_words_strong` — B-Tree (Strong's numarası ile çapraz arama)
- `ix_bm_words_word_clean` — B-Tree (kelime bazlı exact match)
- `ix_bm_words_word_clean_trgm` — GIN trigram (fuzzy matching, transliterasyon)
- `ix_bm_words_verse_id` — B-Tree (FK lookup)
- `ix_bm_words_language` — B-Tree (dil filtreleme)
- `ix_bm_verses_book_id` — B-Tree (FK lookup)

**Arama Algoritması** (Kur'an Arapça kök aramasını yansıtır):

```
İbranice Giriş → Unicode normalizasyon (nikud/hareke temizleme)
  ↓
[Adım 1] Exact match: root = query (İbranice kök)
  → Bulunursa → o kökten türeyen tüm kelimeleri bul
  ↓
[Adım 2] Strong's lookup: Girilen kelime Strong's numarasıysa (H07225)
  → O Strong's numarasına sahip tüm kelimeleri bul
  ↓
[Adım 3] Transliterasyon: Latin giriş (ktb) → İbranice dönüşüm (כתב) → tekrar ara
  ↓
[Adım 4] Fuzzy match: pg_trgm ile benzerlik araması
  → En yakın eşleşmeyi döndür
```

**API Endpoint'leri** (mevcut Kur'an pattern'ini genişletir):

| Endpoint | Açıklama |
|----------|----------|
| `POST /api/keyword-search/bible` | Orijinal dilde kelime/kök ara (testament + dil filtreli) |
| `GET /api/keyword-search/bible/roots` | Tüm İbranice/Yunanca kökleri listele |
| `GET /api/keyword-search/bible/root/{root}` | Belirli bir kökün detayları |
| `GET /api/keyword-search/bible/stats` | İstatistikler (toplam kelime, unique kök sayısı) |

**Kullanıcı Deneyimi**:

- Kullanıcı "כתב" (veya Latin "ktb") yazar → sistem kök bulur → כָּתַב, כְּתָב, מִכְתָּב, כָּתוּב tüm türevleri getirir
- Sonuçlar: toplam oluş sayısı, unique türev kelimeleri, kitap dağılımı, sayfalanmış ayet listesi (eşleşen kelimeler vurgulu)
- Filtreleme: Eski Ahit kitapları bazında
- Kur'an keyword search ile aynı response şeması (uyarlanmış alan adları)
- **Font**: Unicode İbranice — Ezra SIL

**Kur'an ETL ile Paralel Yapı**:

| Konu | Kur'an (RFC-006) | İbranice Eski Ahit (Faz 1) |
|------|-----------------|---------------------------|
| Kaynak | Tanzil XML + QAC TSV | UXLC + OSHB OSIS XML |
| Kök kaynağı | QAC insan-doğrulamalı kök | OSHB Strong's H + lemma |
| Normalizasyon | Arapça hareke temizleme | İbranice nikud temizleme |
| Transliterasyon | Buckwalter (Arapça ↔ Latin) | İbranice ↔ Latin transliterasyon |
| Script | `setup_quran_morphology.py` | `setup_bible_keyword.py` |

### Faz 2 — Yunanca Yeni Ahit + LXX Keyword Search

Faz 1 altyapısını Yunanca metinlere genişletir. Aynı `bm_words` tablosu `language='greek'` ile kullanılır.

**Yunanca Yeni Ahit — SBLGNT + MorphGNT**:
- **Metin kaynağı**: SBLGNT (Michael W. Holmes editörlüğü) — Westcott-Hort, Tregelles, NIV Yunanca ve Robinson-Pierpoint metinleri karşılaştırılarak oluşturulmuş bağımsız eklektik metin. NA28 ile %90+ uyumlu, ancak NA28'in mülkiyetine dayanmaz. CC BY 4.0.
- **Morfoloji**: MorphGNT — lemma, POS etiketi, morfolojik analiz. CC BY 4.0.
- **Alternatif metinler**: Robinson-Pierpoint 2005 (Bizans metni, Kamu Malı), Textus Receptus Scrivener 1881 (Kamu Malı).
- **Keyword Search**: Yunanca kelimeler `bm_words` tablosuna `language='greek'` ile indekslenecek. Lemma bazlı arama MorphGNT morfolojik verilerine dayanacak.
- **Font**: Unicode Yunanca — Gentium.

**Septuagint (LXX) — Rahlfs 1935**:
- **Metin kaynağı**: CCAT (Center for Computer Analysis of Texts) tarafından morfolojik etiketlenmiş Rahlfs 1935 edisyonu. Kamu Malı.
- **Kapsam**: Tüm Deuterokanonik kitaplar dahil (Tobit, Yudit, Makkabiler, Sirach vb.).
- **Kaynak depoları**: CrossWire (SWORD Project) modülleri, `eliranwong/LXX-Rahlfs-1935` GitHub deposu.
- **Keyword Search**: LXX Yunanca kelimeleri de `bm_words` tablosuna indekslenecek — Apokrif metinlerin Yunanca orijinalinde arama imkanı.
- **⚠️ Göttingen Septuagint**: En güncel akademik edisyon ancak Deutsche Bibelgesellschaft lisansı ile korunuyor — **kullanılmayacak**.

**Strong's Concordance Çapraz Referans** (Faz 2 ile birlikte):

Strong's Concordance, İbranice ve Yunanca kökler arasında köprü kurar. Aynı kavramın (örn: "sevgi") İbranice'de "אהב" (ahav, H157) ve Yunanca'da "ἀγάπη" (agape, G26) olarak nasıl ifade edildiğini gösterir.

**Ek Tablo**:

| Tablo | Sütunlar |
|-------|----------|
| `bm_strongs` | `number` (H157/G26), `original_word`, `transliteration`, `definition`, `language` (hebrew/greek) |

**Veri Kaynağı**: `openscriptures/strongs` deposu — İbranice (`hebrew/StrongHebrewG.xml`, 8.674 giriş) + Yunanca (`greek/strongsgreek.xml`, 5.624 giriş). Kamu Malı.

**Ek Kullanıcı Deneyimi**:
- Ayet içinde bir kelimeye tıklandığında Strong's numarası, kök, lemma, gramer bilgisi görünür
- "Bu köke sahip tüm ayetleri göster" butonu
- Kavramsal bağlantılar: aynı Strong's numarasına sahip İbranice ↔ Yunanca çapraz arama
- Interlinear görüntüleme: Orijinal dil + İngilizce çeviri yan yana

**El Yazması Kanıtları** (ileri araştırma modülü):
- **Codex Sinaiticus**: MS 4. yy en eski tam İncil el yazması — dijital transkripsiyon TEI XML formatında. CC BY-NC-SA 3.0. SBLGNT metninin yanında "Orijinal El Yazması" katmanı olarak sunulabilir.
- **NTVMR API** (Münster INTF): Binlerce el yazmasının fotoğraf ve transkripsiyonu. Belirli bir ayet için mevcut el yazması kanıtlarını dinamik olarak çekebilir (`http://ntvmr.uni-muenster.de/community/vmr/api`). Ticari kullanım sınırlı olabileceğinden "araştırma eklentisi" olarak sunulmalı.

**Ayet Eşleştirme (Versification Mapping)**: Masoretik Metin ile LXX arasındaki ayet numarası farkları (özellikle Mezmurlar) yönetilmelidir.

### Faz 3 — Türkçe Metin Katmanı (Gelecek)

*(Kaynak Raporu 2, Bölüm 6)*

Projenin hedef kitlesi Türkiye olduğundan, Türkçe Kitab-ı Mukaddes metninin eklenmesi stratejik öneme sahiptir.

**1941 "Eski Çeviri" (MacCallum) — Varsayılan Türkçe Metin**:
- **Kaynak**: `seven1m/open-bibles` deposu → `tur-turkish.osis.xml` (OSIS XML formatı)
- **Telif Analizi**: Dr. Frederick W. MacCallum ✝28 Kasım 1945 İstanbul. Türkiye 5846 Sayılı FSEK, Madde 27: koruma süresi = ölüm + 70 yıl = 1945 + 70 = **1 Ocak 2016'da telif sona ermiştir**. Kurumsal eser olarak değerlendirilse dahi (KMŞ, Madde 26): yayın + 70 yıl = 1941 + 70 = **2011'de dolmuş olacaktı**. Her iki senaryoda da **Kamu Malı**.
- **Kullanım**: Varsayılan Türkçe metin olarak "Klasik Çeviri" / "1941 Metni" adıyla sunulacak.
- **⚠️ 2001/2008 "Yeni Çeviri"**: Kitabı Mukaddes Şirketi telifli — izinsiz dijital kullanım yasaktır. Projenin varlığı bu lisansa bağlı olmamalıdır.

**Sefaria Entegrasyonu — Bağlamsal Zenginleştirme**:
- Sefaria API veya yerel bulk export ile Yahudi yorum geleneği (Midraş, Talmud, Rashi) entegre edilebilir.
- API yanıtları her metin parçası için `license` alanı döndürür — programatik filtreleme mümkün.
- "Yorumlar" sekmesinde Rashi'nin belirli bir ayet üzerine yorumunu anında getirmek, uygulamayı bir "araştırma platformu"na dönüştürür.

---

## Veri İşleme Stratejisi (ETL Pipeline)

### Faz 1 ETL: İbranice Eski Ahit (OSHB → PostgreSQL)

Kur'an ETL pipeline'ı (`setup_quran_morphology.py`) ile paralel bir `setup_bible_keyword.py` scripti:

```
openscriptures/morphhb (OSHB OSIS XML)
    ↓
[Parse] OSIS XML → books, chapters, verses, words
    → Her <w> elementi: Strong's H numarası + morfolojik etiket + lemma
    ↓
[Normalize] İbranice nikud (hareke/ünlü) temizleme → word_clean
    ↓
[Root Extract] OSHB Strong's H numarasından kök çıkarımı
    → Strong's sözlüğü ile kök eşleştirme
    ↓
[Transliterate] İbranice → Latin transliterasyon (arama için)
    ↓
[Insert] bm_books → bm_verses → bm_words (batch upsert)
    ↓
[Validate] Sayıları doğrula: 39 kitap (Eski Ahit), ~23.145 ayet, ~300.000+ kelime
```

### Faz 2 ETL: Yunanca Yeni Ahit + LXX

```
MorphGNT (TSV) + SBLGNT
    ↓
[Parse] TSV → book, chapter, verse, word, lemma, POS, morph_tag
    ↓
[Normalize] Yunanca aksan/tonlama temizleme → word_clean
    ↓
[Insert] bm_words tablosuna language='greek' ile ekle
    ↓

Rahlfs LXX 1935 (CCAT morfolojik)
    ↓
[Parse] Morfolojik etiketli metin → words
    ↓
[Insert] bm_words tablosuna language='greek' ile ekle (Apokrif/Deuterokanonik)
```

### Kur'an ETL ile Karşılaştırma

| Konu | Kur'an (RFC-006) | İbranice Eski Ahit (Faz 1) | Yunanca Yeni Ahit (Faz 2) |
|------|-----------------|---------------------------|--------------------------|
| Kaynak format | Tanzil XML + QAC TSV | OSHB OSIS XML | MorphGNT TSV + SBLGNT |
| Normalizasyon | Arapça hareke temizleme, hamza normalize | İbranice nikud temizleme | Yunanca aksan temizleme |
| Kök/Lemma kaynağı | QAC insan-doğrulamalı kök | OSHB Strong's H + lemma | MorphGNT lemma + POS |
| Transliterasyon | Buckwalter (Arapça ↔ Latin) | İbranice ↔ Latin | Yunanca ↔ Latin |
| Kelime sayısı | ~77.430 | ~300.000+ | ~140.000 (NT) + LXX |
| Script | `setup_quran_morphology.py` | `setup_bible_keyword.py` | Aynı script, Faz 2 modu |

**Veri Format Pipeline** *(Kaynak Raporu 2, Bölüm 7.1)*:
- **OSIS** (İbranice metinler): OSHB → OSIS XML parser → PostgreSQL
- **TSV** (Yunanca metinler): MorphGNT → TSV parser → PostgreSQL
- **JSON** (Apokrif genişletme): Scrollmapper JSON → doğrudan insert (İngilizce çeviri `text_english` alanına)
- **TEI** (Gnostik/Pseudepigrapha): OCP, Coptic Scriptorium → TEI XML parser → PostgreSQL

---

## Lisanslama ve Yasal Değerlendirme

Araştırma raporlarının tespitlerine dayanarak:

| Kaynak | Kullanım | Lisans | Gereklilik |
|--------|----------|--------|------------|
| KJVA metin (mevcut) | Tüm fazlar (İngilizce çeviri referansı) | Kamu Malı | Kısıtlama yok |
| ~~NLTK/spaCy (İngilizce lemmatization)~~ | ~~Kullanılmayacak~~ | ~~MIT/Apache~~ | ~~Orijinal dil odağı nedeniyle gereksiz — OSHB/MorphGNT morfolojisi kullanılacak~~ |
| WLC/UXLC metin (`tanach.us`) | Faz 1 | Kamu Malı | Kısıtlama yok |
| OSHB morfoloji (`openscriptures/morphhb`) | Faz 1 | CC BY 4.0 | Atıf zorunlu |
| Strong's Concordance (`openscriptures/strongs`) | Faz 1-2 | Kamu Malı | Kısıtlama yok |
| SBLGNT (`logosbible/SBLGNT`) | Faz 2 | CC BY 4.0 | Atıf zorunlu (SBL + Logos) |
| MorphGNT | Faz 2 | CC BY 4.0 | Atıf zorunlu |
| Rahlfs LXX 1935 (CCAT) | Faz 2 | Kamu Malı | Kısıtlama yok |
| 1941 Türkçe Çeviri (`seven1m/open-bibles`) | Faz 3 | Kamu Malı (FSEK 70 yıl kuralı) | Kısıtlama yok |
| Sefaria İbranice metinler | Faz 3 | Kamu Malı | API `license` alanını kontrol et |
| Sefaria İngilizce çeviriler | Faz 3 | Karışık (CC-BY / telifli) | Her metin için API yanıtındaki lisansı programatik filtrele |
| Codex Sinaiticus | Faz 2+ | CC BY-NC-SA 3.0 | Yalnızca ticari olmayan kullanım — "araştırma modülü" |
| NTVMR API (Münster) | Faz 2+ | Sınırlı — akademik | Ticari kullanım öncesi lisans teyidi gerekli |
| ~~BHS (Biblia Hebraica Stuttgartensia)~~ | ~~Kullanılmayacak~~ | ~~Deutsche Bibelgesellschaft telifli~~ | ~~Pahalı lisans, UXLC/OSHB ile aynı kodeks zaten mevcut~~ |
| ~~Göttingen Septuagint~~ | ~~Kullanılmayacak~~ | ~~Deutsche Bibelgesellschaft telifli~~ | ~~Rahlfs 1935 yeterli~~ |
| ~~2001/2008 Türkçe "Yeni Çeviri"~~ | ~~Kullanılmayacak~~ | ~~KMŞ telifli~~ | ~~1941 çevirisi yeterli~~ |

**CC BY 4.0 yükümlülüğü**: Uygulamanın "Hakkında" veya "Kaynaklar" sayfasında aşağıdaki kuruluşlara atıf zorunludur:
- **Open Scriptures** — OSHB morfoloji verileri
- **Society of Biblical Literature (SBL) + Logos Bible Software** — SBLGNT metin
- **MorphGNT** — Yunanca morfolojik etiketleme
- **Coptic Scriptorium** — Gnostik/Kıptice metinler (ileri fazlarda)

---

## Expected Outcome

### Faz 1 Tamamlandığında

- Kullanıcılar İbranice kök veya kelime ile Eski Ahit üzerinde morfolojik arama yapabilir
- "כתב" (ktb) araması → כָּתַב, כְּתָב, מִכְתָּב, כָּתוּב tüm türevleri getirir
- Latin transliterasyon girişi desteklenir (Kur'an Buckwalter'ın karşılığı)
- Strong's H numarası ile arama yapılabilir (H03789 → "yazmak" ile ilgili tüm ayetler)
- Kitap dağılımı bir bakışta görülebilir (hangi kitapta kaç kez)
- Her ayet hem İbranice orijinal hem İngilizce KJVA çevirisi ile gösterilir
- Mevcut Kur'an keyword search aynen çalışmaya devam eder — regresyon yok
- API endpoint'leri Kur'an keyword search ile tutarlı şema kullanır
- PostgreSQL'de ~300.000+ İbranice kelime B-Tree + GIN indekslerle milisaniye düzeyinde sorgulanır

### Faz 2 Tamamlandığında

- Yunanca Yeni Ahit üzerinde lemma bazlı arama yapılabilir (SBLGNT + MorphGNT)
- Septuagint (LXX) üzerinde Yunanca arama — Apokrif metinlerin orijinal dilinde arama
- Strong's Concordance çapraz referans: aynı kavramın İbranice ↔ Yunanca karşılıkları
- Interlinear görüntüleme: orijinal dil + İngilizce çeviri yan yana
- Morfolojik analiz: kelimeye tıkla → kök, lemma, gramer bilgisi (fiil çekimi, isim hali vb.)

## Kapsam ve Sınırlar

**Bu RFC, Kitab-ı Mukaddes orijinal dil metinleri (İbranice/Yunanca) üzerinde morfolojik kök bazlı keyword aramayı kapsar.**

### Scope İÇİNDE
- PostgreSQL'de orijinal dil kelime indeksleme (`bm_books → bm_verses → bm_words`)
- İbranice kök bazlı arama (OSHB morfoloji verisiyle)
- Yunanca lemma bazlı arama (MorphGNT morfoloji verisiyle)
- Strong's Concordance çapraz referans sistemi
- Apokrif/Pseudepigrapha/Gnostik metinlerin keyword search'e eklenmesi
- Türkçe metin katmanı (keyword search olarak — Faz 3)

### Scope DIŞINDA
- **İngilizce keyword search** — Mevcut semantik arama (Qdrant hybrid search) İngilizce metin erişimini zaten karşılıyor. İngilizce lemma bazlı arama bu RFC'nin kapsamında değildir.
- **Qdrant entegrasyonu** — Bu RFC kapsamında hiçbir Qdrant (vektör/semantik) değişikliği yapılmayacaktır. Yeni eklenen metinler yalnızca PostgreSQL keyword search'e girecektir. Qdrant indeksleme ayrı bir RFC ile ele alınacaktır.
- Mevcut semantik arama (Qdrant hibrit search — dense + sparse vektörler) aynen korunur ve bu değişiklikten etkilenmez.

### İki Sistem Birbirini Tamamlar
- **Keyword search (bu RFC)**: "Bu İbranice/Yunanca kök tam olarak nerede geçiyor?" (morfolojik form analizi, frekans, dağılım, kesin eşleşme)
- **Semantic search (mevcut)**: "Bu kavram hakkında ne söyleniyor?" (anlam bazlı, bağlamsal, İngilizce çeviri üzerinden)

## Open Questions

### Açık Sorular

- **OSHB XML parse stratejisi**: OSIS XML parser mı (lxml), yoksa mevcut bir Python kütüphanesi (python-scripture, pysword) mi kullanılacak? OSHB'nin `<w>` element yapısı göz önüne alındığında custom parser daha uygun olabilir.
- **İbranice kök çıkarımı**: OSHB Strong's H numarasından kök doğrudan alınabiliyor mu, yoksa Strong's sözlüğüne cross-reference gerekli mi? Kur'an'da QAC doğrudan kök veriyor — aynı doğrudanlık sağlanmalı.
- **Nikud/hareke normalizasyon derinliği**: İbranice nikud (ünlü işaretleri) tamamen mı temizlenecek, yoksa bazı harfler (şin/sin noktası gibi) korunacak mı?
- **Frontend**: RFC-007 (Quran Keyword Search Frontend) tasarımı Bible keyword search'e de genişletilecek mi, yoksa ayrı bir sayfa mı olacak? RFC-007 "Future Scope" bölümünde buna değinilmiş.
- **Performans**: ~300.000 İbranice + ~140.000 Yunanca kelime — batch boyutları ve indeks optimizasyonu gerekli mi?
- **Versification Mapping**: Masoretik Metin ↔ LXX ↔ Türkçe çeviri ayet numarası farklılıkları (özellikle Mezmurlar) nasıl yönetilecek?
- **Font desteği**: İbranice (Ezra SIL), Yunanca (Gentium), Kıptice (Antinoou) web fontları frontend'e nasıl entegre edilecek?
- **Metin seçici**: Kullanıcıya Yunanca metin alternatifleri (SBLGNT / Robinson-Pierpoint / Textus Receptus) arasında seçim sunulacak mı?
- **İbranice transliterasyon standardı**: Hangi İbranice→Latin transliterasyon standardı kullanılacak? SBL Academic, Library of Congress, veya simplified?

### Çözülmüş Sorular

- ~~**Morfolojik veri kaynağı**~~ → **Çözüldü**: OSHB (`openscriptures/morphhb`) İbranice taraf için her kelimeye Strong's H numarası + morfolojik etiket + lemma sağlıyor. Yunanca taraf için MorphGNT mevcut ve SBLGNT üzerine morfolojik etiketleme yapıyor. *(Kaynak Raporu 2, Bölüm 2.2 ve 3.1)*
- ~~**MorphGNT erişilebilirliği**~~ → **Çözüldü**: MorphGNT projesi SBLGNT morfolojik etiketlemesi olarak erişilebilir. CC BY 4.0. *(Kaynak Raporu 2, Bölüm 3.1)*
- ~~**İngilizce keyword search gerekli mi?**~~ → **Çözüldü**: Hayır. Mevcut semantik arama İngilizce erişimi karşılıyor. Bu RFC yalnızca orijinal dil (İbranice/Yunanca) keyword search'e odaklanıyor.
