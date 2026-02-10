# **Dijital Teoloji ve Yazılım Mimarisi: Kitab-ı Mukaddes, Kritik Metinler ve Genişletilmiş Apokrif Külliyatı İçin Kaynak Tespit ve Lisanslama Stratejileri Üzerine Kapsamlı Araştırma Raporu**

## **Yönetici Özeti**

Bu rapor, Türkiye pazarına yönelik geliştirilmesi hedeflenen akademik düzeyde bir "Kitab-ı Mukaddes" yazılım projesi için gerekli olan metinsel altyapıyı, dijital veri kaynaklarını ve hukuki lisanslama çerçevelerini derinlemesine incelemektedir. Projenin kapsamı, Eski Ahit (Tanah), Yeni Ahit (İncil) ve Genişletilmiş Apokrif (Deuterokanonik, Pseudepigrapha ve Gnostik metinler) külliyatının tamamını içermektedir. Rapor, teolojik veri madenciliği, dijital beşeri bilimler (Digital Humanities) ve fikri mülkiyet hukuku disiplinlerinin kesişim noktasında, yazılım geliştiricilerine ve proje yöneticilerine stratejik bir yol haritası sunmayı amaçlamaktadır.

Analizler sonucunda, yazılımın filolojik doğruluğunu ve yasal sürdürülebilirliğini garanti altına alacak "Açık Erişim" (Open Access) veri yığınları tespit edilmiştir. Özellikle Masoretik Metin için Westminster Leningrad Kodeksi (WLC), Kritik Yunanca Yeni Ahit için SBLGNT ve Türkçe metin için 1941 Kitab-ı Mukaddes çevirisinin (MacCallum) telif süresinin dolmasıyla oluşan "Kamu Malı" (Public Domain) statüsü, projenin temel taşlarını oluşturmaktadır. Bu rapor, sadece kaynakları listelemekle kalmayıp, bu verilerin OSIS, TEI ve JSON formatlarında nasıl işleneceğini, API entegrasyonlarını ve akademik literatürdeki yerlerini 15.000 kelimelik kapsamlı bir analizle ortaya koymaktadır.

## ---

**1\. Giriş: Dijital İncil Çalışmalarında Metinsel Otorite ve Veri Egemenliği**

Dijital çağda teolojik araştırmalar ve yazılım geliştirme süreçleri, geleneksel basılı edisyonların (Codex) dijital veri tabanlarına (Corpus) dönüşümü ile radikal bir değişim geçirmiştir. Bir Kitab-ı Mukaddes yazılımı geliştirilirken karşılaşılan en büyük ontolojik ve teknik zorluk, "Metin" kavramının kendisidir. Kutsal metinler, tekil ve statik nesneler değil; varyantlar, editoryal kararlar ve tarihsel katmanlardan oluşan dinamik sistemlerdir. Bu nedenle, geliştirilecek yazılımın akademik ciddiyeti, kullandığı veri setlerinin (dataset) kökenine, filolojik kalitesine ve bu verilerin yasal kullanım haklarına doğrudan bağlıdır.

Günümüzde dijital İncil çalışmaları piyasası iki ana kampa ayrılmıştır. Bir tarafta, *Deutsche Bibelgesellschaft* (Alman Kitab-ı Mukaddes Derneği) gibi kurumların kontrolündeki yüksek maliyetli ve kapalı lisanslı akademik sistemler (Nestle-Aland, Biblia Hebraica Stuttgartensia); diğer tarafta ise *Society of Biblical Literature* (SBL) ve *Coptic Scriptorium* gibi inisiyatiflerin öncülük ettiği Açık Erişim (Open Access) ve Açık Kaynak (Open Source) projeleri yer almaktadır. Bu raporun temel tezi, Türkiye bağlamında geliştirilecek bir projenin, yüksek lisans maliyetlerinden kaçınarak akademik titizlikten ödün vermeden, ikinci grup (Açık Erişim) kaynakları üzerine inşa edilebileceğidir.

Veri egemenliği kavramı burada kritik bir rol oynar. Yazılımın dışsal API'lara (Application Programming Interface) bağımlı kalması, projenin sürdürülebilirliğini riske atar. Bu nedenle rapor, mümkün olduğunca verilerin yerel sunucularda barındırılmasına (self-hosted) olanak tanıyan, indirilebilir ham veri setlerine (XML, JSON) öncelik vermektedir.

## ---

**2\. Eski Ahit (Tanah): Masoretik Metnin Dijital Arkeolojisi ve Kaynaklar**

Eski Ahit'in dijital ortamda temsili, İbranice'nin morfolojik karmaşıklığı, sesli harf işaretleri (nikkudim) ve vurgu işaretleri (kantilyasyon/tropes) nedeniyle teknik bir meydan okumadır. Akademik bir yazılımın temel alması gereken metin, "Textus Receptus" niteliğindeki Masoretik Metin'dir (MT). Ancak hangi Masoretik Metin? Bu soru, dijital kaynak seçiminde belirleyicidir.

### **2.1. Metinsel Temel: Leningrad Kodeksi vs. Halep Kodeksi**

Yazılım geliştirme perspektifinden bakıldığında, eldeki en eski ve en güvenilir "tam" el yazması (manuscript) belirleyici faktördür. Tarihsel olarak Halep Kodeksi (Aleppo Codex), Aaron ben Asher tarafından noktalanmış olması nedeniyle en otoriter metin kabul edilse de, 1947'deki Halep olaylarında büyük zarar görmüş ve Tevrat (Torah) kısmının tamamı kaybolmuştur.1 Bu durum, Halep Kodeksi'ni bir yazılım projesi için "tekil kaynak" olmaktan çıkarır; zira eksik kısımların başka kaynaklarla tamamlanması (eklektik bir metin oluşturulması) gerekir ki bu da ciddi editoryal kararlar ve potansiyel telif sorunları doğurur.

Buna karşın, **Leningrad Kodeksi (Codex Leningradensis \- L)**, MS 1008 yılına tarihlenen ve günümüze *eksiksiz* olarak ulaşan en eski İbranice Kitab-ı Mukaddes el yazmasıdır. Modern akademik baskıların (Biblia Hebraica Stuttgartensia \- BHS) temelini oluşturur. Dijital dünyada "standart" olarak kabul edilen metin, bu kodeksin transkripsiyonudur.

#### **2.1.1. Westminster Leningrad Kodeksi (WLC) ve UXLC Projesi**

Yazılım projesi için en uygun, en temiz ve lisans sorunu olmayan kaynak, **Westminster Leningrad Codex (WLC)** ve onun en güncel türevi olan **Unicode/XML Leningrad Codex (UXLC)** projesidir.

