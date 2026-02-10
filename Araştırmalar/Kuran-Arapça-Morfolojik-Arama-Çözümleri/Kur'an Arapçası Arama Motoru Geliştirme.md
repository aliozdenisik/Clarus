# **Kur'an-ı Kerim Dijital Muhafızlığı: Kutsal Metinler İçin Yüksek Hassasiyetli Morfolojik Arama Mimarisi ve Python Uygulama Stratejileri**

## **1\. Giriş: Kutsal Metin Mühendisliğinin Teolojik ve Teknik Paradoksu**

Kur'an-ı Kerim'in dijital ortamda işlenmesi ve aranabilir hale getirilmesi, yalnızca bir yazılım mühendisliği problemi değil, aynı zamanda filolojik hassasiyet ve teolojik sorumluluk gerektiren multidisipliner bir meydan okumadır. Bir "kutsal yazılım mühendisi araştırmacısı" perspektifinden bakıldığında, kutsal metnin dijitalleşmesi, verinin herhangi bir metin yığını (string) olarak değil, her harfinin, harekesinin ve durağının (*vakıf*) anlam taşıdığı, değiştirilemez bir "kutsal veri yapısı" olarak ele alınmasını zorunlu kılar. Kullanıcının Python tabanlı bir uygulama geliştirirken karşılaştığı "ek ve köklerin sorun olması" durumu, aslında Sami dillerinin hesaplamalı dilbilimdeki (Computational Linguistics) en temel zorluğu olan "bitişken morfoloji" (*agglutinative morphology*) ve "kök-desen" (*root-pattern*) yapısının, Kur'an Arapçası'nın arkaik ve kendine has imlasıyla (*Rasm-i Osmani*) birleşmesinden kaynaklanan derin bir mimari sorundur.

Modern Standart Arapça (MSA) için geliştirilmiş genel amaçlı arama motorları ve doğal dil işleme (NLP) kütüphaneleri, Kur'an metni üzerinde uygulandığında genellikle başarısız olur veya yanıltıcı sonuçlar üretir.1 Örneğin, modern bir haber metninde "görmek" fiili "رأى" (*ra'a*) şeklinde yazılırken, Kur'an imlasında bu kelime bazen "رءا" şeklinde, bazen de hemzenin konumu veya elifin düşmesiyle farklı grafik formlarda karşımıza çıkar. Standart bir Python kütüphanesi (örneğin basit bir regex normalleştiricisi), bu iki formu eşleştirmekte yetersiz kalabilir. Bu durum, arama sorgusunda "İbrahim" kelimesini arayan bir kullanıcının, Kur'an'da sıklıkla geçen ve elifsiz yazılan "İbrahm" (*إبرهم*) formlarını kaçırmasına, dolayısıyla "recall" (geri çağırma) oranının düşmesine neden olur. Bir mühendis için bu bir "bug" (hata) iken, kutsal metin araştırmacısı için bu, vahyin korunmuş yapısının (imlasının) teknolojik standartlarla uyumsuzluğudur.

Bu rapor, Kur'an Arapçası'nın morfolojik karmaşıklığını ve Python ekosistemindeki çözüm yollarını, "ek ve kök sorunu"nu merkeze alarak derinlemesine incelemektedir. Raporda, metin madenciliği, morfolojik analiz, kök çıkarma algoritmaları ve semantik arama teknolojileri, kutsal metnin dokunulmazlığı ilkesiyle harmanlanarak sunulacaktır. Hedefimiz, "ekleri sıyırıp köke inen" ancak bu süreçte anlamı tahrip etmeyen, "kutsal bir arama motoru" mimarisi inşa etmektir.

## **2\. Dilbilimsel Ayrışma: Kur'an Arapçası ve Modern Standart Arapça Arasındaki Hesaplamalı Farklar**

Bir arama sistemi tasarlarken ilk adım, işlenen verinin doğasını anlamaktır. Kur'an Arapçası (Klasik Arapça veya *Fushâ et-Turâs*), modern algoritmaların eğitildiği veri setlerinden (örneğin gazete metinleri) yapısal ve sözlüksel olarak ayrılır.2

### **2.1 İmla Farklılıkları ve "Rasm-i Osmani" Engeli**

Kur'an'ın yazılış biçimi olan *Rasm-i Osmani*, modern imla kurallarından (*Rasm-i İmlaî*) sapmalar gösterir. Bu sapmalar, arama motorlarının "normalizasyon" (standartlaştırma) katmanında kritik hatalara yol açar.

