# **Kuran-ı Kerim Morfolojik Arama Motoru Mimarisi: PostgreSQL ve Python Tabanlı Derinlemesine Teknik Analiz ve Uygulama Raporu**

## **1\. Yönetici Özeti ve Mimari Vizyon**

Kutsal metinlerin dijital ortamda aranabilir hale getirilmesi, standart bilgi erişim (Information Retrieval \- IR) sistemlerinin ötesinde, metnin dilbilimsel kutsiyetine ve yapısal karmaşıklığına saygı duyan özelleşmiş mühendislik çözümleri gerektirmektedir. Özellikle Kuran-ı Kerim gibi Klasik Arapça (*Fusha*) ile nazil olmuş bir metin üzerinde "anahtar kelime" veya "tek kelime" araması yapmak, modern arama motorlarının kullandığı basit metin eşleştirme algoritmalarıyla çözülemeyecek kadar çok katmanlı bir problemdir. Kullanıcının talep ettiği, anlamsal (semantik) vektör aramalarını dışarıda bırakan ancak Arapçanın zengin morfolojik yapısını (türetimsel sistemini) kapsayan bir arama motoru geliştirmek, **Deterministik Dilbilimsel İndeksleme** stratejisini zorunlu kılmaktadır.

Bu rapor, PostgreSQL veritabanı yönetim sisteminin gelişmiş metin arama yetenekleri ile Python programlama dilinin doğal dil işleme (NLP) kütüphanelerini entegre eden hibrit bir mimari önermektedir. Raporun temel tezi; Kuran metninde etkili bir anahtar kelime aramasının, kelimenin görünen yüzeyi (*surface form*) üzerinden değil, o kelimenin morfolojik kökü (*root*) ve gövdesi (*lemma*) üzerinden yapılması gerektiğidir. Bu yaklaşım, kullanıcının tek bir kelime (örneğin "kitap") aratarak, aynı kökten türeyen tüm kavramsal varyasyonlara (yazdı, yazılan, kâtip, mektup vb.) ulaşmasını sağlar.

Raporda, veri kaynağı olarak **Quranic Arabic Corpus**'un morfolojik olarak etiketlenmiş verilerinin kullanılması, bu verilerin Python ETL (Extract-Transform-Load) süreçleriyle işlenerek ilişkisel bir PostgreSQL şemasına aktarılması ve veritabanı seviyesinde **GIN (Generalized Inverted Index)** ve **B-Tree** indeksleme stratejileriyle sorgu performansının optimize edilmesi süreçleri en ince teknik detayına kadar incelenecektir. Semantik aramanın dışlanması, sistemin kesinlik (*precision*) ve geri çağırma (*recall*) oranlarının tamamen kural tabanlı morfolojik analizlere dayandırılmasını gerektirir, bu da veri kalitesinin ve veritabanı konfigürasyonunun önemini kritik seviyeye taşır.

## ---

**2\. Kuran Arapçası ve Bilgi Erişim Zorlukları: Dilbilimsel Bağlam**

Kuran-ı Kerim üzerinde yapılacak bir arama motoru tasarımının ilk adımı, verinin doğasını, yani Klasik Arapçanın morfolojik yapısını derinlemesine anlamaktır. Modern İngilizce veya Türkçe arama motorları genellikle "ek atma" (*stemming*) yöntemiyle kelimenin köküne iner. Ancak Arapça, "kök ve vezin" (*root and pattern*) sistemine dayalı, bükümlü (*inflectional*) ve türetimsel (*derivational*) bir dildir. Bu durum, basit "LIKE" sorgularının veya standart metin işleme algoritmalarının başarısız olmasına neden olur.

### **2.1 Morfolojik Yoğunluk ve Kök Sistemi**

Arapça kelimeler, genellikle üç harfli (sülasi) veya dört harfli (rubai) sessiz harf köklerinden türetilir. Bir kök harf dizisi (örneğin **K-T-B**), belirli sesli harf kalıpları ve eklerle birleşerek onlarca farklı kelimeye dönüşebilir.

* **Kök:** K-T-B (Yazma eylemi ile ilgili soyut kök)  
* **Türevler:**  
  * *Kataba* (Yazdı \- Fiil)  
  * *Yaktubu* (Yazar \- Fiil)  
  * *Kitab* (Kitap \- İsim)  
  * *Kutiba* (Yazıldı/Farz kılındı \- Edilgen Fiil)  
  * *Maktab* (Ofis/Masa \- İsim)

Kullanıcının "uygun bir kaynak bulma ve anahtar kelime araması yapma" talebi 1, bu morfolojik zenginliğin yönetilmesini gerektirir. Eğer veritabanında sadece "Kitab" kelimesi ham metin olarak saklanırsa, kullanıcı "Yazmak" (*Kataba*) fiilini arattığında, veritabanı bu iki kelime arasındaki anlamsal ve kökensel bağı kuramayacak ve sonuç döndürmeyecektir. Bu durum, "morfolojik yapısı gereği zor olmakta" şeklindeki kullanıcı tespitini doğrular niteliktedir.