* **Veri Kaynağı ve Köken:** WLC, J. Alan Groves Center for Advanced Biblical Research tarafından yönetilen, ancak kamu malı (Public Domain) olarak serbest bırakılan dijital bir metindir. UXLC ise bu metnin Unicode standartlarına tam uyumlu hale getirilmiş, XML etiketleri ile zenginleştirilmiş versiyonudur.2  
* **Akademik Değer:** UXLC, Leningrad Kodeksi'nin (Firkovich B19a) fotoğrafik faksimilesine sadık kalmayı amaçlar. Bu, metnin BHS baskısındaki olası dizgi hatalarından arındırıldığı ve doğrudan el yazmasına dayandığı anlamına gelir. Özellikle *Kethiv/Qere* (yazılan ama okunmayan / okunan ama yazılmayan) varyantlarının dijital ortamda işaretlenmesi, akademik çalışmalar için elzemdir. UXLC, bu varyantları XML yapısı içinde ayrıntılı olarak sunar.4  
* **Lisans Durumu:** **Kamu Malı (Public Domain)**. Bu statü, yazılım ekibinin metni veritabanına indirmesine, parse etmesine, mobil uygulamalarda çevrimdışı (offline) olarak sunmasına ve hatta ticari bir ürünün parçası haline getirmesine hiçbir kısıtlama olmaksızın izin verir.  
* **Teknik Format:** Veriler Tanach.us ve GitHub üzerinden XML, HTML ve ODT formatlarında sunulmaktadır. XML yapısı, her bir ayeti, kelimeyi ve hatta kantilyasyon işaretini ayrı düğümler (nodes) olarak tanımlar, bu da arama motoru optimizasyonu için mükemmel bir zemin hazırlar.3

### **2.2. Morfolojik Zenginleştirme: Open Scriptures Hebrew Bible (OSHB)**

Sadece İbranice metni göstermek, son kullanıcı için yeterli değildir. Akademik bir yazılım, kullanıcının bir kelimenin üzerine tıkladığında o kelimenin kökünü (lemma), dilbilgisi yapısını (morfoloji \- örn: Fiil, Kal, Tamamlanmış, 3\. Tekil Eril) ve sözlük anlamını görmesini sağlamalıdır. Ham WLC metninde bu veriler bulunmaz.

Bu noktada devreye **Open Scriptures Hebrew Bible (OSHB)** projesi girmektedir.

* **Projenin Niteliği:** OSHB, Westminster Leningrad Kodeksi üzerine inşa edilmiş, her kelimeye morfolojik etiketler ve Strong numaraları (sözlük referansları) ekleyen açık kaynaklı bir projedir.5  
* **Lisanslama Modeli:** Projenin temel metni (WLC) Kamu Malı olmakla birlikte, projeye eklenen morfolojik veriler ve lemmalar **Creative Commons Attribution 4.0 International (CC BY 4.0)** lisansı ile korunmaktadır.6  
  * *Uygulama İpuçları:* Yazılım geliştiricileri bu veriyi kullanabilir, ancak uygulamanın "Hakkında" veya "Kaynaklar" bölümünde Open Scriptures projesine açıkça atıfta bulunmak zorundadır. Bu, ticari kullanım için bir engel değildir, sadece atıf yükümlülüğü getirir.  
* **Veri Yapısı (OSIS XML):** OSHB verileri, İncil yazılımları için endüstri standardı olan **OSIS (Open Scripture Information Standard)** formatında sunulmaktadır. GitHub deposundaki (openscriptures/morphhb) XML dosyaları, \<w\> etiketleri içinde lemma ve morph özniteliklerini barındırır.  
  * Örnek XML Yapısı:  
    XML  
    \<w lemma\="strong:H07225" morph\="Hebrew:Noun"\>rēʾšîṯ\</w\>

Bu yapı, yazılımın arka planında bir "interlinear" (satır arası) okuma deneyimi oluşturmasını kolaylaştırır.6

### **2.3. Biblia Hebraica Stuttgartensia (BHS) ve Telif Duvarı**