* **Elif Hazfi (Elif'in Düşmesi):** Modern Arapça'da uzun "a" sesi genellikle "elif" (ا) ile gösterilirken, Kur'an'da bu harf sıklıkla düşer ve yerine "hançer elifi" (superscript aleph) gelir. Python'da unicodedata modülü ile yapılan standart bir normalizasyon, hançer elifini tamamen silebilir veya yanlış karakterle eşleştirebilir. Örneğin, "Kitap" (*Kitâb*) kelimesi modern imlada "كتاب" iken, Kur'an'da genellikle "كتٰب" (elif hazfiyle) yazılır. Arama algoritması bu iki formu eşleştiremezse, sistemin güvenilirliği çöker.1  
* **Hemze ve Vav Varyasyonları:** "Hayat" (*Hayât*) veya "Salât" (Namaz) kelimeleri, Kur'an imlasında genellikle "vav" harfi üzerine yazılmış bir elif ile (صَلَوٰةَ) gösterilir. Modern bir stemmer (gövdeleyici), bu kelimeyi köküne indirgerken "vav" harfini kök harfi sanabilir ve kelimeyi yanlış analiz eder.3

### **2.2 Morfolojik Yoğunluk ve "Yapışkan" Ekler**

Arapça, "concatenative" (eklemeli) bir dildir ancak Kur'an Arapçası'nda bu eklemeler, modern metinlere göre çok daha yoğun ve iç içedir. Tek bir grafik kelime (boşluklarla ayrılmış token), tam bir cümle yapısı içerebilir.

* **Örnek Vaka:** "Feseyekfîkehumu" (فَسَيَكْفِيكَهُمُ) – "Allah onlara karşı sana yetecektir."  
  * **Fa- (فَ):** Bağlaç (Ve/Böylece)  
  * **Se- (سَ):** Gelecek zaman eki  
  * **Yekfî (يَكْفِي):** Fiil kökü (Kefâ \- Yetti)  
  * **Ke- (كَ):** Nesne zamiri (Seni)  
  * **Humu (هُمُ):** İkinci nesne zamiri (Onları)

Bir Python kütüphanesi olan NLTK içindeki ISRI Stemmer gibi kural tabanlı algoritmalar, bu kelimeye yaklaştığında genellikle agresif bir kesme işlemi uygular. Kelimenin sonundaki "-humu"yu ve başındaki "fese-"yi atabilir, ancak ortada kalan yapıyı doğru kök olan "K-F-Y" (kefiye) yerine, yanlış bir köke ("K-F-K" gibi) indirgeyebilir. Kur'an Arapçası'nda zamirlerin (clitics) yoğun kullanımı, basit "prefix/suffix stripping" (ön-ek/son-ek sıyırma) yöntemlerini yetersiz kılar.4

### **2.3 Kök ve Anlam Arasındaki Kutsal Bağ**

Modern arama motorlarında "stemming" (gövdeleme), kelimenin morfolojik varyasyonlarını birleştirmek için kullanılır. "Koşuyor", "koştu", "koşar" kelimeleri "koş" gövdesinde birleşir. Ancak Kur'an'da kökler teolojik kavramlardır. "K-F-R" kökü; "küfür" (inkar), "kâfir" (inkarcı), "kefaret" (örtmek/telafi etmek) ve "çiftçi" (tohumu toprağa örten) anlamlarına gelebilir. "Kutsal yazılım mühendisi" için, arama sistemi bu nüansları yönetebilmelidir. Kullanıcı "Kâfir" aradığında, bağlamdan kopuk bir şekilde "tarla süren çiftçi" (ki Kur'an'da bu anlamda da kullanılır) ayetinin gelmesi teknik olarak doğru (aynı kök) ama semantik olarak gürültüdür. Bu durum, salt morfolojik analizin ötesinde, semantik bir katmana ihtiyaç duyulduğunu gösterir.6

## **3\. Python Ekosisteminde Arapça NLP Kütüphanelerinin Kritik Değerlendirmesi**

Kullanıcının "Python tabanlı uygulama" talebi doğrultusunda, mevcut açık kaynak kütüphanelerin Kur'an metni üzerindeki performansları, güçlü ve zayıf yönleriyle aşağıda analiz edilmiştir.

### **3.1 CAMeL Tools: Ağır Siklet Akademik Çözüm**

New York Üniversitesi Abu Dabi (NYUAD) CAMeL Lab tarafından geliştirilen CAMeL Tools, şu an Python ekosistemindeki en gelişmiş Arapça NLP aracıdır.8

* **Mimarisi:** Veritabanı destekli bir morfolojik analizör (CALIMA Star) kullanır. Kelimeleri algoritmik olarak tahmin etmek yerine, milyonlarca kelimelik önceden analiz edilmiş bir veritabanından sorgular.  
* **Kur'an İçin Uygunluğu:** Klasik Arapça veritabanlarını içerdiği için, modern haber metinleri üzerine eğitilmiş araçlara göre Kur'an metninde çok daha yüksek başarı oranına sahiptir.  
* **Python Entegrasyonu:** camel\_morphology modülü, bir kelimenin tüm olası analizlerini (POS tag, lemma, kök) döndürür.  
* **Kısıt:** Sistem kaynaklarını yoğun kullanır ve başlangıç yükleme süresi uzundur. Ancak "kapsamlı" bir çözüm için en güvenilir araçtır. Özellikle kelime anlamlandırma (disambiguation) konusunda, ayet içindeki bağlama göre en doğru kökü seçme yeteneği yüksektir.9

### **3.2 Farasa (Sezgi): Hız ve Segmentasyon**

Katar Hesaplamalı Araştırma Enstitüsü (QCRI) tarafından geliştirilen Farasa, segmentasyon (parçalama) odaklıdır.

* **Mimarisi:** Destek Vektör Makineleri (SVM) kullanarak kelimeleri "ön ek \+ gövde \+ son ek" şeklinde parçalar. Bu, kural tabanlı sistemlerden daha esnek, derin öğrenme modellerinden ise daha hızlıdır.  
* **Kullanım Senaryosu:** Arama motorunun "indeksleme" aşamasında çok etkilidir. Kullanıcının girdiği veya metindeki "ve-le-kad" (وَلَقَدْ) gibi birleşik yapıları w+ l+ qd şeklinde parçalayarak, her bir parçanın ayrı ayrı aranabilmesini sağlar.  
* **Python Durumu:** Orijinali Java olmakla birlikte, farasapy gibi Python sarmalayıcıları (wrappers) mevcuttur ve API üzerinden hızlı erişim sağlar.10

### **3.3 Tashaphyne: Hafif ve Esnek Gövdeleyici**

Tamamen Python ile yazılmış, hafif bir kütüphanedir.

* **Mimarisi:** Sonlu Durum Otomatları (Finite State Automata) kullanarak kelimelerin köklerini bulur.  
* **Avantajı:** Saf Python olması ve dış bağımlılık (Java gibi) gerektirmemesi nedeniyle taşınabilirliği yüksektir. Kodu okumak ve Kur'an'a özel kurallar eklemek (örneğin belirli bir ön eki yoksaymak) kolaydır.  
* **Dezavantajı:** "Kırık çoğullar" (Broken Plurals) konusunda zayıftır. Örneğin "Kitaplar" (*Kutub*) kelimesini, düzenli bir çoğul eki almadığı için köküne (*K-T-B*) indirmekte zorlanabilir. Bu durum, sözlük tabanlı olmayan tüm algoritmik kök bulucuların ortak sorunudur.7

### **3.4 PyArabic: Metin Temizliği ve Normalizasyon**

Arama sisteminin "ön işleme" (preprocessing) aşamasının vazgeçilmezidir.

* **Fonksiyonları:** Hareke temizleme (strip\_tashkeel), uzatmaları atma (strip\_tatweel) ve hemze normalizasyonu (normalize\_hamza) gibi temel işlemleri yüksek hızda yapar. Kur'an metnini "aranabilir" ham metne dönüştürmek için kritik öneme sahiptir.13

### **3.5 NLTK ISRI Stemmer: Kaçınılması Gereken Tuzak**

NLTK kütüphanesi içinde gelen ISRI Stemmer, kök sözlüğü kullanmadan algoritmik olarak çalışır.

* **Risk:** Kur'an metninde, kök harfleriyle ek harflerin birbirine karıştığı durumlarda (örneğin *miskin* kelimesindeki *mim* harfini ön ek sanıp atması gibi) kelimeyi anlamsız bir köke indirgeyerek "aşırı gövdeleme" (over-stemming) hatası yapar. Kutsal metin hassasiyeti için **önerilmez**.15

## **4\. Veri Mühendisliği: Doğru Kaynak ve Veri Hazırlığı**

Yazılım mimarisinin kalitesi, beslendiği verinin kalitesiyle sınırlıdır. Kur'an söz konusu olduğunda, internetten rastgele çekilen metinler (scrape edilmiş veriler) hatalı harekeler içerebileceğinden güvenilmezdir.

### **4.1 Tanzil Projesi: Referans Metin Katmanı**

Tanzil.net, dünya genelinde dijital Kur'an uygulamaları için "altın standart" kabul edilen, titizlikle doğrulanmış metinleri sunar.3

* **XML Yapısı:** quran-simple.xml (basitleştirilmiş imla) ve quran-uthmani.xml (görsel imla) olmak üzere iki ana format sunar.  
* **Mühendislik Stratejisi:** Uygulamanızda **çift katmanlı veri mimarisi** kullanmalısınız.  
  1. **Görüntüleme Katmanı:** Kullanıcıya ayeti gösterirken *Uthmani* metni (quran-uthmani.xml) kullanın. Bu, metnin kutsallığını ve görsel doğruluğunu korur.  
  2. **Arama İndeksi Katmanı:** Arka planda arama yaparken *Simple* veya *Clean* metni (quran-simple-clean.xml) kullanın. Bu metin, arama algoritmalarının takılacağı özel karakterlerden arındırılmıştır.16

### **4.2 Kur'an Arapça Külliyatı (Quranic Arabic Corpus): Morfolojik Katman**

Kais Dukes tarafından geliştirilen bu proje, Kur'an'daki 77.430 kelimenin her biri için manuel olarak doğrulanmış morfolojik etiketler (POS tags), kökler ve lemmalar içerir.4

* **Kritik Çözüm:** "Ek ve kök sorunu"nu algoritmik olarak çözmeye çalışmak yerine, bu veritabanını kullanmak kesin çözümdür. Algoritma (Farasa veya CAMeL) %95 doğrulukla çalışsa bile, kalan %5'lik hata payı Kur'an için kabul edilemez olabilir. Kais Dukes'un verisi, her kelimenin kökünü (örneğin "yemin" kelimesinin kökü *Y-M-N*) dilbilimcilerin onayıyla sabitlemiştir.  
* **Entegrasyon:** Bu veriyi JSON veya SQL formatında indirip, uygulamanızın veritabanına "Lookup Table" (Başvuru Tablosu) olarak eklemelisiniz. Kullanıcı bir kelime aradığında, sistem önce bu tabloya bakarak kelimenin kesin kökünü bulur.18

## **5\. Uygulama Mimarisi: Ek ve Kök Sorununu Çözen Python Pipeline Tasarımı**

Aşağıda, bir "Kutsal Yazılım Mühendisi"nin kurması gereken, hata payını minimize eden arama motoru mimarisi adım adım açıklanmıştır.

### **Adım 1: Veri İçe Aktarma ve Ayrıştırma (Parsing)**

Tanzil XML dosyasını Python'un yerleşik xml.etree.ElementTree kütüphanesi ile parçalayarak, her ayeti bir nesne (object) olarak belleğe alın.

Python

import xml.etree.ElementTree as ET

def load\_quran\_data(xml\_file):  
    tree \= ET.parse(xml\_file)  
    root \= tree.getroot()  
    quran\_index \=  
    for sura in root.findall('sura'):  
        sura\_id \= sura.get('index')  
        for aya in sura.findall('aya'):  
            aya\_id \= aya.get('index')  
            text \= aya.get('text')  
            quran\_index.append({  
                'sura': sura\_id,  
                'aya': aya\_id,  
                'text': text  
            })  
    return quran\_index

Bu temel yapı, ham metni verir. Ancak "ek ve kök" sorunu için bu metin işlenmelidir.19

### **Adım 2: Gelişmiş Normalizasyon ve Temizleme**

Kur'an metnini aranabilir hale getirmek için agresif bir normalizasyon fonksiyonu yazılmalıdır. Bu fonksiyon, kullanıcının klavyesinden girdiği (muhtemelen harekesiz ve modern imlalı) metin ile veritabanındaki (harekeli ve arkaik imlalı) metni eşleştirecek köprüdür.14

**Normalizasyon Kuralları:**

1. **Hareke Temizliği:** Fetha, kesra, damme, sükun, şedde ve tenvinleri silin. (re.sub(r'', '', text))  
2. **Tatweel (Uzatma) Temizliği:** Süsleme amaçlı kullanılan "\_" karakterini (\\u0640) silin.  
3. **Elif Birleştirme:** Tüm elif formlarını (î, â, ǎ, ٱ) tek bir "yalın elif"e (ا) dönüştürün.  
4. **Yâ ve Elif-i Maksura:** "Yâ" (ي) ve "Elif-i Maksura" (ى) harflerini, arama esnekliği için tek bir forma (genellikle ى) indirin veya ikisini de "y" olarak kabul edin.  
5. **Hemze Standardizasyonu:** Kelime başındaki, ortasındaki veya sonundaki hemzeleri (ؤ, ئ) duruma göre "hemze" (ء) veya taşıyıcı harfe dönüştürün.

### **Adım 3: Morfolojik Analiz ve İndeksleme (Search Backend)**

Python uygulamanızın kalbi, arama motorudur. Küçük ölçekli projeler için **Whoosh**, ölçeklenebilir ve profesyonel projeler için **Elasticsearch** kullanılmalıdır. Kapsamlı bir çözüm için Elasticsearch önerilir.22

**Elasticsearch İçin "Kök-Tabanlı" Analizör Konfigürasyonu:**

Standart Arapça analizörü yerine, Kur'an'a özel bir "Custom Analyzer" tanımlanmalıdır.

* **Tokenizer:** Standart (boşluk ve noktalama işaretlerine göre böler).  
* **Filter 1 (Normalization):** Yukarıda belirtilen normalizasyon kurallarını uygular.  
* **Filter 2 (Stopwords):** Kur'an'da çok sık geçen ancak arama değeri düşük olan edatları (örneğin "fî", "min", "alâ") filtreler (isteğe bağlı).  
* **Filter 3 (Synonym Graph \- Kilit Nokta):** "Ek ve kök" sorununu çözmenin en zarif yollarından biri "Eş Anlamlılar Grafiği"dir. Kullanıcı modern bir kelime aradığında, sistem bunu Kur'an'daki karşılığına yönlendirir.  
* **Filter 4 (Stemming):** Burada "Light Stemming" (Hafif Gövdeleme) kullanılmalıdır. Algoritmik kök bulucu yerine, kelimenin sadece bariz eklerini (çoğul ekleri, belirlilik takısı *El-*) atan bir yaklaşım daha güvenlidir.23

### **Adım 4: Kök Çıkarma ve Sözlük Entegrasyonu**

Kullanıcı "Yardım" kavramını aradığında, sistem hem "nasr" (yardım), hem "yansuru" (yardım eder), hem de "nasir" (yardımcı) kelimelerini bulmalıdır. Bunu yapmak için, her ayetin indeksine "Kökler Listesi" alanı eklenmelidir.

**Veri Yapısı Tasarımı (Örnek Belge):**

JSON

{  
  "sura": 110,  
  "aya": 1,  
  "text\_display": "إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ",  
  "text\_search": "idha jaa nasr allah waalfath",  
  "roots": \["j-y-", "n-s-r", "l-l-h", "f-t-h"\],  
  "lemmas": \["jaa", "nasr", "Allah", "fath"\]  
}

Bu yapı sayesinde, kullanıcı "nasr" kökünü arattığında, sistem metin içinde eşleştirme yapmaya çalışmaz; doğrudan roots dizisinde "n-s-r" kökünü barındıran ayetleri getirir. Bu yöntem, "ek sorunu"nu tamamen ortadan kaldırır çünkü arama, eklerden arındırılmış saf veri (kök) üzerinde yapılır.25

## **6\. Derin Morfolojik Analiz: Eklerin Ötesine Geçmek**

Kullanıcının "kapsamlı morfolojik inceleme" talebi, basit bir kök bulmanın ötesine geçmeyi gerektirir. Kur'an Arapçası'nda bir kelimenin morfolojik analizi, onun gramer yapısını (i'rab) ve anlamını belirler.

### **6.1 POS Tagging (Sözcük Türü İşaretleme)**

Kur'an'da bir kelimenin isim mi, fiil mi yoksa harf (edat) mi olduğu, arama sonuçlarını filtrelemek için hayati önem taşır. Kais Dukes'un veritabanı, her kelimeyi detaylı etiketlerle (örneğin V \- Fiil, N \- İsim, PN \- Özel İsim) işaretler.

* **Uygulama:** Python uygulamanızda arama filtresi olarak "Sadece Fiilleri Getir" seçeneği sunabilirsiniz. Örneğin, "Secde" kelimesini arayan kullanıcı, sadece "secde etmek" fiillerini görmek isteyebilir (isim olan "mescid"leri değil). Bu, veritabanındaki POS etiketleri üzerinden SQL sorgusu ile (WHERE pos\_tag LIKE 'V%') kolayca yapılır.4

### **6.2 Lemmatizasyonun Önemi**

Kök her zaman yeterli değildir. "K-T-B" kökü hem "yazmak" hem de "kitap" kelimelerini üretir. Kullanıcı "Kitap" arıyorsa, kök araması çok geniş sonuç getirir. Burada devreye "Lemma" (Sözlük Maddesi) girer.

* **Çözüm:** Uygulamanızda **Al-Fanous** projesinin API mantığını örnek alabilirsiniz. Al-Fanous, her kelimeyi hem köküne hem de lemmasına göre indeksler. Böylece kullanıcı "Kitap" aradığında, sistem "Kütüb" (Kitaplar) kelimesini bulur (çünkü lemması Kitap'tır) ama "Yektübü" (Yazıyor) kelimesini getirmez (çünkü lemması Yaz'dır). Bu ayrım, morfolojik aramanın zirvesidir.28

## **7\. Semantik Arama ve Yapay Zeka Entegrasyonu**

"Kutsal yazılım mühendisi" vizyonu, teknolojinin sınırlarını zorlamayı gerektirir. Kelime eşleştirmenin ötesinde, "anlam" araması için modern Yapay Zeka teknikleri kullanılmalıdır.

### **7.1 Vektör Gömmeleri (Embeddings) ve AraBERT**

Kullanıcı "miras hukuku" diye arama yaptığında, ayetlerde "miras" kelimesi geçmeyebilir; bunun yerine "nısıf" (yarısı), "sülüs" (üçte biri) gibi paylar veya "velede" (çocuk) kelimeleri geçer. Klasik arama burada çaresizdir.

* **Çözüm:** **AraBERT** veya **QARiB** (Kur'an ve Hadis üzerine eğitilmiş BERT modelleri) kullanılarak, her ayet 768 boyutlu bir vektöre dönüştürülür. Kullanıcının sorgusu da vektöre çevrilir ve "Kosinüs Benzerliği" (Cosine Similarity) ile en yakın ayetler bulunur. Bu yöntem, kelime benzerliğini değil, konu/bağlam benzerliğini yakalar.30  
* **Python Uygulaması:** sentence-transformers kütüphanesi ile önceden eğitilmiş bir Arapça model (örneğin aubmindlab/bert-base-arabertv02) yüklenir. Tüm ayetlerin vektörleri önceden hesaplanıp FAISS (Facebook AI Similarity Search) gibi bir vektör veritabanında saklanır. Arama milisaniyeler sürer.

### **7.2 Ontoloji Tabanlı Arama (Bilgi Grafiği)**

Kök ve ek sorununu aşmanın bir diğer yolu, kelimeleri kavramsal bir hiyerarşiye oturtmaktır. Kur'an Ontolojisi (Quranic Ontology), kavramları birbirine bağlar.

* **Örnek:** "Su" kavramı \-\> Alt kavramlar: "Yağmur", "Nehir", "Deniz", "Pınar".  
* **Uygulama:** Python'da rdflib kütüphanesi ile Kur'an ontolojisi (RDF/OWL formatında) yüklenir. Kullanıcı "Su" aradığında, sistem ontolojiden tüm alt kavramları çeker ve aramayı otomatik olarak genişletir ("Query Expansion"). Böylece kullanıcı "Yağmur" kelimesini yazmasa bile, su ile ilgili ayetlere ulaşır.32

## **8\. Tablo: Kur'an Arama Yöntemlerinin Karşılaştırmalı Analizi**

Aşağıdaki tablo, bir araştırmacı olarak hangi yöntemi ne zaman kullanmanız gerektiğini özetler:

| Yöntem | Teknoloji | Avantajı | Dezavantajı | Kapsam |
| :---- | :---- | :---- | :---- | :---- |
| **Tam Metin Arama (Regex)** | Python re | Basit, hızlı, kurulum gerektirmez. | İmla farklarını kaçırır, ekleri yönetemez. | Basit kelime eşleşmeleri. |
| **Morfolojik Kök Arama** | Kais Dukes DB / CAMeL Tools | Kesin sonuç, tüm türevleri bulur. | Anlamsal ayrımı yapamaz (Yazmak vs Kitap). | Kök tabanlı akademik araştırmalar. |
| **Lemma Tabanlı Arama** | Al-Fanous / Farasa | Dilbilgisel doğruluk, kırık çoğulları yönetir. | Veri hazırlığı zordur. | Kavramsal kelime aramaları. |
| **Semantik (Vektör) Arama** | AraBERT / FAISS | Kelime geçmese bile konuyu bulur. | "Kara kutu"dur, neden o sonucu getirdiği bazen belirsizdir. | Konu ve tema araştırmaları. |
| **Ontoloji Araması** | RDF / SPARQL | Kavramlar arası ilişkileri kullanır. | Sadece ontolojide tanımlı kavramlarla sınırlıdır. | Tematik sınıflandırma. |

## **9\. Sonuç ve Gelecek Vizyonu**

Kur'an-ı Kerim için Python tabanlı bir arama sistemi geliştirmek, "string" işlemekten çok daha öte, bir veri arkeolojisi çalışmasıdır. "Ek ve kök sorunu", tek bir sihirli algoritma ile değil, **hibrit bir mimari** ile çözülür:

1. **Veri Katmanında:** Tanzil.net'in temiz metinleri ve Kais Dukes'un morfolojik veritabanı "Hakikat Kaynağı" (Source of Truth) olarak kullanılmalıdır.  
2. **İşlem Katmanında:** Farasa veya CAMeL Tools ile metinler segmente edilmeli, ancak son karar daima insan onaylı veritabanına bırakılmalıdır.  
3. **Arama Katmanında:** Elasticsearch üzerinde özel analizörler ve eş anlamlılar grafiği kurulmalı, buna ek olarak AraBERT destekli semantik arama modülü sisteme entegre edilmelidir.

Bir "Kutsal Yazılım Mühendisi" olarak nihai hedef, kullanıcının niyetini anlayan, metnin kutsal yapısını bozmadan en derin morfolojik katmanlarına inebilen ve "Nasr" (Yardım) arayan birine, sadece harfleri değil, ilahi yardım vaadinin geçtiği tüm bağlamları sunabilen bir dijital rehber inşa etmektir. Bu, teknolojinin teolojiyle en zarif dansıdır.

#### **Works cited**

1. Can you understand the Quran with MSA (The Fusha)? \- AlBaher Arabic Language Center, accessed February 1, 2026, [https://albahertrainingcenter.com/how-much-can-modern-standard-arabic-help-you-understand-the-quran/](https://albahertrainingcenter.com/how-much-can-modern-standard-arabic-help-you-understand-the-quran/)  
2. How different is Quranic Arabic from modern Arabic language? Which one should I learn?, accessed February 1, 2026, [https://www.quora.com/How-different-is-Quranic-Arabic-from-modern-Arabic-language-Which-one-should-I-learn](https://www.quora.com/How-different-is-Quranic-Arabic-from-modern-Arabic-language-Which-one-should-I-learn)  
3. Tanzil Project \- Tanzil Documents, accessed February 1, 2026, [https://tanzil.net/docs/tanzil\_project](https://tanzil.net/docs/tanzil_project)  
4. Morphological Annotation of Quranic Arabic \- ACL Anthology, accessed February 1, 2026, [https://aclanthology.org/L10-1190/](https://aclanthology.org/L10-1190/)  
5. Stemming the Qur'an \- ACL Anthology, accessed February 1, 2026, [https://aclanthology.org/W04-1616.pdf](https://aclanthology.org/W04-1616.pdf)  
6. New Arabic Root Extraction Algorithm \- The Science and Information (SAI) Organization, accessed February 1, 2026, [https://thesai.org/Downloads/Volume14No5/Paper\_43-New\_Arabic\_Root\_Extraction\_Algorithm.pdf](https://thesai.org/Downloads/Volume14No5/Paper_43-New_Arabic_Root_Extraction_Algorithm.pdf)  
7. Tashaphyne: A Python package for Arabic Light Stemming \- Open Journals, accessed February 1, 2026, [https://www.theoj.org/joss-papers/joss.06063/10.21105.joss.06063.pdf](https://www.theoj.org/joss-papers/joss.06063/10.21105.joss.06063.pdf)  
8. CAMeL\_Tools.ipynb \- Colab \- Google, accessed February 1, 2026, [https://colab.research.google.com/github/ARBML/adawat/blob/main/notebooks/CAMeL\_Tools.ipynb](https://colab.research.google.com/github/ARBML/adawat/blob/main/notebooks/CAMeL_Tools.ipynb)  
9. camel\_morphology — camel\_tools 1.5.2 documentation, accessed February 1, 2026, [https://camel-tools.readthedocs.io/en/latest/cli/camel\_morphology.html](https://camel-tools.readthedocs.io/en/latest/cli/camel_morphology.html)  
10. Farasa python package project, accessed February 1, 2026, [https://www.hbku.edu.qa/sites/default/files/alt-farasa\_python\_package.pdf](https://www.hbku.edu.qa/sites/default/files/alt-farasa_python_package.pdf)  
11. MagedSaeed/farasapy: A Python implementation of Farasa toolkit \- GitHub, accessed February 1, 2026, [https://github.com/MagedSaeed/farasapy](https://github.com/MagedSaeed/farasapy)  
12. (PDF) Tashaphyne: A Python package for Arabic Light Stemming \- ResearchGate, accessed February 1, 2026, [https://www.researchgate.net/publication/377777060\_Tashaphyne\_A\_Python\_package\_for\_Arabic\_Light\_Stemming](https://www.researchgate.net/publication/377777060_Tashaphyne_A_Python_package_for_Arabic_Light_Stemming)  
13. PyArabic: A Python package for Arabic text \- Semantic Scholar, accessed February 1, 2026, [https://pdfs.semanticscholar.org/5e7a/96362421fe53cca22ce06ccf95c4c61622f9.pdf](https://pdfs.semanticscholar.org/5e7a/96362421fe53cca22ce06ccf95c4c61622f9.pdf)  
14. pyarabic/pyarabic/normalize.py at master · linuxscout/pyarabic \- GitHub, accessed February 1, 2026, [https://github.com/linuxscout/pyarabic/blob/master/pyarabic/normalize.py](https://github.com/linuxscout/pyarabic/blob/master/pyarabic/normalize.py)  
15. nltk.stem.isri module, accessed February 1, 2026, [https://www.nltk.org/api/nltk.stem.isri.html](https://www.nltk.org/api/nltk.stem.isri.html)  
16. Tanzil Documents, accessed February 1, 2026, [https://tanzil.net/docs/](https://tanzil.net/docs/)  
17. (PDF) Reusability of Quranic document using XML \- ResearchGate, accessed February 1, 2026, [https://www.researchgate.net/publication/366548557\_Reusability\_of\_Quranic\_document\_using\_XML](https://www.researchgate.net/publication/366548557_Reusability_of_Quranic_document_using_XML)  
18. The Quranic Arabic Corpus \- Word by Word Grammar, Syntax and Morphology of the Holy Quran, accessed February 1, 2026, [https://corpus.quran.com/](https://corpus.quran.com/)  
19. xml.etree.ElementTree — The ElementTree XML API — Python 3.14.2 documentation, accessed February 1, 2026, [https://docs.python.org/3/library/xml.etree.elementtree.html](https://docs.python.org/3/library/xml.etree.elementtree.html)  
20. How to Parse XML in Python Without Using External Libraries \- freeCodeCamp, accessed February 1, 2026, [https://www.freecodecamp.org/news/how-to-parse-xml-in-python-without-using-external-libraries/](https://www.freecodecamp.org/news/how-to-parse-xml-in-python-without-using-external-libraries/)  
21. Python Functions for Arabic \- al-Raqmiyyāt, accessed February 1, 2026, [https://maximromanov.github.io/2013/01-02.html](https://maximromanov.github.io/2013/01-02.html)  
22. msarhan/elasticsearch-analysis-arabic-plugin \- GitHub, accessed February 1, 2026, [https://github.com/msarhan/elasticsearch-analysis-arabic-plugin](https://github.com/msarhan/elasticsearch-analysis-arabic-plugin)  
23. How to Implement Synonym Search in Elasticsearch, accessed February 1, 2026, [https://oneuptime.com/blog/post/2026-01-21-elasticsearch-synonym-search/view](https://oneuptime.com/blog/post/2026-01-21-elasticsearch-synonym-search/view)  
24. Synonym graph token filter | Reference \- Elastic, accessed February 1, 2026, [https://www.elastic.co/docs/reference/text-analysis/analysis-synonym-graph-tokenfilter](https://www.elastic.co/docs/reference/text-analysis/analysis-synonym-graph-tokenfilter)  
25. list of Quranic roots and their derivatives in JSON format \- GitHub, accessed February 1, 2026, [https://github.com/AbstractThinker0/quran-roots](https://github.com/AbstractThinker0/quran-roots)  
26. Root-based online Arabic dictionary : r/learn\_arabic \- Reddit, accessed February 1, 2026, [https://www.reddit.com/r/learn\_arabic/comments/6fayu7/rootbased\_online\_arabic\_dictionary/](https://www.reddit.com/r/learn_arabic/comments/6fayu7/rootbased_online_arabic_dictionary/)  
27. \\quran: Morphologically Annotated Quranic Corpus \- arXiv, accessed February 1, 2026, [https://arxiv.org/html/2506.18148v1](https://arxiv.org/html/2506.18148v1)  
28. Alfanous API — Alfanous Quranic Search Engine 0.7.00 documentation, accessed February 1, 2026, [https://alfanous.readthedocs.io/en/latest/src/alfanous/README/](https://alfanous.readthedocs.io/en/latest/src/alfanous/README/)  
29. Alfanous: Quran Ayah Search, accessed February 1, 2026, [https://www.alfanous.org/en/aya/](https://www.alfanous.org/en/aya/)  
30. Embedding Search for Quranic Texts based on Large Language Models \- iajit, accessed February 1, 2026, [https://iajit.org/upload/files/Embedding-Search-for-Quranic-Texts-based-on-Large-Language-Models.pdf](https://iajit.org/upload/files/Embedding-Search-for-Quranic-Texts-based-on-Large-Language-Models.pdf)  
31. Semantic search engine for the holy Quran \- Theseus, accessed February 1, 2026, [https://www.theseus.fi/bitstream/handle/10024/855111/Ahmed\_Omar.pdf?sequence=2\&isAllowed=y](https://www.theseus.fi/bitstream/handle/10024/855111/Ahmed_Omar.pdf?sequence=2&isAllowed=y)  
32. Automatic Mapping of Quranic Ontologies Using RML and Cellfie Plugin \- White Rose Research Online, accessed February 1, 2026, [https://eprints.whiterose.ac.uk/id/eprint/186011/7/Automatic\_Mapping\_of\_Quranic\_Ontologies\_Using\_RML\_and\_Cellfie\_Plugin.pdf](https://eprints.whiterose.ac.uk/id/eprint/186011/7/Automatic_Mapping_of_Quranic_Ontologies_Using_RML_and_Cellfie_Plugin.pdf)  
33. Ontology of Quranic Concepts, accessed February 1, 2026, [https://corpus.quran.com/ontology.jsp](https://corpus.quran.com/ontology.jsp)