### **2.2 Yazım Kuralları: Resm-i Osmani ve İmla Sorunsalı**

Kuran'ın yazımı (*Resm-i Osmani*), modern standart Arapça imlasından (*İmla*) farklılıklar gösterir. Bu durum, arama motoru için ciddi bir normalizasyon problemi doğurur.

* **Örnek:** "Zekât" kelimesi modern Arapçada "زكاة" şeklinde yazılırken, Kuran imlasında genellikle "Waw" harfinin üzerine küçük bir Elif konularak "زكـٰوة" şeklinde yazılır.  
* **Arama Problemi:** Kullanıcı klavyesinde modern imla ile "Zekat" yazacaktır. Veritabanında ise orijinal Kuran metni korunmalıdır. Arama motoru, kullanıcının modern girdisini, metnin arkaik formuyla eşleştirebilecek bir normalizasyon katmanına sahip olmalıdır.2

### **2.3 Ekler ve Bitişik Zamirler (Affixation)**

Kuran Arapçasında kelimeler genellikle tek başına durmaz; edatlar, bağlaçlar ve zamirler kelimenin bünyesine entegre olur.

* *Falyaktub* (O halde yazsın): Burada "Fa" (o halde), "Li" (emir kipi için), "Yaktub" (yazsın) bileşenleri tek bir kelime gibi yazılır.  
* Basit bir kelime aramasında, kelimenin başındaki "Fa" veya sonundaki zamir ekleri, kelimenin kök formunun bulunmasını engeller. Bu nedenle sistem, "ön ek" (*prefix*), "kök" (*stem*) ve "son ek" (*suffix*) ayrıştırmasını yapabilmelidir.

## ---

**3\. Veri Kaynağı Değerlendirmesi ve Seçimi**

Kuran arama motorunun başarısı, doğrudan kullanılan verinin kalitesine ve yapısına bağlıdır. Kullanıcının "uygun bir kuranı kerim kaynağı bulmak" talebi doğrultusunda, mevcut açık kaynaklı verisetleri detaylı bir analize tabi tutulmuştur.

### **3.1 Aday Veri Kaynaklarının Karşılaştırmalı Analizi**

#### **3.1.1 risan/quran-json ve AbdullahGhanem/quran-database**

Bu kaynaklar, geliştiriciler arasında popüler olan ve Kuran metnini JSON veya SQL formatında sunan projelerdir.4

* **Veri Yapısı:** Genellikle Sure ID, Ayet ID ve Ayet Metni sütunlarından oluşur. Çeviri metinlerini de içerirler.4  
* **Eksiklik:** Bu kaynaklar genellikle **düz metin** (*plain text*) sunarlar. Kelime-kelime morfolojik analiz, kök bilgisi veya gramer etiketleri (POS tags) içermezler. Kullanıcının talep ettiği "morfolojik yapıya dayalı arama" için bu veritabanları ham haliyle yetersizdir; çünkü kök-kelime ilişkisini kuracak veri katmanından yoksundurlar.  
* **Kullanım Alanı:** Sadece ayet metninin son kullanıcıya gösterilmesi (frontend display) için uygundur.

#### **3.1.2 Quranic Arabic Corpus (Morfoloji v0.4)**

Kais Dukes tarafından yönetilen bu proje, Kuran hesaplamalı dilbilimi alanında "altın standart" olarak kabul edilir.6

* **Veri Derinliği:** Kuran'daki 77.430 kelimenin her biri için manuel olarak doğrulanmış morfolojik etiketler, lemnalar (sözlük halleri) ve kökler (radikaller) içerir.  
* **Güvenilirlik:** Otomatik algoritmaların aksine, insan uzmanlar tarafından doğrulandığı için hata oranı minimaldir. Kuran gibi hassas bir metinde algoritmik hatalara (yanlış kök tespiti) tahammül edilemez.  
* **Format:** Veri genellikle özel bir metin formatında sunulur ve işlenmesi (parsing) gerekir.

#### **3.1.3 mustafa0x/quran-morphology (Önerilen Kaynak)**

Bu depo, orijinal Quranic Arabic Corpus'un bir çatalı (fork) olup, veri mühendisliği açısından kritik iyileştirmeler içermektedir.8

* **İyileştirmeler:** Orijinal korpustaki Buckwalter transliterasyonu (Latin harfleriyle Arapça kodlama) yerine doğrudan Arapça harfler kullanılmıştır. Ayrıca, "yevmeizin" (o gün) gibi birleşik kelimelerin kökleri ayrıştırılmış ve bazı hatalı kök atamaları düzeltilmiştir.8  
* **Dosya Formatı:** quran-morphology.txt dosyası, her kelimeyi, o kelimenin kökünü, gövdesini ve dilbilgisi özelliklerini satır satır listeler.  
* **Seçim Gerekçesi:** Kullanıcının morfolojik arama ihtiyacını karşılamak için en hazır, en temiz ve en zengin veri kaynağı budur.