Birçok akademisyen, basılı dünyadaki standart olan BHS'yi talep edebilir. Ancak yazılım mimarisi açısından BHS, ciddi bir yasal engel teşkil etmektedir. Alman Kitab-ı Mukaddes Derneği (Deutsche Bibelgesellschaft), BHS'nin metinsel içeriğini değil (çünkü o da Leningrad Kodeksi'dir), ancak metin üzerindeki editoryal kararları, dipnotları (masora) ve kritik aygıtı (critical apparatus) telif hakkı ile korumaktadır.8

* **Risk Analizi:** BHS metnini izinsiz kullanmak, uluslararası telif ihlali doğurur. Dernek, açık kaynaklı projelere lisans verme konusunda son derece isteksizdir ve ticari lisanslar binlerce doları bulabilmektedir.10  
* **Stratejik Karar:** Proje, BHS yerine **UXLC/OSHB** kombinasyonunu kullanmalıdır. UXLC, BHS'nin dayandığı el yazmasının aynısıdır; tek fark, modern editörlerin (Kittel, Elliger vb.) eklediği modern yorumların bulunmamasıdır ki bu, saf bir metin arayanlar için aslında bir avantajdır.

### **2.4. Sefaria: Yahudi Literatürü ile Bağlamsallaştırma**

Eski Ahit çalışmasını sadece metinle sınırlamayıp, Yahudi yorum geleneği (Midraş, Talmud, Rashi vb.) ile zenginleştirmek isteyen bir yazılım için **Sefaria** projesi eşsiz bir kaynaktır.

* **API ve Veri Dökümü:** Sefaria, tüm kütüphanesini (Tanah dahil) JSON formatında dışa aktarılabilir (bulk export) şekilde sunar veya API üzerinden anlık sorgulamaya açar (GET /api/texts/Genesis.1).  
* **Lisanslama:** Sefaria'daki İbranice metinlerin çoğu Kamu Malı'dır. Ancak İngilizce çevirilerin (örneğin JPS 1985\) bazıları teliflidir. API yanıtları, her bir metin parçası için lisans bilgisini (license: "Public Domain" veya license: "CC-BY") döndürür, bu da yazılımın hangi metni gösterip hangisini filtreleyeceğine programatik olarak karar vermesini sağlar.11  
* **Kullanım Senaryosu:** Yazılımın "Yorumlar" sekmesinde, Rashi'nin Yaratılış 1:1 üzerine yorumunu anında getirmek için Sefaria veritabanı yerel olarak entegre edilebilir. Bu, uygulamayı sadece bir "okuma" aracı olmaktan çıkarıp bir "araştırma" platformuna dönüştürür.

## ---

**3\. Yeni Ahit (İncil): Kritik Yunanca Metin ve Akademik Konsensüs**

Yeni Ahit metin eleştirisi (Textual Criticism) alanı, Nestle-Aland (NA28) / United Bible Societies (UBS5) metinlerinin tekelindedir. Bu metinler "Eklektik" (farklı el yazmalarından derlenmiş) metinlerdir ve akademik standarttır. Ancak, Eski Ahit'teki BHS örneğinde olduğu gibi, bu metinler de Alman Kitab-ı Mukaddes Derneği'nin sıkı telif koruması altındadır. Proje için alternatif ve yasal olarak güvenli bir strateji gereklidir.

### **3.1. Çözüm: SBL Greek New Testament (SBLGNT)**

2010 yılında Society of Biblical Literature (SBL) ve Logos Bible Software işbirliğiyle yayınlanan **SBL Greek New Testament**, tam da bu telif sorununu çözmek için üretilmiştir.

* **Metinsel Karakter:** SBLGNT, Michael W. Holmes editörlüğünde hazırlanmıştır. Metin oluşturulurken Westcott-Hort, Tregelles, NIV Yunanca Metni ve Robinson-Pierpoint (Bizans) metinleri karşılaştırılmış ve yeni bir eklektik metin oluşturulmuştur. Bu metin, NA28 ile %90'ın üzerinde uyumludur ancak NA28'in mülkiyetindeki verilere dayanmaz, bu da onu telif açısından özgür kılar.13  
* **Lisanslama (CC BY 4.0):** SBLGNT, açıkça **Creative Commons Attribution 4.0** lisansı ile yayınlanmıştır. Bu, yazılım geliştiricilerin metni serbestçe kullanmasına, veritabanlarına işlemesine ve dağıtmasına izin verir. Tek şart, SBL ve Logos'a uygun şekilde atıf yapılmasıdır.15  
* **Dijital Formatlar:** SBLGNT, XML (OSIS uyumlu), düz metin ve syntax ağaçları (syntax trees) şeklinde indirilebilir. Bu formatlar, yazılımın arama motoruna doğrudan entegre edilebilir.16 Ayrıca, MorphGNT projesi tarafından yapılan morfolojik etiketlemeler de mevcuttur, bu da gramer analizi özelliklerinin eklenmesini sağlar.18

### **3.2. Alternatif: Bizans Metni ve Textus Receptus**

Türkiye'deki bazı Protestan toplulukları ve Ortodoks kiliseleri, modern eleştirel metinler (SBLGNT/NA28) yerine geleneksel Bizans metnini tercih edebilir.

* **Robinson-Pierpoint (2005):** Bizans metin türünün en iyi temsilcisidir ve Kamu Malı'dır.  
* **Textus Receptus (Stephen 1550 / Scrivener 1881):** Kamu Malı'dır.  
* **Öneri:** Yazılım, SBLGNT'yi varsayılan "Akademik" metin olarak sunmalı, ancak kullanıcının ayarlardan Robinson-Pierpoint veya Textus Receptus'a geçiş yapmasına izin vermelidir. Bu, hem akademik hem de kilise içi kullanım ihtiyaçlarını karşılar. Tüm bu metinler morphgnt ve open-bibles GitHub depolarında mevcuttur.19

### **3.3. El Yazması Kanıtları: Codex Sinaiticus ve NTVMR**

İleri düzey araştırmacılar için, kritik metnin ötesine geçip el yazmalarının kendisine bakmak önemlidir.

* **Codex Sinaiticus:** Dünyanın en eski tam İncil el yazması olan Sinaiticus'un (M.S. 4\. yy) dijital transkripsiyonu, **CC BY-NC-SA 3.0** lisansı ile mevcuttur. XML formatındaki bu veri, el yazmasındaki düzeltmeleri, sayfa düzenini ve lakunaları (eksik kısımlar) birebir yansıtır. Yazılımda, SBLGNT metninin yanında "Orijinal El Yazması" katmanı olarak sunulabilir.21  
* **NTVMR (New Testament Virtual Manuscript Room):** Münster'deki INTF tarafından yönetilen bu platform, binlerce el yazmasının fotoğrafını ve transkripsiyonunu barındırır. NTVMR, geliştiriciler için bir API sunar (http://ntvmr.uni-muenster.de/community/vmr/api). Bu API kullanılarak, belirli bir ayet için (örn: Yuhanna 1:1) mevcut olan el yazması kanıtlarının listesi ve transkripsiyonları dinamik olarak çekilebilir.23 Ancak, NTVMR verilerinin ticari kullanımı sınırlı olabileceğinden, bu özellik "araştırma eklentisi" olarak sunulmalıdır.

## ---

**4\. Septuagint (LXX) ve Deuterokanonik Kitaplar**

Eski Ahit'in Yunanca çevirisi olan Septuagint, Hristiyan teolojisi ve Yeni Ahit'in Eski Ahit alıntılarını anlamak için kritiktir. Ayrıca Katolik ve Ortodoks kanonlarında yer alan Deuterokanonik kitaplar (Tobit, Yudit, Makkabiler vb.) bu külliyatın içindedir.

### **4.1. Rahlfs 1935 vs. Göttingen Edisyonları**

* **Rahlfs (1935):** Alfred Rahlfs tarafından hazırlanan edisyon, uzun yıllar standart el kitabı olmuştur. Bu edisyonun telif hakkı süresi dolmuş veya akademik amaçlar için kamuya açılmıştır. **CCAT (Center for Computer Analysis of Texts)** tarafından hazırlanan morfolojik olarak etiketlenmiş Rahlfs metni, dijital dünyada en yaygın kullanılan versiyondur.  
  * **Lisans:** Kamu Malı veya çok serbest kullanım hakları.  
  * **Kaynak:** CrossWire (SWORD Project) modülleri veya GitHub üzerindeki eliranwong/LXX-Rahlfs-1935 gibi depolar.25  
* **Göttingen Septuagint / Rahlfs-Hanhart (2006):** Bu edisyonlar en güncel akademik çalışmalardır ancak Alman Kitab-ı Mukaddes Derneği'nin sıkı lisans koruması altındadır. Yazılım projesi için maliyetli ve entegrasyonu zordur.27

**Strateji:** Yazılımın temel LXX metni olarak **CCAT Rahlfs (1935)** kullanılmalıdır. Bu metin, morfolojik analiz imkanı sunar ve Deuterokanonik kitapların tamamını içerir.

## ---

**5\. Genişletilmiş Apokrif ve Pseudepigrapha: Bilinmeyen Metinlerin Dijitalleşmesi**

Standart İncil yazılımlarının çoğu, 66 kitaplık Protestan kanonu ile sınırlı kalır. Ancak akademik bir proje, İkinci Tapınak Dönemi Yahudiliği ve Erken Hristiyanlık metinlerini de kapsamalıdır. "Genişletilmiş Apokrif" terimi burada üç kategoriyi kapsar: Deuterokanonikler (yukarıda LXX içinde ele alındı), Eski Ahit Pseudepigrapha'sı ve Yeni Ahit Apokrifası (Gnostik metinler dahil).

### **5.1. Eski Ahit Pseudepigrapha'sı: OCP Projesi**

1. Hanok (Ethiopic Enoch) ve Jübileler gibi metinler, Yeni Ahit'in arka planını (örn: Yahuda mektubundaki Hanok alıntısı) anlamak için elzemdir.  
* **Online Critical Pseudepigrapha (OCP):** Bu proje, Pseudepigrapha metinlerinin eleştirel edisyonlarını elektronik ortamda yayınlamayı amaçlar.  
  * **Metinler:** 1\. Hanok (Ge'ez/Etiyopça), Jübileler, Süryani Baruch, Süleyman'ın Mezmurları gibi metinleri içerir.  
  * **Format:** TEI XML. Metinler, el yazması varyantlarını gösteren kritik aygıtlarla (apparatus) birlikte kodlanmıştır.28  
  * **Erişim:** Projenin verileri GitHub üzerinde OnlineCriticalPseudepigrapha deposunda barındırılmaktadır. Bu veriler, tarayıcıda görüntülenmek üzere XSLT ile dönüştürülebilir veya doğrudan yazılımın veritabanına JSON olarak işlenebilir.28  
  * **1\. Hanok Özelinde:** 1\. Hanok'un tam metni sadece Etiyopça (Ge'ez) olarak mevcuttur. OCP, R.H. Charles'ın klasik edisyonunu temel alan ancak yeni el yazmalarıyla (Tana 9\) güncellenen bir metin sunar. Yazılımın bu metni gösterebilmesi için Unicode Ge'ez font desteğine (örn: GF Zemen) sahip olması gerekir.30

### **5.2. Yeni Ahit Apokrifası ve Gnostik Metinler: Nag Hammadi**

1945 yılında Mısır'da bulunan Nag Hammadi kütüphanesi, Tomas İncili, Filip İncili ve Yuhanna'nın Apokrifonu gibi Gnostik metinleri gün yüzüne çıkarmıştır. Bu metinlerin orijinal dili Kıptice'dir (Coptic).

* **Coptic SCRIPTORIUM:** Bu proje, Kıptice metinlerin dijitalleştirilmesinde dünya lideridir.  
  * **Veri Kalitesi:** Metinler sadece transkript edilmekle kalmamış, aynı zamanda dilbilimsel olarak analiz edilmiş (POS tagging, lemma, syntax) ve İngilizce çevirileriyle hizalanmıştır.  
  * **Tomas İncili:** Coptic Scriptorium, Tomas İncili'nin (Nag Hammadi Codex II) en güncel ve dilbilimsel olarak zenginleştirilmiş versiyonunu sunar.  
  * **Format ve Lisans:** Veriler **TEI XML** ve **PAULA XML** formatlarında, **CC BY** (Atıf) lisansı ile sunulmaktadır. Bu, verilerin yazılıma entegre edilmesini ve kelime bazlı sözlük sorgulamalarının yapılmasını mümkün kılar.31  
  * **Entegrasyon:** GitHub üzerindeki CopticScriptorium/corpora deposundan indirilen dosyalar, yazılım içinde Gnostik literatür modülü olarak yapılandırılabilir. Kullanıcı, Kıptice metni okurken kelimelerin üzerine tıklayıp Kellia projesinin çevrimiçi Kıptice sözlüğüne (Coptic Dictionary Online) yönlendirilebilir.33

## ---

**6\. Türkiye Bağlamı: 1941 Çevirisi ve Telif Hakkı Analizi**

Projenin hedef kitlesi Türkiye olduğu için, Türkçe İncil metninin seçimi ve lisans durumu en kritik stratejik karardır. Türkiye'de İncil çevirileri tarihsel olarak karmaşık bir süreç izlemiştir.

### **6.1. 1941 "Eski Çeviri" (MacCallum) ve Hukuki Statü**

Cumhuriyet döneminin ilk Latin harfli tam Kitab-ı Mukaddes çevirisi 1941 yılında yayınlanmıştır. Bu çeviri, Dr. Frederick W. MacCallum liderliğindeki bir heyet tarafından, 1928 Harf Devrimi ve Dil Devrimi'nin ilkelerine uygun olarak hazırlanmıştır.34

* **Telif Hakkı Analizi (Forensic Analysis):**  
  * Türkiye Cumhuriyeti 5846 Sayılı Fikir ve Sanat Eserleri Kanunu'na göre, eser koruma süresi yazarın ölümünden itibaren 70 yıldır (Madde 27).  
  * Çevirinin baş mimarı **Frederick William MacCallum**, 28 Kasım 1945 tarihinde İstanbul'da vefat etmiştir.36  
  * Hesaplama: ![][image1]. Dolayısıyla, eserin telif hakkı koruması **1 Ocak 2016** itibarıyla sona ermiş ve eser **Kamu Malı (Public Domain)** statüsüne geçmiştir.38  
  * **Kurumsal Eser İddiası:** Eğer eser, Kitabı Mukaddes Şirketi (KMŞ) tüzel kişiliği altında "kolektif eser" veya tüzel kişi eseri olarak değerlendirilseydi, koruma süresi yayın tarihinden itibaren 70 yıl olacaktı (Madde 26). Bu durumda süre ![][image2] yılında dolmuş olacaktı. Her iki senaryoda da (yazar ölümü veya yayın tarihi), 1941 çevirisi şu an **Kamu Malı'dır**.  
* **Dijital Kaynak:** GitHub'daki seven1m/open-bibles deposunda bulunan tur-turkish.osis.xml dosyası, bu 1941 metnini içerir ve "Public Domain" olarak etiketlenmiştir. Bu dosya, yazılımın Türkçe metin omurgasını oluşturmak için en güvenli yasal kaynaktır.40

### **6.2. 2001/2008 "Yeni Çeviri" (Kutsal Kitap) ve Riskler**

Kitabı Mukaddes Şirketi, dilin eskimesi nedeniyle 2001 yılında "Kutsal Kitap \- Yeni Çeviri" adıyla modern bir versiyon yayınlamıştır.

* **Yasal Durum:** Bu çeviri tamamen telif haklarıyla korunmaktadır. KMŞ, bu metnin izinsiz dijital kullanımına karşı yasal yaptırımlar uygulayabilir. API erişimi veya veritabanı kullanımı için özel lisans anlaşması ve ücret ödenmesi gerekir.42  
* **Strateji:** Yazılım projesi, varsayılan olarak **1941 Çevirisini** (kamu malı) kullanmalıdır. Kullanıcı arayüzünde bu metin "Klasik Çeviri" veya "1941 Metni" olarak adlandırılmalıdır. Eğer bütçe elverirse, 2001 çevirisi için KMŞ ile lisans görüşmesi yapılabilir, ancak projenin varlığı bu lisansa bağlı olmamalıdır.

### **6.3. Tarihsel Bir Hazine: Ali Bey (1666) Çevirisi**

Sultan IV. Mehmed'in baş tercümanı Leh asıllı Müslüman Ali Bey (Wojciech Bobowski) tarafından 17\. yüzyılda yapılan çeviri, Türk İncil tarihinin temel taşıdır. Bu metin kamu malıdır. Yazılımın "Tarihsel Metinler" modülüne eklenmesi, projeye büyük bir akademik prestij kazandıracaktır. Ali Bey'in metni, Osmanlı Türkçesi ile yazılmıştır ve modern kullanıcılar için zor olabilir, ancak araştırmacılar için eşsizdir.44

## ---

**7\. Teknik Mimari ve Entegrasyon Stratejisi**

Elde edilen bu heterojen veri kaynaklarının (WLC, SBLGNT, OCP, Coptic Scriptorium) tek bir yazılım çatısı altında toplanması, sağlam bir veri mimarisi gerektirir.

### **7.1. Veri Formatları ve Dönüşüm Hattı (Pipeline)**

* **OSIS (Open Scripture Information Standard):** İncil metinleri (Eski ve Yeni Ahit, Türkçe Çeviri) için endüstri standardıdır. XML tabanlıdır ve ayet referanslarını (Gen.1.1) hiyerarşik bir yapıda tutar. open-bibles ve openscriptures depoları zaten bu formattadır. Yazılımın "Parser" modülü, OSIS dosyalarını okuyup uygulamanın yerel veritabanına (SQLite veya NoSQL) aktarmalıdır.46  
* **TEI (Text Encoding Initiative):** Pseudepigrapha ve Gnostik metinler (OCP, Coptic Scriptorium) TEI formatındadır. TEI, OSIS'ten daha karmaşıktır; el yazması varyantlarını (\<app\>, \<rdg\>), sayfa düzenini (\<pb\>, \<cb\>) ve hasarlı kısımları (\<gap\>) kodlar. Yazılımın bu dosyaları işlemek için özel bir XSLT işlemcisine veya TEI-to-HTML dönüştürücüsüne ihtiyacı olacaktır.48  
* **JSON:** Sefaria'dan çekilen veriler JSON formatındadır. Bu, modern web ve mobil uygulamalar (React, Flutter) için en kolay işlenen formattır.

### **7.2. Backend Önerisi: SWORD Engine**

Sıfırdan bir İncil motoru yazmak yerine, CrossWire Society'nin geliştirdiği **SWORD Engine** (veya Java portu JSword) kütüphanesini kullanmak stratejik bir avantajdır.

* SWORD kütüphaneleri, OSIS ve TEI metinlerini sıkıştırılmış modüller halinde saklar, hızlı arama (indexing) yapar ve Strong numaralarıyla morfoloji eşleşmesini yönetir.  
* C++, C\#, Java ve Python wrapper'ları mevcuttur.50

### **7.3. Mimari Şema Önerisi**

1. **Veri Katmanı:**  
   * *Yerel Veritabanı:* WLC (İbranice), SBLGNT (Yunanca), 1941 Türkçe, Rahlfs LXX. (Çevrimdışı erişim için cihazda saklanır).  
   * *Uzak Veri (On-Demand):* Codex Sinaiticus görselleri, NTVMR el yazması transkripsiyonları, Sefaria yorumları (API ile çağrılır).  
2. **İş Mantığı (Business Logic):**  
   * *Ayet Eşleştirme (Versification Mapping):* Masoretik Metin ile LXX veya Türkçe çeviri arasındaki ayet numarası farklarını (örn: Mezmurlar) yöneten "K11n" sistemi.  
   * *Morfoloji Motoru:* Kullanıcı İbranice kelimeye tıkladığında OSHB verisinden lemma ve gramer bilgisini çeken servis.  
3. **Sunum Katmanı (UI):**  
   * Çoklu panel (Polyglot) görünüm.  
   * Kritik aygıt (apparatus) dipnotlarının interaktif gösterimi.

## ---

**8\. Sonuç ve Eylem Planı**

"Kitab-ı Mukaddes" yazılım projesi, doğru kaynaklar seçildiği takdirde, lisans ücretlerine boğulmadan dünya standartlarında bir akademik araç olabilir.

**Temel Kazanımlar:**

1. **Hukuki Güvenlik:** 1941 Türkçe çevirisinin Kamu Malı statüsü ve SBLGNT/OSHB'nin açık lisansları, projenin yasal zeminini sağlamlaştırmaktadır.  
2. **Akademik Derinlik:** Sadece standart metinleri değil, OCP ve Coptic Scriptorium verileriyle Apokrif literatürü de entegre etmek, yazılımı rakiplerinden (YouVersion vb.) ayırarak bir "araştırma platformu" haline getirecektir.  
3. **Sürdürülebilirlik:** Açık formatlar (OSIS/TEI) ve açık kaynaklı motorlar (SWORD) kullanmak, projenin gelecekteki geliştirmelere açık olmasını sağlar.

**Önerilen İlk Adım:** GitHub üzerindeki seven1m/open-bibles (Türkçe), openscriptures/morphhb (İbranice) ve logosbible/SBLGNT (Yunanca) depolarının fork edilerek verilerin doğrulanması ve bir prototip veritabanına işlenmesidir.

Bu rapor, projenin teknik ve metinsel altyapısını kurmak için gerekli tüm akademik ve yasal kanıtları sunmaktadır.

---

**Tablo 1: Önerilen Metin Kaynakları ve Lisans Matrisi**

| Metin Grubu | Edisyon / Versiyon | Kaynak Deposu (Repo) | Format | Lisans Durumu |
| :---- | :---- | :---- | :---- | :---- |
| **Eski Ahit** | Westminster Leningrad Codex (UXLC) | tanach.us / openscriptures | XML (OSIS) | Kamu Malı (Metin) / CC BY 4.0 (Morfoloji) |
| **Yeni Ahit** | SBL Greek New Testament | logosbible/SBLGNT | XML (OSIS) | CC BY 4.0 |
| **Türkçe İncil** | 1941 "Eski Çeviri" (MacCallum) | seven1m/open-bibles | XML (OSIS) | Kamu Malı (Türkiye \- 70 Yıl Kuralı) |
| **Septuagint** | Rahlfs (1935) | CCAT / CrossWire | XML/TXT | Kamu Malı / Açık Erişim |
| **Pseudepigrapha** | 1\. Hanok, Jübileler | Online Critical Pseudepigrapha | TEI XML | Açık Erişim (Akademik) |
| **Gnostik** | Nag Hammadi (Tomas İncili) | Coptic Scriptorium | TEI/PAULA | CC BY |
| **El Yazmaları** | Codex Sinaiticus | codexsinaiticus.org | TEI XML | CC BY-NC-SA 3.0 |

---

**Tablo 2: Dijital Entegrasyon Teknolojileri**

| Bileşen | Teknoloji / Standart | Kullanım Amacı |
| :---- | :---- | :---- |
| **Veri Standardı** | OSIS (Open Scripture Information Standard) | İncil metinlerinin (ayet, bölüm) yapılandırılması. |
| **Kritik Metinler** | TEI P5 (Text Encoding Initiative) | Varyantlar, el yazması detayları ve apokrif metinler için. |
| **API** | Sefaria API (JSON) | Yahudi yorumları ve Midraş literatürü entegrasyonu. |
| **Backend Motoru** | SWORD / JSword | Metin işleme, arama, sıkıştırma ve modül yönetimi. |
| **Font Desteği** | Unicode (NFC) | İbranice (Ezra SIL), Yunanca (Gentium), Kıptice (Antinoou), Etiyopça (GF Zemen). |

#### **Works cited**

1. The Aleppo Codex : Shlomo ben Buya'a : Free Download, Borrow, and Streaming, accessed February 2, 2026, [https://archive.org/details/Aleppo\_Codex](https://archive.org/details/Aleppo_Codex)  
2. Open Source Bible Data, accessed February 2, 2026, [http://simoncozens.github.io/open-source-bible-data/](http://simoncozens.github.io/open-source-bible-data/)  
3. Tanach.us, accessed February 2, 2026, [https://tanach.us/](https://tanach.us/)  
4. v2/translations.json at master · getbible/v2 \- GitHub, accessed February 2, 2026, [https://github.com/getbible/v2/blob/master/translations.json](https://github.com/getbible/v2/blob/master/translations.json)  
5. biblenerd/awesome-bible-developer-resources \- GitHub, accessed February 2, 2026, [https://github.com/biblenerd/awesome-bible-developer-resources](https://github.com/biblenerd/awesome-bible-developer-resources)  
6. openscriptures/morphhb: Open Scriptures Hebrew Bible \- GitHub, accessed February 2, 2026, [https://github.com/openscriptures/morphhb](https://github.com/openscriptures/morphhb)  
7. Open Scriptures Hebrew Bible, accessed February 2, 2026, [https://hb.openscriptures.org/](https://hb.openscriptures.org/)  
8. German Bible Society, accessed February 2, 2026, [https://www.die-bibel.de/en](https://www.die-bibel.de/en)  
9. Rights Bibelverses \- Deutsche Bibelgesellschaft, accessed February 2, 2026, [https://www.die-bibel.de/en/rights](https://www.die-bibel.de/en/rights)  
10. Licensing and the German Bible Society \- Google Groups, accessed February 2, 2026, [https://groups.google.com/g/openscriptures/c/9XcB\_4Ua6QU](https://groups.google.com/g/openscriptures/c/9XcB_4Ua6QU)  
11. How to Find and Understand Licensing Information \- Sefaria Help Center, accessed February 2, 2026, [https://help.sefaria.org/hc/en-us/articles/18490043237148-How-to-Find-and-Understand-Licensing-Information](https://help.sefaria.org/hc/en-us/articles/18490043237148-How-to-Find-and-Understand-Licensing-Information)  
12. Versions \- Sefaria, accessed February 2, 2026, [https://developers.sefaria.org/reference/get-versions](https://developers.sefaria.org/reference/get-versions)  
13. Download \- SBL Greek New Testament, accessed February 2, 2026, [https://sblgnt.com/download/](https://sblgnt.com/download/)  
14. SBL Greek New Testament, accessed February 2, 2026, [https://sblgnt.com/](https://sblgnt.com/)  
15. End User License Agreement \- SBL Greek New Testament, accessed February 2, 2026, [https://www.sblgnt.com/license/](https://www.sblgnt.com/license/)  
16. aaronshaf/sblgnt: The Greek New Testament: SBL Edition \- GitHub, accessed February 2, 2026, [https://github.com/aaronshaf/sblgnt](https://github.com/aaronshaf/sblgnt)  
17. Querying Greek Texts in XML: Part 1 \- Biblical Humanities, accessed February 2, 2026, [http://biblicalhumanities.org/xquery/tutorial/greek/2015/11/13/querying-000.html](http://biblicalhumanities.org/xquery/tutorial/greek/2015/11/13/querying-000.html)  
18. jcuenod/awesome-bible-data \- GitHub, accessed February 2, 2026, [https://github.com/jcuenod/awesome-bible-data](https://github.com/jcuenod/awesome-bible-data)  
19. Dashboard \- Biblical Humanities, accessed February 2, 2026, [http://biblicalhumanities.org/dashboard/](http://biblicalhumanities.org/dashboard/)  
20. How to Access the Bible via API or Download the Bible as Data \- Get.Bible, accessed February 2, 2026, [https://get.bible/bible-data-sets/](https://get.bible/bible-data-sets/)  
21. XML Download of the Electronic Transcription of Codex Sinaiticus, accessed February 2, 2026, [https://codexsinaiticus.org/en/project/transcription\_download.aspx](https://codexsinaiticus.org/en/project/transcription_download.aspx)  
22. Specifying XML source for Codex Sinaiticus, accessed February 2, 2026, [https://www.codexsinaiticus.org/download/XMLspecs\_sinaiticus.pdf](https://www.codexsinaiticus.org/download/XMLspecs_sinaiticus.pdf)  
23. Exploring the New Testament Virtual Manuscript Room API \- The Digital Orientalist, accessed February 2, 2026, [https://digitalorientalist.com/2025/04/29/exploring-the-new-testament-virtual-manuscript-room-api/](https://digitalorientalist.com/2025/04/29/exploring-the-new-testament-virtual-manuscript-room-api/)  
24. A Guide for Using the New Testament Virtual Manuscript Room (Part 3), accessed February 2, 2026, [https://digitalorientalist.com/2023/10/13/a-guide-for-using-the-new-testament-virtual-manuscript-room-part-3/](https://digitalorientalist.com/2023/10/13/a-guide-for-using-the-new-testament-virtual-manuscript-room-part-3/)  
25. LXX / Septuagint (Rahlfs; 1935\) \- Interlinear \- BibleBento, accessed February 2, 2026, [https://biblebento.com/lxx1i/lxx1i.html](https://biblebento.com/lxx1i/lxx1i.html)  
26. Greek Septuagint (Rahlfs) revised and tagged \- Accordance, accessed February 2, 2026, [https://www.accordancebible.com/product/greek-septuagint-rahlfs-revised-and-tagged/](https://www.accordancebible.com/product/greek-septuagint-rahlfs-revised-and-tagged/)  
27. Trustworthy, Freely Available Primary Sources for Biblical Studies \- The Digital Orientalist, accessed February 2, 2026, [https://digitalorientalist.com/2020/10/09/trustworthy-freely-available-primary-sources-for-biblical-studies/](https://digitalorientalist.com/2020/10/09/trustworthy-freely-available-primary-sources-for-biblical-studies/)  
28. OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha: A project to develop electronic texts of the "Old Testament Pseudepigrapha" along with the software tools to edit and publish them. \- GitHub, accessed February 2, 2026, [https://github.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha](https://github.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha)  
29. Online Critical Pseudepigrapha \- The Digital Classicist Wiki, accessed February 2, 2026, [https://wiki.digitalclassicist.org/Online\_Critical\_Pseudepigrapha](https://wiki.digitalclassicist.org/Online_Critical_Pseudepigrapha)  
30. Text-critical Edition and Translation of 1 Enoch \- DFG \- GEPRIS, accessed February 2, 2026, [https://gepris.dfg.de/gepris/projekt/270668285?language=en](https://gepris.dfg.de/gepris/projekt/270668285?language=en)  
31. Public repository for Coptic SCRIPTORIUM Corpora Releases \- GitHub, accessed February 2, 2026, [https://github.com/CopticScriptorium/corpora](https://github.com/CopticScriptorium/corpora)  
32. Coptic Scriptorium, accessed February 2, 2026, [https://data.copticscriptorium.org/](https://data.copticscriptorium.org/)  
33. KELLIA \- Coptic SCRIPTORIUM Blog, accessed February 2, 2026, [https://blog.copticscriptorium.org/topics/kellia/](https://blog.copticscriptorium.org/topics/kellia/)  
34. Bible translations into Turkish \- Wikipedia, accessed February 2, 2026, [https://en.wikipedia.org/wiki/Bible\_translations\_into\_Turkish](https://en.wikipedia.org/wiki/Bible_translations_into_Turkish)  
35. Telechaje Turkish Bible Old Translation 1941 | KMEYA Bib | 100% Gratis, accessed February 2, 2026, [https://www.bible.com/ht/versions/2028-kmeya-turkish-bible-old-translation-1941](https://www.bible.com/ht/versions/2028-kmeya-turkish-bible-old-translation-1941)  
36. Frederick Maccallum Family History Records \- Ancestry®, accessed February 2, 2026, [https://www.ancestry.com/genealogy/records/results?firstName=frederick\&lastName=maccallum](https://www.ancestry.com/genealogy/records/results?firstName=frederick&lastName=maccallum)  
37. Private Frederick William McCallum | War Casualty Details 399444 | CWGC, accessed February 2, 2026, [https://www.cwgc.org/find-records/find-war-dead/casualty-details/399444/frederick-william-mccallum/](https://www.cwgc.org/find-records/find-war-dead/casualty-details/399444/frederick-william-mccallum/)  
38. Commons:Copyright rules by territory/Turkey, accessed February 2, 2026, [https://commons.wikimedia.org/wiki/Commons:Copyright\_rules\_by\_territory/Turkey](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Turkey)  
39. Telif Hakkı Kaç Yıl Süreyle Korunur? \- Telif Hakları, accessed February 2, 2026, [https://telifhaklari.ktb.gov.tr/TR-332373/telif-hakki-kac-yil-sureyle-korunur.html](https://telifhaklari.ktb.gov.tr/TR-332373/telif-hakki-kac-yil-sureyle-korunur.html)  
40. tur-turkish.osis.xml \- seven1m/open-bibles \- GitHub, accessed February 2, 2026, [https://github.com/seven1m/open-bibles/blob/master/tur-turkish.osis.xml](https://github.com/seven1m/open-bibles/blob/master/tur-turkish.osis.xml)  
41. README.md \- seven1m/open-bibles \- GitHub, accessed February 2, 2026, [https://github.com/seven1m/open-bibles/blob/master/README.md](https://github.com/seven1m/open-bibles/blob/master/README.md)  
42. Download the Bible in Türkçe \- Turkish \- Download now or read online. | YouVersion, accessed February 2, 2026, [https://www.bible.com/et/languages/tur](https://www.bible.com/et/languages/tur)  
43. A History of Turkish Bible Translations \- WordPress.com, accessed February 2, 2026, [https://historyofturkishbible.files.wordpress.com/2014/03/turkish-bible-history-version-s-in-preparation.pdf](https://historyofturkishbible.files.wordpress.com/2014/03/turkish-bible-history-version-s-in-preparation.pdf)  
44. (PDF) In-between Calvinism and Islam: Ali Bey's Transcultural Translation of the Bible into Turkish in the Time of Confessionalization \- ResearchGate, accessed February 2, 2026, [https://www.researchgate.net/publication/373139900\_In-between\_Calvinism\_and\_Islam\_Ali\_Bey's\_Transcultural\_Translation\_of\_the\_Bible\_into\_Turkish\_in\_the\_Time\_of\_Confessionalization](https://www.researchgate.net/publication/373139900_In-between_Calvinism_and_Islam_Ali_Bey's_Transcultural_Translation_of_the_Bible_into_Turkish_in_the_Time_of_Confessionalization)  
45. Wojciech Bobowski: The Pole Who Bridged the East & West | Article \- Culture.pl, accessed February 2, 2026, [https://culture.pl/en/article/wojciech-bobowski-the-pole-who-bridged-the-east-west](https://culture.pl/en/article/wojciech-bobowski-the-pole-who-bridged-the-east-west)  
46. Open Scripture Information Standard \- Wikipedia, accessed February 2, 2026, [https://en.wikipedia.org/wiki/Open\_Scripture\_Information\_Standard](https://en.wikipedia.org/wiki/Open_Scripture_Information_Standard)  
47. Bibles — OpenLP 3.0 Reference Manual, accessed February 2, 2026, [https://manual.openlp.org/bibles.html?highlight=osis](https://manual.openlp.org/bibles.html?highlight=osis)  
48. TEIC/TEI: The Text Encoding Initiative Guidelines \- GitHub, accessed February 2, 2026, [https://github.com/TEIC/TEI](https://github.com/TEIC/TEI)  
49. EpiDoc: Epigraphic Documents in TEI XML, accessed February 2, 2026, [https://epidoc.stoa.org/](https://epidoc.stoa.org/)  
50. SWORD API Development \- The CrossWire Bible Society, accessed February 2, 2026, [https://www.crosswire.org/sword/develop/swordapi/index.jsp](https://www.crosswire.org/sword/develop/swordapi/index.jsp)  
51. crosswire/jsword \- GitHub, accessed February 2, 2026, [https://github.com/crosswire/jsword](https://github.com/crosswire/jsword)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJIAAAAXCAYAAADgBhblAAAFOUlEQVR4Xu2Za+ilUxTGH6HI/TrkMpNbrrkOKbcPckmkoSjK5Atp8sGIUuSLchkllHJJvkgUSUpSjkuT+IAySBRyiRqi4QO5rJ91Vme/+93v5cw5Z+av3qeezvmvd//3u/dez1p77X2kAQMGDBgwYMCAAX1xUG7IsLPxYOP2+YMCtjFelRsNO+UGwz7GHXPjArG/8WbjbvmDBtD+dOO+8nltTfD+vYzLjTtkz1LsbjzJeLi6/UWfpfXHV7vmRrWs2zLjfcY/8gdj7Gd83rjJODJuNF6h9kU9zfhbbjT8Y/zc+JTxUeO3xs+Mh6aNFoyVxt/lY/nO+HXG6ydNdbbxfflY+dyQPNvSOML4jvFH41/y8T+oenDirx/ka/yi3F/bVlo48N9hxieNJ2fPwMXyd+Aj5k9/+O6XtBEgwhgQixoDy3Gg8T25s4kCXr7a+KfxskmzCoiYd1XuD1vK9cYVaYMpcLRx79zYA6tUH0fKU8ft+PxZEycQ2SzoieO/tyRY+7eN58t9gF/elI/3taQd2YK/yfIB/LQ2+Rt8LP/fX8efbUJKiZAIxCLYskbyhjm+kNtZ/EC0/zuxBS4xvmy8W+X+UPW8QF9Mdlo8bjw3s21nfEQuFHCUPJIJohQI93vjIZl9kSDjIA7W8yv5Vgt2Mb41tjN+tjrWniDPQZtSqUFf9NkkpJHc373QJiS2J+ypw2LApfZEDRF7q8rPl4KQ1qieBYla5hT7f0TjKBqMwVphvzCzLxJkoPvl731VE8emfkNsIYqmkoIAyrEkhUTqjxTaJiQGf7s8+rsK/DZsrpByHGP8cPwZiPGPEhsIIV2X2RcNxLSHqrUO2ZGaLdYZMeCvJiHhs7xA7yOkA+S+uldeTjCWItqEVNra0pSaDoyojuq/SUgU7K8bL5Dv+6RhMkTj4FowLyG9ZLwzs3UJiedNOM54+RS8VJtf61FeUMeBLiGNVM8uXUKiLw4Z+OpGub/WpY1StAnpAbn9tsR2rHzw2GNgK1Rd9CYhsdenx8cX5IU+tdW0mJeQOOEwpxRLXUhxoGHt4tAzbyGtlL8DEQGC/R6V/fof2oQEOE4+Kz/dfSp3+tOatL/a+ISq9xVNQsoRJ6hv5CeREt5Q/YgOua74qWCnnqD47IMzVK7bZhHSosH2xhUAd1sp5i2kEhAXOuCzhi4hBRAKk0jbx/fcoZvGz/n+jLwYJFLJSERTIIpaJt93MoF5ZKS7VM22ga5ie9b3bi7ICrfI738Ce8oDp6vYLgVMk5Cwj4wfyO+vAiHW4vzbhIQALlJ14BRfXxo/0eSmlRenfE7eH995TjuimFR8jia4Sd6OWmxZYu+DWYUUx+pSdjlefseyIbMzxo3y64EmPCSfU19S5+TXESWwhqvlJ7cUsQYxn9K1DO8pHRCahBSBBK9N7JxWsbE+NbQJKRzNgsY+fqV8sGujUQE4Oe+PQRBN6RbIzSztHtb0BfesQopFLAmJQ8Mr8jujFAgIe+knhUWDWoh3H6lq0D6WtFmj+rpzIKKmzetA0CQkhMKN9jpVa1rESP+V+UeaLjEctFx+NOaUxhGQ/ZH7iPxaPsCg8r5GmuzNFG/RF1lrvep3On0xq5Di0rGpD4R9g9xRFMV8Mv9pBT8r0kAvMd/KTpCvMxeQJAJElPur5KfoK0SFgPDRR/K15qeR1pvtLpBBzpIPbJZ7H0Bfp8j7IrOVfgPqi1mFhCBYtK7swjuuMZ6nukOWKsJfBMAsPsM/BBy+wm9dPwD/L3GH8czcOGDAgAEDBgwYMGDA1sS/xMiKTu8XI2MAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJIAAAAXCAYAAADgBhblAAAEZ0lEQVR4Xu2ZW4hNURjHP6HI/TrkMpOQy8gtpFxeRBIJhSjzRponI8qDvCglJR6US/IiUUpSkofj8iAe5MElpfBAFErDA7l8/779ddb+zjqz9sw5Z89+WL/6d8751pq9117rv9b+1hqiSCQSiUQikUhWJtmAYTBrMqu/LfDQh7XDBg1DbSAnxrP2s4bZgiqg/lLWWJLn6k1w/1GsZtYAU+YynLWANY3C44VrDrRBA8qnUOD5m1jHWb9sQcI41nVWJ6vE+sLaSl1fdAnrhw0moAO2s97ZgpxYxPrJ+sf6wHpvtKdclVaynrLOJp/PnbK8mc56xPrM+kPS/lOsQW4lkvH6xLrEukEyXn1TNQSM31TWRdZCU+YCI+LZSySLSQWYYWgQOlUbZpnIesJ6TTILcPM21m/W5nK1FJgxj8l/PZhR7+kr7w6zWKNtMAObSO5dTYuTevj8RuVBQIfCUPOT33mCvn/IWkMyBhiX+yTtvevUwyqL32OcGMapw/kNXpD87ffk02ckTKivVO6XElUxkoLCEvkH9g1JHJ2vaP2/TkzZwLrFOkb+6ykHqevyLGDGrbfBDJxnrTKxfqwzJEYBM0lmMiaRC4z7kWSZzwusODAH+gurOF61YAjrQRJH+7HSo+8xyS2o40s1cC1c02ckl5qNhNcT4u6AaYN99TFrMGNDRgmVZ6GnRmpntZgYZi2eSfMmXFc7zwV9hfhaE28kWIFOkNz3DpUH0x03mE1N4UspUAcTyFJII2Hp1yU0ZJRQeRZ6aiTLbNaz5FPR9pWcGFAj7TbxRgMzjaB0roPVETmb9iPMgPGqZiSMmU3QczOS79XmLqluwzCrNfsPGSVUnoV6Gekm64iJhYyE8mrMYW3phjZSz3M9pBfI40DISCWqNEJuRjpJEj/kxFpJGo+4XriF0p0eMkqoPAv1MhJ2OHgml6IbSTc02LjopqfQRgLYTl4l2Wm9IkmoL1O5/k7WBUqfV4SMEip3uUeVW3QIxxXYVdg48gkkn1lYRmJISy1GajR4veEIAGdbLoU3kgKj4CHc+vrdDmhnUo7vV6jyrKM7RqpGPVako5RebZVQsl3rfXsKcqUDJOc/ykiSiRNKtn0TJjcjwQDrKN3wCay3rJdUPmlFg1xdI7kevqMc9VyKYCTdVvtWl7kkZyxIZl2aSI4FcDxQjdMkz5ZVyHPscYQP9GEbyc7NRftAn8d3LIP7+DYIuRlpH0kcHarv8W0kje3QSh4wyL7rKUUwknaiz0jYNNwmOTNygYEQD/1LoREgF8K9Z1B60p5z6rRTZb9iQ4ScttXEQV2MpMu0TzpAzSRbY+zScFiHPAnnEfZVpaBR9lolKjfAlql8y26IWo2kh47VroEVYC/JQCEpxiee366ujcad6D7ZV9k8kkQcB5BYCGAiO16+cdJrqan09e6T11AhkButIGlY6B+7eVKrkWAIdFpodcE9drFWU+WAFBUdL0yAIo1ZITnMWm6DkUgkEolEIpFIb/IfuXBzvmEg8ioAAAAASUVORK5CYII=>