Bu veri kaynağı kullanılırken, depo içerisinde yer alan varsayılan **Python düzeltme betiklerinin (fix scripts) olduğu gibi çalıştırılmaması hayati önem taşımaktadır.**

Söz konusu betikler, standart arama motorlarında "bulunabilirliği" artırmak amacıyla **agresif bir normalizasyon** uygulamaktadır. Bu işlem sırasında:

1. **Dişil Çoğul Zamirler (Feminine Plural):** Örneğin *"El-Lai"* (ki o kadınlar) zamiri, eril tekil olan *"El-Lezi"* (ki o erkek) formuna dönüştürülmektedir.  
2. **İkililer (Dual Forms):** *"Hâzâni"* (o ikisi) gibi tesniye formları, tekil *"Hâzâ"* formuna indirgenmektedir.  
3. **İşaret İsimleri:** *"Hâzihi"* (bu \- dişil) işaret sıfatı, *"Hâzâ"* (bu \- eril) ile birleştirilmektedir.

Projemizin amacı "metnin dilbilimsel kutsiyetine saygı duyan" bir yapı kurmak olduğu için, bu **"cinsiyetsizleştirme" (gender neutralization)** işlemi reddedilmiştir. Ham verinin işlenmesi sırasında bu spesifik kod blokları devre dışı bırakılarak, veritabanına Kuran'daki gramatikal cinsiyet ve sayı detaylarının **kayıpsız** (lossless) aktarılması sağlanacaktır

### **3.2 Seçilen Veri Yapısı ve Entegrasyon Stratejisi**

Proje için `mustafa0x/quran-morphology` veri seti temel alınacaktır. Ancak entegrasyon stratejisi, **"Seçici ETL" (Selective Extract-Transform-Load)** prensibine dayanacaktır.

Bu strateji, verinin işlenmesi sırasında iki katmanlı bir filtreleme uygular:

1. **Zorunlu Ortografik Düzeltmeler (Uygulanacak):** Buckwalter kodlarının Arapça harflere dönüştürülmesi ve Kuran imlası (Resm-i Osmani) ile modern imla arasındaki *yazım* farklarının giderilmesi işlemleri uygulanacaktır. Bu, arama motorunun modern klavyelerle uyumlu çalışması için zorunludur.  
2. **Morfolojik İndirgemeler (Engellenecek):** Kelimenin kök anlamını değiştirmeyen ancak gramatikal kimliğini (cinsiyet, sayı, şahıs) belirleyen özelliklerin silinmesi engellenecektir.

**Veri Hassasiyeti Prensibi:** Sistem, kullanıcının *"Müminler"* (çoğul/eril) araması ile *"Mümin"* (tekil) aramasını kök seviyesinde (E-M-N) eşleştirebilmeli; ancak kullanıcı spesifik olarak *"Müminat"* (kadın müminler) araması yaptığında, sistem bunu *"Mümin"* (erkek) sonuçlarıyla karıştırmadan filtreleyebilecek detayda veriye sahip olmalıdır.

Bu nedenle, Python ETL sürecinde `singularize_mp` (çoğulları tekilleştirme) ve `split_dem` (işaret isimlerini parçalama) fonksiyonlarının cinsiyet silen özellikleri devre dışı bırakılarak, veritabanındaki `words` tablosuna (bkz. 4.1.3) **zenginleştirilmiş morfolojik etiketler** (örn. `PRON|FP` \- Pronoun Feminine Plural) olduğu gibi aktarılacaktır. Bu yaklaşım, sistemin sadece bir "kelime bulucu" değil, aynı zamanda bir "gramer analiz aracı" olarak çalışmasını sağlar.

## ---

**4\. PostgreSQL Veritabanı Mimarisi ve Şema Tasarımı**

Kullanıcının tercih ettiği PostgreSQL, metin arama ve yapısal veri yönetimi konusundaki üstünlüğü nedeniyle bu proje için ideal bir seçimdir. Ancak standart bir şema tasarımı, morfolojik arama için yeterli olmayacaktır. Veritabanı, Kuran'ın hiyerarşik yapısını (Sure \-\> Ayet \-\> Kelime \-\> Kök) yansıtacak şekilde normalize edilmelidir.

### **4.1 Varlık-İlişki (Entity-Relationship) Modeli**

Veritabanı şeması, verinin tekrarını önlemek ve sorgu performansını artırmak amacıyla 3\. Normal Form (3NF) prensiplerine uygun olarak tasarlanmalıdır.

#### **4.1.1 Tablo: surahs (Sureler)**

Kuran'ın 114 suresinin meta verilerini saklar.

| Sütun Adı | Veri Tipi | Açıklama |
| :---- | :---- | :---- |
| id | INTEGER (PK) | 1-114 arası sure numarası. |
| name\_arabic | VARCHAR(100) | Surenin Arapça adı (örn. الفاتحة). |
| name\_transliterated | VARCHAR(100) | Latin harfleriyle okunuşu (örn. Al-Fatiha). |
| revelation\_type | VARCHAR(20) | Mekki veya Medeni. |

#### **4.1.2 Tablo: ayahs (Ayetler)**

Her bir ayetin tam metnini ve arama vektörlerini saklar.

| Sütun Adı | Veri Tipi | Açıklama |
| :---- | :---- | :---- |
| id | SERIAL (PK) | Benzersiz kayıt numarası. |
| surah\_id | INTEGER (FK) | surahs tablosuna referans. |
| ayah\_number | INTEGER | Sure içindeki ayet numarası. |
| content\_uthmani | TEXT | Kuran hattına uygun, harekeli orijinal metin (Görüntüleme için). |
| content\_clean | TEXT | Harekesiz, normalize edilmiş metin (Basit metin araması için). |
| search\_vector | TSVECTOR | PostgreSQL Full Text Search için önceden hesaplanmış lexeme vektörü. |

#### **4.1.3 Tablo: words (Morfolojik Kelime Birimleri)**

Sistemin beyni bu tablodur. Kuran'daki her bir kelime, tek bir satır olarak bu tabloda saklanır. Anahtar kelime araması burada gerçekleşecektir.

| Sütun Adı | Veri Tipi | İndeks Tipi | Açıklama |
| :---- | :---- | :---- | :---- |
| id | SERIAL (PK) | B-Tree | Benzersiz kelime ID'si. |
| ayah\_id | INTEGER (FK) | B-Tree | ayahs tablosuna referans. |
| position | INTEGER | \- | Kelimenin ayet içindeki sırası. |
| token | VARCHAR(100) | \- | Kelimenin orijinal hali (örn. *yaktubûne*). |
| token\_clean | VARCHAR(100) | GIN (Trigram) | Kelimenin harekesiz hali (örn. *yktbwn*). |
| root | VARCHAR(50) | **B-Tree** | **Kelimenin kökü (örn. *ktb*).** |
| lemma | VARCHAR(50) | B-Tree | Kelimenin sözlük hali (örn. *kataba*). |
| pos\_tag | VARCHAR(20) | \- | Kelime türü (İsim, Fiil, Edat vb.). |

**Tasarım İçgörüsü:** root sütununun ayrı bir sütun olarak tutulması ve indekslenmesi, morfolojik arama problemini, veritabanı açısından çok hızlı bir "tam eşleşme" (*exact match*) sorgusuna indirger. Kullanıcı ne kadar karmaşık bir kelime girerse girsin, Python tarafında kökü bulup bu sütunda basit bir sorgu çalıştıracağız.

### **4.2 İndeksleme Stratejileri ve Performans Optimizasyonu**

PostgreSQL'de metin arama performansı, doğru indeks tipinin seçilmesine bağlıdır.9

#### **4.2.1 B-Tree İndeksleri (Kök Aramaları İçin)**

root sütunu üzerinde standart **B-Tree** indeksi kullanılmalıdır.11

* **Neden?** B-Tree indeksleri, eşitlik (=) operatörleri için en hızlı yöntemdir. Bir kök (örneğin "ktb") arandığında, veritabanı ağaç yapısını gezerek milisaniyeler içinde ilgili satırlara ulaşır. Morfolojik aramada, kök bilindiği için "fuzzy" (bulanık) aramaya gerek yoktur, bu da B-Tree'yi ideal kılar.

#### **4.2.2 GIN İndeksleri (Metin İçinde Arama İçin)**

Eğer kullanıcı kök tabanlı değil de, metin içinde geçen bir ifadeyi aramak isterse (örneğin "Rabbena"), ayahs.search\_vector üzerinde **GIN (Generalized Inverted Index)** kullanılmalıdır.9

* **Mekanizma:** GIN indeksi, her bir kelimeyi (lexeme) o kelimenin geçtiği satır numaralarıyla eşleştiren bir "tersine çevrilmiş liste" (*inverted list*) tutar. Kuran gibi okuma ağırlıklı (read-heavy) ve güncelleme gerektirmeyen (static) veri setlerinde GIN mükemmel performans sunar.

#### **4.2.3 RUM İndeksleri (Opsiyonel Gelişmiş Sıralama)**

Eğer sistemde "sıralama" (*ranking*) veya kelime yakınlığı (*phrase search*) kritikse, standart GIN yerine **RUM** eklentisi düşünülebilir.13

* **Fark:** GIN sadece kelimenin varlığını tutarken, RUM kelimenin pozisyon bilgisini de tutar. Bu, "Allah" ve "Rahim" kelimelerinin yan yana geçtiği ayetleri bulmak için (\<-\> operatörü) çok daha hızlıdır. Kullanıcı sadece "tek kelime" araması talep ettiği için GIN yeterlidir, ancak geleceğe dönük olarak RUM eklentisinin kurulması önerilir.

## ---

**5\. PostgreSQL Metin Arama Konfigürasyonu (Text Search Configuration)**

PostgreSQL'in varsayılan metin arama ayarları İngilizce veya genel dillere göredir ve Arapça için, özellikle Kuran Arapçası için yetersizdir. Özel bir konfigürasyon oluşturulmalıdır.

### **5.1 Unaccent Eklentisi ve Harekelerin Temizlenmesi**

Arapça metinlerdeki harekeler (Fetha, Kesre, Damme, Şedde vb.) arama sırasında gürültü oluşturur. PostgreSQL'in unaccent eklentisi, harfleri temizlemek için kullanılır, ancak varsayılan olarak sadece Latin karakterlerini destekler.15

**Özel Arapça Sözlüğü Oluşturma:** Kuran araması için özel bir arabic.rules dosyası oluşturulmalıdır. Bu dosya, tüm Arapça diakritik işaretlerini (Unicode aralığı U+064B ile U+0652 arası) boş karakterle eşleştirerek silmelidir.16

Dosya konumu (Linux sistemlerde): /usr/share/postgresql/VERSION/tsearch\_data/arabic.rules.18 Dosya içeriği örneği: َ (Fetha) \-\> (Boşluk yok) ً (Fethatan) \-\> ُ (Damme) \-\> ...

Veritabanı içi konfigürasyon:

SQL

CREATE EXTENSION unaccent;  
CREATE TEXT SEARCH CONFIGURATION public.quran ( COPY \= simple );  
CREATE TEXT SEARCH DICTIONARY arabic\_stem (  
    TEMPLATE \= unaccent,  
    RULES \= 'arabic'  
);  
ALTER TEXT SEARCH CONFIGURATION public.quran  
    ALTER MAPPING FOR asciiword, word, hword, hword\_part  
    WITH arabic\_stem, simple;

Bu konfigürasyon sayesinde, veritabanı "El-Rahmân" (harekeli) ile "El-Rahman" (harekesiz) kelimelerini aynı kabul edecektir.

## ---

**6\. Python Uygulama Katmanı ve ETL Süreçleri**

Python, bu mimaride iki kritik role sahiptir: Ham verinin işlenerek veritabanına aktarılması (ETL) ve kullanıcı sorgularının işlenmesi (Query Processing).

### **6.1 ETL (Extract-Transform-Load): Morfolojik Verinin İşlenmesi**

quran-morphology.txt dosyasının veritabanına aktarılması, basit bir dosya okuma işlemi değildir. Veri, hiyerarşik etiketlerden oluşur ve bunların ayrıştırılması gerekir.

**Kullanılacak Kütüphaneler:**

* pandas: Veri manipülasyonu ve CSV işleme için.19  
* psycopg2: PostgreSQL veritabanı bağlantısı ve toplu veri girişi (bulk insert) için.21  
* re (Regular Expressions): Metin dosyasındaki (1:1:1) formatındaki konum bilgilerini ve ROOT:ktb gibi etiketleri ayrıştırmak için.23

**Algoritma Akışı:**

1. **Satır Okuma:** Metin dosyasını satır satır oku.  
2. **Regex ile Ayrıştırma:**  
   * Konum bilgisini al: (Sure:Ayet:Kelime)  
   * Etiketleri parçala: TAG:N, LEM:kitab, ROOT:ktb.  
3. **Kök Normalizasyonu:** Bazı kaynaklarda kökler Buckwalter (ASCII) formatında olabilir (örn. ktb). Bunların Arapça harflere (كتب) dönüştürülmesi gerekir. mustafa0x verisetinde bu zaten yapılmıştır, ancak kontrol edilmelidir.  
4. **Veritabanına Yazma:** İşlenen veriyi words tablosuna aktar. Performans için execute\_batch veya COPY komutu kullanılmalıdır.

### **6.2 Kullanıcı Sorgularının İşlenmesi: "Sorgu Genişletme" (Query Expansion)**

Kullanıcı arayüzüne bir kelime girdiğinde (örn. "Müminler"), sistemin arka planda yapması gereken işlem zinciri şöyledir:

#### **6.2.1 Metin Normalizasyonu (PyArabic)**

Kullanıcı girdisi modern imla ile yazılmış olabilir, ancak veritabanındaki kökler Klasik Arapça formundadır. PyArabic kütüphanesi bu uyumsuzluğu giderir.2

* **Hamze Normalizasyonu:** {أ, إ, آ, ؤ, ئ} karakterlerinin hepsi "Elif" (ا) olarak genelleştirilir.  
* **Son Harf Normalizasyonu:** "Taa Marbuta" (ة) \-\> "Ha" (ه) ve "Yaa" (ى) \-\> "Yaa" (ي) dönüşümleri yapılır.

Python

import pyarabic.araby as araby  
def normalize\_query(text):  
    text \= araby.strip\_tashkeel(text) \# Harekeleri sil  
    text \= araby.normalize\_hamza(text) \# Hamzeleri düzelt  
    return text

#### **6.2.2 Kök Çıkarımı (Tashaphyne ile Stemming)**

Kullanıcının girdiği kelimenin kökünü bulmak için algoritmik bir kök bulucuya ihtiyaç vardır. **Tashaphyne**, Python tabanlı hafif bir kök bulucu (light stemmer) olup, Arapça metinlerde yüksek performans gösterir.27

* **İşlem:** Kullanıcı "Müminler" (المؤمنون \- Al-Mu'minoon) yazar. Tashaphyne, baştaki "Al-" takısını ve sondaki çoğul eki "-oon"u atar. Geriye kök olarak **E-M-N** (امن) kalır.

Python

from tashaphyne.stemming import ArabicLightStemmer  
def extract\_root(word):  
    ArListem \= ArabicLightStemmer()  
    stem \= ArListem.light\_stem(word) \# Ekleri at  
    root \= ArListem.get\_root() \# Kökü çıkar  
    return root

**Kritik Uyarı:** Algoritmik kök bulucular hata yapabilir. Bu nedenle sistem **Hibrit Yaklaşım** kullanmalıdır:

1. Önce, kullanıcının kelimesi words tablosunda token\_clean sütununda tam olarak var mı diye bakılır (Exact Match).  
2. Eğer varsa, o kelimenin veritabanında kayıtlı, insan tarafından doğrulanmış kökü (root sütunu) alınır. Bu %100 doğruluk sağlar.  
3. Eğer kelime veritabanında yoksa (örn. kullanıcı yanlış yazdıysa), o zaman Tashaphyne ile kök tahmin edilmeye çalışılır.

## ---

**7\. Arama Mantığı ve SQL Sorgu Stratejisi**

Sistemin kalbi, Python tarafından hazırlanan verilerin SQL sorgusuna dönüştürüldüğü andır. Kullanıcının "tek kelime araması" aslında arka planda kapsamlı bir küme sorgusuna dönüşür.

### **7.1 Senaryo: Kullanıcı "Yazmak" (ktb) kökünden bir kelime arıyor**

Kullanıcı "Yazıyorlar" (*yaktubûne*) kelimesini arattığında:

1. **Python:** "Yaktubûne" kelimesini analiz eder \-\> Kök: **K-T-B**.  
2. **SQL:** Veritabanına şu soruyu sorar: *"Kökü 'K-T-B' olan tüm kelimeleri ve bu kelimelerin geçtiği ayetleri getir."*

SQL

SELECT DISTINCT  
    s.name\_arabic AS sure\_adi,  
    a.ayah\_number AS ayet\_no,  
    a.content\_uthmani AS ayet\_metni,  
    w.token AS bulunan\_kelime  
FROM words w  
JOIN ayahs a ON w.ayah\_id \= a.id  
JOIN surahs s ON a.surah\_id \= s.id  
WHERE w.root \= 'كتب'; \-- Python'dan gelen kök

Bu sorgu, kullanıcı sadece "yazıyorlar" yazmış olsa bile, sonuçlarda "Kitap", "Kâtip", "Mektup" geçen ayetleri de getirecektir. Bu, kullanıcının "morfolojik yapı nedeniyle zorlanıyorum" sorununa getirilen kesin çözümdür. "Yazma" eylemiyle ilgili tüm semantik alan, semantik vektörler kullanılmadan, tamamen dilbilimsel kök bağlantılarıyla taranmış olur.

### **7.2 Bulanık Arama (Fuzzy Search) Desteği**

Kullanıcı imla hatası yaparsa (örn. "Mümin" yerine "Mumin" yazarsa), pg\_trgm eklentisi devreye girer.28

* Kök bulunamazsa sistem SQL'de SIMILAR TO veya % operatörünü kullanır:  
  SQL  
  SELECT \* FROM words WHERE token\_clean % 'mumin'; \-- Trigram benzerliği

Bu özellik, sistemin kullanıcı hatalarına karşı toleranslı olmasını sağlar.

## ---

**8\. Performans ve Ölçeklenebilirlik Değerlendirmesi**

Önerilen mimarinin performans karakteristikleri:

1. **Veri Hacmi:** Kuran yaklaşık 77.430 kelime ve 6.236 ayetten oluşur. Bu veri hacmi, modern veritabanları (PostgreSQL) için "küçük" kabul edilir. Tüm veritabanı belleğe (RAM) rahatlıkla sığabilir.  
2. **Sorgu Hızı:** words tablosundaki root sütunu indekslendiğinde, bir kök sorgusu 1-2 milisaniye sürer. GIN indeksleri ile tam metin araması da benzer hızlardadır.  
3. **Depolama:** Metin verisi ve indeksler toplamda 50-100 MB civarında bir alan kaplayacaktır, bu da sunucu maliyetlerini minimize eder.

**Optimizasyon Önerisi:** Ayet metinleri statik olduğu için, PostgreSQL'in **Materialized View** özelliği kullanılarak sık yapılan sorguların sonuçları önbelleklenebilir, ancak veri boyutu küçük olduğu için bu erken bir optimizasyon olabilir.

## ---

**9\. Sonuç ve Öneriler**

Kullanıcının talep ettiği Kuran-ı Kerim arama motoru, Arapça'nın morfolojik zorluklarını aşmak için standart metin eşleştirme yöntemlerinin ötesine geçmelidir. Bu raporda sunulan çözüm, **Quranic Arabic Corpus**'un doğrulanmış verilerini **PostgreSQL**'in ilişkisel gücü ve **Python**'un işleme yeteneği ile birleştiren deterministik bir mimaridir.

**Temel Çıkarımlar:**

1. **Semantik Değil Morfolojik Arama:** Vektör veritabanlarına ihtiyaç yoktur. Kuran'ın kelime türetim sistemi (kök-gövde), anlam ilişkilerini kurmak için yeterli bir ağ sağlar.  
2. **Veri Kaynağı Kritiktir:** mustafa0x/quran-morphology gibi etiketlenmiş veri setleri kullanılmalıdır; ham metin dosyaları bu proje için yetersizdir.  
3. **PostgreSQL Konfigürasyonu:** Varsayılan ayarlarla değil, unaccent ve özel sözlükler yapılandırılarak kullanılmalıdır.  
4. **Hibrit Kök Çıkarımı:** Python'daki algoritmik kök bulucular (Tashaphyne), veritabanındaki insan doğrulamalı kök verisiyle desteklenmelidir.

Bu mimari, kullanıcının "tek kelime" girerek Kuran'ın derinlikli anlam dünyasında, dilin yapısına sadık kalarak, kesin ve kapsamlı sonuçlara ulaşmasını sağlayacaktır. Proje, teknik karmaşıklığı arka planda tutarak, kullanıcıya sade ama dilbilimsel olarak zengin bir arama deneyimi sunma potansiyeline sahiptir.

#### **Works cited**

1. Awesome-Muslims/README.md at master \- GitHub, accessed February 1, 2026, [https://github.com/choubari/Awesome-Muslims/blob/master/README.md](https://github.com/choubari/Awesome-Muslims/blob/master/README.md)  
2. Python Functions for Arabic \- al-Raqmiyyāt, accessed February 1, 2026, [https://maximromanov.github.io/2013/01-02.html](https://maximromanov.github.io/2013/01-02.html)  
3. pyarabic/pyarabic/normalize.py at master · linuxscout/pyarabic \- GitHub, accessed February 1, 2026, [https://github.com/linuxscout/pyarabic/blob/master/pyarabic/normalize.py](https://github.com/linuxscout/pyarabic/blob/master/pyarabic/normalize.py)  
4. risan/quran-json: Quran text and translations in JSON format. \- GitHub, accessed February 1, 2026, [https://github.com/risan/quran-json](https://github.com/risan/quran-json)  
5. AbdullahGhanem/quran-database: quran mysql database \- GitHub, accessed February 1, 2026, [https://github.com/AbdullahGhanem/quran-database](https://github.com/AbdullahGhanem/quran-database)  
6. Data Download \- Quranic Arabic Corpus, accessed February 1, 2026, [https://corpus.quran.com/download](https://corpus.quran.com/download)  
7. The Quranic Arabic Corpus \- Word by Word Grammar, Syntax and Morphology of the Holy Quran, accessed February 1, 2026, [https://corpus.quran.com/](https://corpus.quran.com/)  
8. mustafa0x/quran-morphology \- GitHub, accessed February 1, 2026, [https://github.com/mustafa0x/quran-morphology](https://github.com/mustafa0x/quran-morphology)  
9. Building Full Arabic Text Search with PostgreSQL | by Ali Shiyyab | Jan, 2026 | Medium, accessed February 1, 2026, [https://medium.com/@aliakefsh/building-full-arabic-text-search-with-postgresql-2431aa282707](https://medium.com/@aliakefsh/building-full-arabic-text-search-with-postgresql-2431aa282707)  
10. Full-text search engine with PostgreSQL \- Fibertide, accessed February 1, 2026, [https://fibertide.com/knowledge/textsearch/](https://fibertide.com/knowledge/textsearch/)  
11. Postgres Full-Text Search: A Search Engine in a Database | Crunchy Data Blog, accessed February 1, 2026, [https://www.crunchydata.com/blog/postgres-full-text-search-a-search-engine-in-a-database](https://www.crunchydata.com/blog/postgres-full-text-search-a-search-engine-in-a-database)  
12. Documentation: 18: 12.9. Preferred Index Types for Text Search \- PostgreSQL, accessed February 1, 2026, [https://www.postgresql.org/docs/current/textsearch-indexes.html](https://www.postgresql.org/docs/current/textsearch-indexes.html)  
13. RUM: improved inverted index for full-text search based on GIN index | Supabase Docs, accessed February 1, 2026, [https://supabase.com/docs/guides/database/extensions/rum](https://supabase.com/docs/guides/database/extensions/rum)  
14. Difficult Fuzzy Search: Principles of Unique GIN, GiST, SP-GiST, and RUM Indexes of PostgreSQL \- Alibaba Cloud Community, accessed February 1, 2026, [https://www.alibabacloud.com/blog/difficult-fuzzy-search-principles-of-unique-gin-gist-sp-gist-and-rum-indexes-of-postgresql\_595632](https://www.alibabacloud.com/blog/difficult-fuzzy-search-principles-of-unique-gin-gist-sp-gist-and-rum-indexes-of-postgresql_595632)  
15. The unaccent extension \- Neon Docs, accessed February 1, 2026, [https://neon.com/docs/extensions/unaccent](https://neon.com/docs/extensions/unaccent)  
16. 18: F.48. unaccent — a text search dictionary which removes diacritics \- PostgreSQL, accessed February 1, 2026, [https://www.postgresql.org/docs/current/unaccent.html](https://www.postgresql.org/docs/current/unaccent.html)  
17. Re: BUG \#13440: unaccent does not remove all diacritics \- PostgreSQL, accessed February 1, 2026, [https://www.postgresql.org/message-id/CAEepm%3D3Th%2B3XRiOoXewLvL1DybCbKxjc0FE4o6XqaZZBLUSOvg%40mail.gmail.com](https://www.postgresql.org/message-id/CAEepm%3D3Th%2B3XRiOoXewLvL1DybCbKxjc0FE4o6XqaZZBLUSOvg%40mail.gmail.com)  
18. Documentation: 18: 12.6. Dictionaries \- PostgreSQL, accessed February 1, 2026, [https://www.postgresql.org/docs/current/textsearch-dictionaries.html](https://www.postgresql.org/docs/current/textsearch-dictionaries.html)  
19. Python and Pandas on Quranic Root Words \- AbdulBaqi, accessed February 1, 2026, [http://abdulbaqi.io/2019/01/19/quranic-roots-pandas/](http://abdulbaqi.io/2019/01/19/quranic-roots-pandas/)  
20. How to insert the records into postgresql python? \- Stack Overflow, accessed February 1, 2026, [https://stackoverflow.com/questions/71019338/how-to-insert-the-records-into-postgresql-python](https://stackoverflow.com/questions/71019338/how-to-insert-the-records-into-postgresql-python)  
21. Insert Python list into PostgreSQL database \- GeeksforGeeks, accessed February 1, 2026, [https://www.geeksforgeeks.org/python/insert-python-list-into-postgresql-database/](https://www.geeksforgeeks.org/python/insert-python-list-into-postgresql-database/)  
22. Fastest Way to Load Data Into PostgreSQL Using Python | Haki Benita, accessed February 1, 2026, [https://hakibenita.com/fast-load-data-python-postgresql](https://hakibenita.com/fast-load-data-python-postgresql)  
23. Python library to read and extract information from the Quranic Arabic Corpus \- GitHub, accessed February 1, 2026, [https://github.com/assem-ch/python-qurancorpus](https://github.com/assem-ch/python-qurancorpus)  
24. Detecting Arabic characters in regex \- python \- Stack Overflow, accessed February 1, 2026, [https://stackoverflow.com/questions/50971337/detecting-arabic-characters-in-regex](https://stackoverflow.com/questions/50971337/detecting-arabic-characters-in-regex)  
25. PyArabic: A Python package for Arabic text \- ResearchGate, accessed February 1, 2026, [https://www.researchgate.net/publication/370057456\_PyArabic\_A\_Python\_package\_for\_Arabic\_text](https://www.researchgate.net/publication/370057456_PyArabic_A_Python_package_for_Arabic_text)  
26. PyArabic: A Python package for Arabic text \- Semantic Scholar, accessed February 1, 2026, [https://pdfs.semanticscholar.org/5e7a/96362421fe53cca22ce06ccf95c4c61622f9.pdf](https://pdfs.semanticscholar.org/5e7a/96362421fe53cca22ce06ccf95c4c61622f9.pdf)  
27. Tashaphyne: A Python package for Arabic Light Stemming \- Open Journals, accessed February 1, 2026, [https://www.theoj.org/joss-papers/joss.06063/10.21105.joss.06063.pdf](https://www.theoj.org/joss-papers/joss.06063/10.21105.joss.06063.pdf)  
28. Fuzzy Search with PostgreSQL Trigrams: Smarter Matching Beyond LIKE | by Vinod Jagwani | Medium, accessed February 1, 2026, [https://medium.com/@vinodjagwani/fuzzy-search-with-postgresql-trigrams-smarter-matching-beyond-like-bce2bd3c4548](https://medium.com/@vinodjagwani/fuzzy-search-with-postgresql-trigrams-smarter-matching-beyond-like-bce2bd3c4548)  
29. Postgres Fuzzy Search With pg\_trgm: Smart Database Guesses What You Want and Returns "Cat Food"... | Towards Data Science, accessed February 1, 2026, [https://towardsdatascience.com/postgres-fuzzy-search-with-pg-trgm-smart-database-guesses-what-you-want-and-returns-cat-food-4b174d9bede8/](https://towardsdatascience.com/postgres-fuzzy-search-with-pg-trgm-smart-database-guesses-what-you-want-and-returns-cat-food-4b174d9bede8/)