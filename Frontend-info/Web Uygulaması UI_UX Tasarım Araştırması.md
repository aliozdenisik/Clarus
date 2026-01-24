# **Faydacı Lüksün Dijital Mimarisi: Fare Odaklı Metin Analiz Araçları İçin Kapsamlı UI/UX Tasarım Raporu**

## **1\. Yönetici Özeti ve Tasarım Paradigması**

Yazılım geliştirme araçları ve veri yoğunluklu uygulamalar dünyasında, son yıllarda "Faydacı Lüks" (Utilitarian Luxury) olarak adlandırılan yeni bir estetik ve işlevsel paradigma yükselişe geçmiştir. Linear, Raycast ve Vercel gibi platformların öncülük ettiği bu akım, komut satırı arayüzlerinin (CLI) ham verimliliğini, yüksek kaliteli tüketici elektroniği ürünlerinin görsel sofistikasyonu ile birleştirmektedir. Bu rapor, söz konusu estetiği temel alan ancak geleneksel olarak klavye odaklı olan bu yapıyı, fare ve dokunmatik etkileşim öncelikli bir web uygulamasına dönüştürmek için kapsamlı bir tasarım stratejisi sunmaktadır. Özellikle "Ayet Koleksiyonları" (Verse Collections) gibi akademik ve manevi derinliği olan metinlerin yönetimi için tasarlanan bu sistem; Landing Page, Kimlik Doğrulama, Kullanıcı Profili ve temel Okuma/Analiz modüllerini kapsamaktadır.

Analiz, modern web teknolojilerinin (React Server Components, Tailwind CSS v4) sunduğu imkanlar ile kullanıcı psikolojisi (karanlık modun algısal yükü, iyimser UI güncellemeleri) arasındaki kesişim noktalarına odaklanmaktadır. Rapor boyunca, CLI araçlarının "hız" hissinin, fare hareketlerine duyarlı mikro etkileşimlerle nasıl yeniden üretileceği ve yoğun metin verilerinin "Bento" ızgaraları ve bölünmüş paneller aracılığıyla nasıl yönetileceği detaylandırılacaktır.1

## **2\. Estetik Temeller: Linear ve Raycast Ekolünün Dekonstrüksiyonu**

"Faydacı Lüks" estetiği, sadece görsel bir kabuk değil, aynı zamanda kullanıcıya güven ve hız telkin eden bir iletişim dilidir. Bu dilin fare odaklı bir arayüze tercüme edilmesi, görsel hiyerarşinin ve renk teorisinin yeniden ele alınmasını gerektirir.

### **2.1 Karanlık Modun Ötesinde: "Linear Tarzı" Renk Paleti ve Derinlik**

Modern "developer-focused" (geliştirici odaklı) araçlar, standart "dark mode" (siyah üzerine beyaz) anlayışını terk ederek, çok katmanlı ve kromatik bir karanlık tema benimsemiştir. Linear ve Raycast örneklerinde görüldüğü üzere, arayüz zifiri siyah (\#000000) yerine, derin gri tonları (Zinc, Slate, Charcoal) ve düşük doygunluklu renklerin karmaşık bir kombinasyonunu kullanır.2

#### **2.1.1 Kromatik Derinlik ve Yüzey Katmanları**

Arayüz tasarımında "yüzeyler", ışık kaynağının simülasyonu ile birbirinden ayrılır. Fare odaklı bir tasarımda bu ayrım, tıklanabilir alanların (affordance) algılanması için kritiktir.

* **Temel Katman (Background):** Uygulamanın en alt katmanı için \#09090b (Zinc-950) gibi soğuk ve metalik bir ton tercih edilmelidir. Bu, OLED ekranlarda enerji tasarrufu sağlarken, saf siyahın yarattığı kontrast sertliğini (smearing) engeller.3  
* **İşlevsel Yüzeyler (Components):** Kartlar, paneller ve menüler için \#18181b (Zinc-900) veya \#1c1917 (Stone-900) kullanılmalıdır. Bu yüzeyler, üzerlerine gelen içeriklerin (ayet metinleri, butonlar) "havada asılı" durduğu hissini vermelidir.  
* **Aydınlatılmış Sınırlar (Glowing Borders):** "Linear estetiğinin" en belirgin imzası, 1px kalınlığındaki, ince bir gradyanla aydınlatılmış kenarlıklardır. CSS box-shadow veya mask-image kullanılarak oluşturulan bu kenarlıklar, üstten gelen bir ışık kaynağını taklit eder ve fare imleci yaklaştığında parlayarak interaktiflik hissini güçlendirir.2

| Katman Tipi | Renk Kodu (Tailwind v4 Token) | Kullanım Amacı | Psikolojik Etki |
| :---- | :---- | :---- | :---- |
| **Canvas** | bg-zinc-950 | Ana arka plan, sonsuzluk hissi. | Odaklanma ve derinlik. |
| **Surface 1** | bg-zinc-900 / bg-opacity-50 | Bento kutuları, kenar çubuğu. | Yapısal bütünlük. |
| **Surface 2** | bg-zinc-800 | Hover durumları, aktif öğeler. | Etkileşim daveti. |
| **Border** | border-white/10 | Pasif sınırlar. | İnce ayrım. |
| **Highlight** | border-white/20 | Aktif sınırlar, odaklanmış inputlar. | Premium hassasiyet. |

### **2.2 Camlaşma (Glassmorphism) ve Bağlamsal Bulanıklık**

Fare ile yönetilen arayüzlerde, açılır menüler (popovers) ve modallar sıkça kullanılır. Kullanıcının arka plandaki içerikten (örneğin okuduğu ayetten) kopmaması için, "Post-Neumorphic" bir yaklaşım olan gelişmiş camlaşma teknikleri uygulanmalıdır.5 Arka planın hafifçe bulanıklaştırılması (backdrop-filter: blur(12px)), odaklanılan içeriği öne çıkarırken, bağlamı korur. Bu teknik, özellikle "Verse Collections" modülünde, ayetlerin üzerinde açılan tefsir veya not pencerelerinde görsel gürültüyü azaltmak için hayati önem taşır.6

### **2.3 Tipografi: Teknik Hassasiyet ve Okunabilirlik**

Uygulamanın bir "CLI aracı" ruhunu taşıması, tipografi seçimlerini doğrudan etkiler. Ancak uzun metinlerin (ayetler ve açıklamalar) okunabilirliği, saf bir kod editörü fontundan fazlasını gerektirir.

* **UI ve Başlıklar:** *Inter* veya *Geist Sans* gibi nötr, yüksek x-yüksekliğine sahip sans-serif fontlar, arayüz elemanlarında (butonlar, etiketler, menüler) kullanılmalıdır. Bu fontlar, küçük boyutlarda bile yüksek okunabilirlik sağlar ve "teknik" bir hava katar.7  
* **Veri ve Metadata:** Ayet numaraları, ID'ler, tarihler ve istatistiksel veriler için *JetBrains Mono* veya *Geist Mono* gibi monospace fontlar tercih edilmelidir. Bu, uygulamanın "veri tabanlı" ve "kesin" yapısını vurgular.4  
* **İçerik (Ayet Metinleri):** Uzun okumalar için, gözü yormayan ve manevi bir ağırlığı olan modern serif fontlar (örneğin *Domaine Text* veya *Merriweather*) kullanılmalıdır. Bu zıtlık (Technical Shell vs. Organic Content), "Lüks" hissini yaratan temel unsurdur.8

## **3\. Fare Odaklı Etkileşim Mimarisi: "Tıklanabilir Terminal"**

Orijinal talepte belirtilen "klavye odağı olmayan" (mouse-first) yaklaşım, bu tasarımın en zorlu kısmıdır. Linear ve Raycast gibi araçlar hızlarını klavye kısayollarından (Cmd+K, Cmd+C) alır. Fare odaklı bir tasarımda bu hız hissini korumak için, görsel arayüzün "tahmin edilebilir" ve "erişilebilir" olması gerekir.

### **3.1 Görünür Komut Paleti (The Clickable Command Bar)**

Geleneksel "gizli" komut paleti (Command Palette) yerine, sayfanın merkezine veya üst kısmına yerleştirilmiş, her zaman görünür ve tıklanabilir bir **Küresel Eylem Çubuğu** (Global Action Bar) tasarlanmalıdır.9

* **Tasarım:** Geniş, yarı saydam ve hafifçe parlayan bir arama çubuğu. İçinde "Ayet ara, koleksiyon oluştur veya profilini düzenle..." gibi yönlendirici bir yer tutucu metin (placeholder) bulunmalıdır.  
* **Fare Etkileşimi:** Çubuğa tıklandığında, sadece son aramalar değil, "Hızlı Eylemler" (Quick Actions) listesi de açılmalıdır. Bu liste, klavye kullanmadan erişilebilecek bir menü gibi davranır: "Yeni Koleksiyon Ekle", "Gece Modunu Aç", "Rastgele Ayet Getir" gibi seçenekler, büyük ve tıklanabilir alanlar olarak sunulmalıdır.11  
* **Akıllı Öneriler:** Kullanıcı fareyi arama sonuçları üzerinde gezdirdiğinde, sağ tarafta o sonuca ait detaylı bir ön izleme paneli (preview pane) belirmelidir. Bu, kullanıcının tıklamadan önce içeriği görmesini sağlayarak (peek), "geri-ileri" navigasyon maliyetini düşürür ve hızı artırır.13

### **3.2 Bağlamsal Zeka: Sağ Tık ve Hover Menüleri**

Linear'ın masaüstü uygulamasında sağ tık menüleri (context menus), klavye kısayollarını öğrenmemiş kullanıcılar için bir eğitim aracı ve hızlandırıcı olarak kullanılır. Bu web uygulamasında, tarayıcının varsayılan sağ tık menüsü yerine, uygulamaya özel, zenginleştirilmiş bir menü sistemi entegre edilmelidir.14

* **Sağ Tık (Context Menu):** Bir ayet kartına sağ tıklandığında; "Kopyala", "Koleksiyona Ekle", "Karşılaştır", "Paylaş" ve "Tefsirini Gör" seçeneklerini içeren, ikonlarla zenginleştirilmiş şık bir menü açılmalıdır. Bu menü, Radix UI ContextMenu bileşeni kullanılarak erişilebilir ve performanslı hale getirilebilir.16  
* **Hover Tetikleyicileri:** Görsel kalabalığı azaltmak için, "Beğen", "Kaydet" veya "Düzenle" butonları, kullanıcı fareyi ilgili satırın veya kartın üzerine getirene kadar gizli tutulmalı veya düşük opaklıkta (%30) gösterilmelidir. Fare üzerine geldiğinde bu araçlar %100 opaklığa ulaşarak ve hafifçe büyüyerek (scale: 1.05) etkileşime davet etmelidir.17

### **3.3 Manyetik Etkileşimler ve Fizik Temelli Hareket**

Klavye tuşlarının verdiği dokunsal (tactile) geri bildirimin eksikliği, görsel fizik kuralları ile telafi edilmelidir.

* **Manyetik Butonlar:** Framer Motion kütüphanesi kullanılarak, fare imleci bir butona yaklaştığında butonun imlece doğru hafifçe "çekilmesi" (magnetic effect) sağlanmalıdır. Bu, butonun tıklanabilir alanını hissettirir ve "lüks" bir akışkanlık katar.19  
* **Sıvı Geçişler (Layout Animations):** Bir listeden öğe silindiğinde veya filtreleme yapıldığında, öğeler aniden yok olmamalı; diğer öğeler boşluğu doldurmak için yumuşak bir yay (spring) animasyonu ile kaymalıdır. Bu, arayüzün canlı ve organik olduğu hissini yaratır.20

## **4\. Landing Page: "Göster, Anlatma" Prensibi ve Bento Izgarası**

Karşılama sayfası (Landing Page), uygulamanın vaat ettiği "Faydacı Lüks" deneyiminin vitrinidir. 2025 tasarım trendlerine uygun olarak, bu sayfa metin ağırlıklı açıklamalar yerine, ürünün kendisini ve yeteneklerini sergileyen modüler bir "Bento Izgarası" (Bento Grid) yapısında olmalıdır.21

### **4.1 Hero Bölümü: Sinematik ve Ürün Odaklı**

* **Başlık:** "Ayetlerin CLI Hızıyla Buluştuğu Nokta" veya "Kutsal Metinler İçin Nihai Çalışma Alanı" gibi iddialı, sans-serif ve sıkı kerning (harf aralığı) uygulanmış bir başlık. Metin, "Linear" tarzı bir gradyanla (beyazdan şeffaf griye) maskelenerek metalik bir ışıltı verilebilir.2  
* **Görsel:** Soyut vektörler yerine, uygulamanın "Ayet Karşılaştırma" (Split View) arayüzünün yüksek çözünürlüklü, hafifçe eğimli (3D tilt) ve gölgeli bir ekran görüntüsü kullanılmalıdır. Bu görsel, kullanıcının fare hareketine göre çok hafifçe dönerek (parallax) derinlik hissi yaratmalıdır.  
* **CTA (Eylem Çağrısı):** "Hemen Başla" butonu, arka plandan gelen bir "glow" (parlama) efektiyle vurgulanmalı ve tıklandığında "Login" modalını tetiklemelidir.8

### **4.2 Bento Izgarası ile Özellik Sunumu**

Özellikleri madde işaretleriyle anlatmak yerine, her biri ayrı bir görsel hikaye anlatan ızgara kutuları kullanılmalıdır.25

* **Kutu 1 (Geniş \- Sol Üst):** "Çoklu Karşılaştırma" özelliğini gösteren interaktif bir mini demo. Kullanıcı fareyi sürükleyerek iki farklı meali yan yana getirebilir.  
* **Kutu 2 (Kare \- Sağ Üst):** "Performans" vurgusu. Sayaç gibi çalışan, sürekli artan "İndekslenen Ayet Sayısı" (örneğin: 6.236+). Rakamlar *Geist Mono* fontuyla ve neon yeşili/amber renginde gösterilerek "terminal" havası verilir.  
* **Kutu 3 (Dikey \- Sol Alt):** "Karanlık Mod" estetiği. Kullanıcının bir toggle düğmesine tıklayarak o kutu içindeki temayı değiştirebildiği mini bir simülasyon.  
* **Kutu 4 (Geniş \- Sağ Alt):** "Koleksiyon Yönetimi". Sürükle-bırak (drag & drop) özelliği ile ayetlerin klasörlere taşındığını gösteren bir loop animasyon (GIF veya Lottie).27

### **4.3 Güven ve Sosyal Kanıt**

"Lüks" algısını pekiştirmek için, kullanılan teknolojilerin (React, Next.js, Vercel) veya veri kaynaklarının (Diyanet, Quran.com API) logoları, monokrom ve düşük opaklıkta bir şerit (ticker) olarak sayfanın altında akmalıdır. Bu logolar, fare üzerine gelince orijinal renklerine dönerek ince bir etkileşim sunmalıdır.4

## **5\. Kimlik Doğrulama ve Kullanıcı Profili: Veri Görselleştirme Sanatı**

### **5.1 Sürtünmesiz Giriş (Frictionless Auth)**

Giriş ekranı, ayrı bir sayfaya yönlendirmek yerine, mevcut sayfanın üzerinde açılan bir "Modal" veya "Overlay" olarak tasarlanmalıdır. Bu, kullanıcının bağlamdan kopmamasını sağlar.

* **Tasarım:** Arka plan bulanıklaştırılır (backdrop-blur-xl). Giriş kartı, ince bir parlak kenarlıkla çevrelenir.  
* **Yöntem:** E-posta/Şifre yerine "Magic Link" veya "GitHub/Google ile Devam Et" seçenekleri öne çıkarılmalıdır. Bu, geliştirici kitlesinin alışkanlıklarına uygundur ve "parolasız gelecek" trendini yakalar.28

### **5.2 Profil: Bir İstatistik Paneli Olarak Kimlik**

Kullanıcı profili sayfası, sadece ayarları değiştirmek için değil, kullanıcının okuma ve araştırma alışkanlıklarını görselleştirmesi için bir "Dashboard" olarak kurgulanmalıdır.6

* **Katkı Grafiği (Heatmap):** GitHub'ın katkı grafiğine benzer şekilde, kullanıcının yıl boyunca hangi günlerde kaç ayet okuduğunu veya kaydettiğini gösteren, pikselli bir ısı haritası. Renkler, temanın ana vurgu rengine (örneğin Emerald veya Violet) göre koyudan açığa doğru değişmelidir.21  
* **Koleksiyon Kartları:** Kullanıcının oluşturduğu koleksiyonlar, "Cover Art" (Kapak Görseli) olarak soyut İslami geometrik desenler veya minimalist tipografi içeren kartlar şeklinde listelenmelidir.  
* **İyimser Ayarlar:** Kullanıcı "Bildirimleri Aç" veya "Herkese Açık Profil" gibi bir ayarı değiştirdiğinde, arayüz sunucu yanıtını beklemeden anahtarı (toggle) çevirmelidir. Arka planda hata olursa, anahtar eski haline döner ve nazik bir hata mesajı (Toast) gösterilir. Bu "Optimistic UI" yaklaşımı, uygulamanın yerel bir yazılım kadar hızlı hissedilmesini sağlar.29

## **6\. Çekirdek Modül: Ayet Koleksiyonları ve Karşılaştırmalı Okuma**

Uygulamanın kalbi olan bu modül, yoğun metin verisinin (ayetler, mealler, tefsirler) yönetildiği yerdir. Tasarım, dikkati dağıtmadan maksimum veriyi sunmalıdır.

### **6.1 Bölünmüş Panel (Split-Pane) Mimarisi**

Metin karşılaştırması ve analizi için en ergonomik yapı, yeniden boyutlandırılabilir panellerdir (Resizable Panels).31

* **Düzen:** Ekran dikey olarak iki veya üç sütuna bölünür.  
  * *Sol Panel:* Kaynak Metin (Örn: Arapça Kuran). Büyük puntolu, okunaklı bir hat (Amiri veya KFGQPC Uthman Taha Naskh).  
  * *Sağ Panel:* Hedef Metin (Örn: Türkçe Meal veya İngilizce Çeviri).  
* **Etkileşim:** İki panel arasındaki ayırıcı çizgi (divider), fare ile tutulup sürüklenebilir olmalıdır. Ayırıcı üzerine gelindiğinde, çizgi renk değiştirerek (örneğin maviden mora) aktif olduğunu belli etmelidir.  
* **Senkronize Kaydırma (Scroll Locking):** Kullanıcı sol panelde aşağı indiğinde, sağ paneldeki meal de otomatik olarak eşleşen ayete kaymalıdır. Bu, JavaScript Intersection Observer API kullanılarak hassas bir şekilde kodlanmalıdır.34

### **6.2 Ayet Kartı Bileşeni (Verse Card)**

Liste görünümlerinde her ayet, bağımsız bir "Kart" bileşeni olarak işlenmelidir.

* **Anatomy (Yapı):**  
  * *Başlık:* Sure ve Ayet Numarası (Örn: "2:255"), sol üst köşede, monospace fontla yazılmış, hap şeklinde (pill-shaped) ve düşük kontrastlı bir rozet (badge) içinde.  
  * *Gövde:* Metin içeriği. Okunabilirliği artırmak için satır yüksekliği (line-height) 1.6 veya 1.8 olarak cömertçe ayarlanmalıdır.35  
  * *Aksiyonlar:* Kartın sağ alt köşesinde veya sağ kenarında, fare üzerine gelince beliren "Kaydet", "Kopyala", "Paylaş" ikonları.  
* **Görsel Hiyerarşi:** Arapça metin sağa dayalı (RTL), Latin alfabesindeki mealler sola dayalı (LTR) olmalıdır. Bu zıt yönlü akış, arayüzde dengeli bir simetri yaratır.

### **6.3 İyimser "Kaydetme" (Optimistic Updates) ve Kalp Animasyonu**

Kullanıcı bir ayeti favorilere eklediğinde veya bir koleksiyona kaydettiğinde, sistem anında tepki vermelidir.

* **Mekanizma:** Kullanıcı "Kalp" ikonuna tıklar tıklamaz, ikon anında dolgulu hale gelir ve hafif bir "yaylanma" (bouncing) animasyonu yapar. React Query veya benzeri bir kütüphane kullanılarak, sunucu isteği arka planda (asenkron) işlenirken arayüz güncellenmiş kabul edilir (Optimistic UI). Bu, Raycast ve Linear'ın "hissedilen hızını" yakalamanın anahtarıdır.36

### **6.4 Arama ve Keşif: Perplexity ve Algolia Modeli**

Arama modülü, basit bir filtreleme aracı değil, bir "Cevap Motoru" gibi tasarlanmalıdır.37

* **Arama Arayüzü:** "Perplexity AI" tarzı, sonuçları kaynaklarıyla (citation) birlikte sunan bir yapı. Kullanıcı "Sabır ile ilgili ayetler" yazdığında, sistem sadece ayet listesi dökmez; önce yapay zeka destekli kısa bir özet ("Kuran'da sabır, 90'dan fazla yerde geçer ve genellikle namazla birlikte anılır...") sunar, ardından ilgili ayetleri "Kartlar" halinde listeler.  
* **Filtreleme Çipleri (Chips):** Arama çubuğunun hemen altında, dinamik olarak oluşturulan filtreler (Örn: "Mekki", "Medeni", "Uzun Ayetler", "Kısa Sureler") yer almalıdır. Bu çipler, fare ile seçildiğinde anında listeyi filtrelemelidir (Algolia InstantSearch deseni).39

## **7\. Teknik Altyapı ve Performans Stratejisi**

Tasarımın hayata geçirilmesi, doğru teknoloji yığınının (stack) seçilmesine bağlıdır. "Utilitarian Luxury" sadece görsel değil, performansa dayalı bir lükstür.

### **7.1 React Server Components (RSC) ve Next.js 15**

Yoğun veri setlerinin (binlerce ayet) hızlı yüklenmesi için Next.js 15 ve RSC kullanılmalıdır.

* **Strateji:** Ayet listeleri ve statik içerikler sunucuda (server-side) render edilerek tarayıcıya saf HTML olarak gönderilir. Bu, İlk Zengin Boyama (LCP) süresini milisaniyeler seviyesine indirir.  
* **Nuqs ile URL Yönetimi:** Arama sorguları, filtreler ve aktif koleksiyon ID'si, nuqs kütüphanesi kullanılarak URL parametrelerine (?q=mercy\&view=split) bağlanmalıdır. Bu sayede kullanıcılar, uygulamanın o anki durumunu (state) bir link olarak paylaşabilir ve sayfa yenilendiğinde aynı yerden devam edebilirler.41

### **7.2 Tailwind CSS v4 ve Stil Yönetimi**

Yeni nesil Tailwind v4, derleme süresini ve CSS boyutunu minimize eder.

* **Renk Değişkenleri:** Renkler CSS değişkenleri (--color-surface, \--color-primary) olarak tanımlanmalı ve Tailwind yapılandırmasında eşleştirilmelidir. Bu, gelecekte "Sepia" veya "Okuma Modu" gibi temaların eklenmesini kolaylaştırır.43  
* **Maskeleme (Masking):** Uzun metinlerin alt kısımlarında, "daha fazlası var" hissi uyandırmak için CSS mask-image: linear-gradient(...) kullanılarak metnin yumuşakça silikleşmesi sağlanmalıdır.

### **7.3 Animasyon ve Hareket: Framer Motion**

Uygulamanın "canlı" hissetmesi için Framer Motion kullanılmalıdır.

* **Layout Prop:** Listeler filtrelendiğinde, elemanların aniden kaybolması yerine, kalan elemanların yeni pozisyonlarına kayarak (sliding) yerleşmesi için \<motion.div layout\> özelliği kullanılmalıdır. Bu, kullanıcının mekansal farkındalığını (spatial awareness) korur.20

## **8\. Erişilebilirlik ve Mobil Uyumluluk**

"Faydacı Lüks", sadece masaüstü kullanıcılarına değil, herkese hitap etmelidir.

* **Mobil Adaptasyon:** Bölünmüş paneller (split views), mobilde sekmeli (tabbed) bir yapıya dönüşmelidir. Bento ızgarası tek sütuna inmelidir. Ancak "alt menü" (bottom sheet) kullanılarak, masaüstündeki sağ tık menüsünün işlevselliği dokunmatik jestlerle (uzun basma) sağlanmalıdır.  
* **Klavye Navigasyonu:** Tasarım fare odaklı olsa da, erişilebilirlik (a11y) standartları gereği tüm etkileşimli öğeler (tab index) klavye ile gezilebilir olmalıdır. Odaklanılan öğeler, fare ile üzerine gelindiğindeki gibi belirgin bir "parlama" efektiyle işaretlenmelidir (Focus Ring).45

## **9\. Sonuç ve Öneriler**

Bu rapor, bir "Ayet Koleksiyonu" uygulamasının, modern yazılım geliştirme araçlarının estetik ve işlevsel standartlarına nasıl yükseltilebileceğini ortaya koymuştur. Önerilen tasarım, kullanıcının bilişsel yükünü azaltırken, metinle kurduğu etkileşimi derinleştirmeyi hedefler. Bento ızgaraları ile bilgiyi organize etmek, iyimser UI güncellemeleri ile gecikmeyi algısal olarak yok etmek ve gölgelendirilmiş karanlık mod ile odaklanmayı artırmak, bu projenin başarısının anahtarlarıdır. Geliştirme sürecinde, öncelikle Next.js 15 ve Tailwind v4 altyapısının kurulması, ardından react-resizable-panels ve Radix UI bileşenleri ile arayüz iskeletinin oluşturulması önerilmektedir.

# ---

**Detaylı Tasarım Spesifikasyonu ve Bileşen Analizi**

## **1\. Tasarım Felsefesi: "Tıklanabilir Terminal"**

### **1.1 Çekirdek İlkeler**

Linear ve Raycast araştırmalarından türetilen tasarım, üç temel ilke üzerine kuruludur 1:

1. **Anlık Tepki (Immediacy):** Etkileşimler gecikmesiz hissedilmelidir (Optimistic UI).  
2. **Yoğunluk (Density):** Bilgi yoğunluğu yüksek olmalı ancak tipografik hiyerarşi ile okunabilir kalmalıdır.  
3. **Derinlik (Depth):** Hiyerarşi; kaba gölgelerle değil, ışıklandırma, kenarlık parlamaları ve bulanıklık efektleriyle sağlanmalıdır.

### **1.2 Renk Paleti ve Temalandırma (Tailwind v4 Stratejisi)**

Katı bir renk paleti yerine, CSS değişkenleri ile anlamsal (semantic) bir yapı kurulmalıdır. Bu, Tailwind v4'ün yerel CSS değişkeni desteği ile mükemmel uyum sağlar.

| Değişken Adı | Tailwind Karşılığı | Hex Kodu (Referans) | Kullanım Alanı |
| :---- | :---- | :---- | :---- |
| \--bg-app | bg-zinc-950 | \#09090b | Uygulama arka planı (en alt katman). |
| \--bg-surface | bg-zinc-900 | \#18181b | Kartlar, paneller, bento kutuları. |
| \--bg-highlight | bg-zinc-800 | \#27272a | Hover durumları, aktif öğeler. |
| \--border-subtle | border-zinc-800 | \#27272a | Ayırıcılar, pasif kart sınırları. |
| \--border-glow | border-zinc-700 | \#3f3f46 | Aktif sınırlar, odaklanmış inputlar (ışık efekti). |
| \--text-primary | text-zinc-100 | \#f4f4f5 | Başlıklar, ana ayet metni. |
| \--text-muted | text-zinc-400 | \#a1a1aa | Metadata, tarihler, ikincil eylemler. |
| \--accent-primary | text-indigo-500 | \#6366f1 | Ana aksiyonlar, marka rengi (Raycast moru veya Linear mavisi). |

**Analiz:** Gray veya Slate yerine Zinc kullanılması, tasarıma "SaaS" maviliğinden arınmış, daha endüstriyel ve metalik bir hava katar. Bu, "Faydacı" (Utilitarian) kimliği güçlendirir.

## **2\. Bileşen Mimarisi: "Ayet" Ekosistemi**

### **2.1 Navigasyon: Kenar Çubuğu (Sidebar)**

Geleneksel web sitelerindeki üst menü yerine, masaüstü uygulamalarını (Arc Browser, Slack) andıran kompakt bir sol kenar çubuğu kullanılmalıdır.47

* **Tasarım Deseni:** Daraltılabilir (collapsible) bir kenar çubuğu. Üstte logo, ortada ana modüller (Koleksiyonlar, Favoriler, Geçmiş), altta kullanıcı profili.  
* **Fare Etkileşimi (Mouse Tracking):** Kenar çubuğundaki öğeler üzerinde fare gezdirildiğinde, imleci takip eden hafif bir radyal gradyan (spotlight effect) öğelerin sınırlarını aydınlatmalıdır. Bu, Vercel'in ve Raycast'in web sitelerinde kullanılan modern bir tekniktir.17

### **2.2 Küresel Komut Çubuğu (Global Command Bar)**

Klavye odağı olmasa da, Komut Çubuğu uygulamanın merkezi sinir sistemidir.

* **Görsellik:** Sayfanın içeriğinin üzerinde yüzen, backdrop-blur-md efektli, geniş bir input alanı.  
* **İşlevsellik:**  
  * *Varsayılan Durum:* Tıklandığında "Son Aramalar" ve "Trend Olan Koleksiyonlar" listelenir.  
  * *Yazma Durumu:* Kullanıcı yazdıkça, sonuçlar anında (real-time) filtrelenir.  
  * *Aksiyon:* Sonuçlara tıklandığında, sayfa yenilenmez; ilgili ayet veya koleksiyon bir "Overlay Panel" içinde açılır. Bu, kullanıcının mevcut bağlamını korumasını sağlar.

### **2.3 Ayet Karşılaştırma Bileşeni (Split View)**

Bu bileşen, react-resizable-panels kütüphanesi üzerine inşa edilmelidir.31

* **Yapı:**  
  JavaScript  
  \<PanelGroup direction="horizontal"\>  
    \<Panel defaultSize\={50} minSize\={30}\>  
      \<ScrollArea className\="h-full pr-4"\>  
        {/\* Kaynak Metin (Arapça) \- RTL Desteği \*/}  
        \<div dir\="rtl" className\="font-amiri text-2xl leading-loose"\>  
          {/\* Ayet İçeriği \*/}  
        \</div\>  
      \</ScrollArea\>  
    \</Panel\>

    {/\* Tutamaç (Handle) \- Fare için genişletilmiş hit-area \*/}  
    \<PanelResizeHandle className="w-2 bg-transparent hover:bg-indigo-500/20 transition-colors group"\>  
      \<div className\="w-\[1px\] h-full bg-zinc-800 group-hover:bg-indigo-500 mx-auto" /\>  
    \</PanelResizeHandle\>

    \<Panel defaultSize\={50} minSize\={30}\>  
      \<ScrollArea className\="h-full pl-4"\>  
        {/\* Hedef Metin (Türkçe/İngilizce) \*/}  
        \<div className\="font-serif text-lg text-zinc-300 leading-relaxed"\>  
          {/\* Meal İçeriği \*/}  
        \</div\>  
      \</ScrollArea\>  
    \</Panel\>  
  \</PanelGroup\>

* **UX İçgörüsü:** PanelResizeHandle (Yeniden Boyutlandırma Tutamacı) görsel olarak 1px kalınlığında zarif bir çizgi olmalıdır. Ancak, farenin kolayca yakalayabilmesi için (Fitts Yasası), görünmez tıklama alanı en az 10-12px genişliğinde olmalıdır.

## **3\. Sayfa Düzenleri ve UX Akışları**

### **3.1 Landing Page: "Özellik Katedrali"**

* **Bento Izgarası Stratejisi:**  
  * *Hero (Tam Genişlik):* "Ayet Motoru". Uygulamanın çalışır haldeki ekran görüntüsü, karanlık bir boşlukta süzülüyormuş gibi hafif açılı (perspective) ve altından yansıyan bir ışıkla sunulur.  
  * *Satır 2 (3 Sütun):*  
    * Sütun 1: "Hız". Yanıp sönen imleç (cursor) animasyonuyla anlık arama demosu.  
    * Sütun 2: "Yapı". İç içe geçmiş klasör yapısını gösteren statik bir grafik.  
    * Sütun 3: "Odak". Arayüzün sadeleştiği "Zen Modu"nun bir videosu.  
* **Gradyan Metinler:** Başlıklarda bg-clip-text kullanılarak beyazdan şeffaf griye giden lineer gradyanlar kullanılmalı. Bu, metnin metalik bir yüzeyden ışığı yansıtıyormuş gibi görünmesini sağlar.

### **3.2 Ayet Detay ve Okuma Modu**

* **Tipografi Odaklı Düzen:** Ayet detay sayfasında, UI elemanları (kenar çubukları) geri çekilmeli veya "Dim" (sönük) moda geçmelidir. Odak tamamen metin üzerinde olmalıdır.  
* **Ses Entegrasyonu:** Eğer ayetin ses kaydı varsa, sayfanın altında "SoundCloud" tarzı ince bir dalga formu (waveform) görselleştiricisi yer almalıdır. Oynatma çubuğu, fare ile üzerinde gezindikçe sese duyarlı olarak parlamalıdır.

## **4\. Etkileşim Tasarımı: Fare Odaklı Mikro Etkileşimler**

### **4.1 "Manyetik" Butonlar**

Düzlemsel bir ekranda fiziksel bir his yaratmak için, butonlar fareye tepki vermelidir. Framer Motion ile, fare butona yaklaştığında butonun x ve y ekseninde hafifçe (5-10px) fareye doğru hareket etmesi sağlanabilir. Bu, "yapışkan" (sticky) bir his verir ve tıklama hassasiyetini artırır.19

### **4.2 İyimser Karşılaştırma Anahtarları (Toggles)**

Ayet görünümünde "Meali Göster", "Transkripsiyonu Aç" gibi seçenekler için toggle anahtarları kullanılır.

* **UX Deseni:** Kullanıcı anahtara tıklar tıklamaz UI değişir. Veri henüz yüklenmemişse, mealin geleceği alanda, metin satırları şeklinde yanıp sönen bir iskelet (skeleton) yükleyici belirir. Bu, düzen kaymasını (Layout Shift) engeller ve algılanan performansı artırır.

### **4.3 Bağlamsal "Sağ Tık" Menüleri**

Web tabanlı bir uygulamada "Desktop App" hissi yaratmanın en güçlü yolu, tarayıcının varsayılan sağ tık menüsünü (override) etmektir.

* **Uygulama:** Radix UI ContextMenu kullanılarak.  
* **Menü Öğeleri:**  
  * "Metni Kopyala" (İkonlu)  
  * "Referansı Kopyala (2:255)"  
  * *Ayırıcı Çizgi*  
  * "Koleksiyona Kaydet \>" (Alt Menü açılır)  
  * "Şununla Karşılaştır \>" (Alt Menü: Elmalılı, Diyanet, vb.)  
* **Görsellik:** Menü, tarayıcı menüsünden görsel olarak ayrışmalıdır: Koyu gri arka plan, yuvarlatılmış köşeler (rounded-lg), ince bir border (border-zinc-800) ve hafif bir gölge (shadow-2xl).

## **5\. Teknik Uygulama Kılavuzu (React & Next.js 15\)**

### **5.1 Sunucu ve İstemci Bileşenleri Ayrımı**

* **Sunucu Bileşenleri (page.tsx):** Ham ayet verilerinin veritabanından (PostgreSQL/Supabase) çekilmesi, HTML'in oluşturulması ve ilk SEO render işlemleri burada yapılır. Bu, uygulamanın ilk açılış hızını (TTFB) garanti eder.  
* **İstemci Bileşenleri (VerseList.tsx, Search.tsx):** Arama filtreleme, panellerin yeniden boyutlandırılması ve iyimser güncellemeler gibi interaktif işlemler burada yönetilir.  
* **Nuqs Entegrasyonu:** Arama durumu (state) URL'e bağlanır:  
  JavaScript  
  const \[query, setQuery\] \= useQueryState('q', { history: 'push' })

  Bu sayede kullanıcı app.com/ayetler?q=merhamet linkini kopyalayıp paylaştığında, karşı taraf sayfayı "merhamet" arama sonuçlarıyla açar.42

### **5.2 React Query ile İyimser UI Örneği**

Bir ayeti "Beğenme/Kaydetme" işlemi için örnek kod deseni:

JavaScript

const { mutate } \= useMutation({  
  mutationFn: saveVerseToCollection,  
  onMutate: async (newVerse) \=\> {  
    // 1\. Giden arka plan yenilemelerini iptal et  
    await queryClient.cancelQueries({ queryKey: \['savedVerses'\] })  
      
    // 2\. Mevcut durumun anlık görüntüsünü (snapshot) al  
    const previousVerses \= queryClient.getQueryData(\['savedVerses'\])  
      
    // 3\. UI'ı "başarılı olmuş gibi" güncelle (Optimistic Update)  
    queryClient.setQueryData(\['savedVerses'\], (old) \=\> \[...old, newVerse\])  
      
    // 4\. Geri alma (rollback) için snapshot'ı döndür  
    return { previousVerses }  
  },  
  onError: (err, newVerse, context) \=\> {  
    // 5\. Hata durumunda eski veriyi geri yükle  
    queryClient.setQueryData(\['savedVerses'\], context.previousVerses)  
    toast.error("Kaydedilemedi, lütfen tekrar deneyin.")  
  },  
  onSettled: () \=\> {  
    // 6\. Başarılı veya hatalı, her durumda sunucuyla senkronize ol  
    queryClient.invalidateQueries({ queryKey: \['savedVerses'\] })  
  }  
})

Bu desen, kullanıcının butona bastığı an ile sunucudan yanıt gelmesi arasındaki 200-500ms'lik gecikmeyi arayüzden siler ve "lüks" bir hız hissi yaratır.36

## **6\. Sonuç: Form ve Fonksiyonun Sentezi**

Önerilen "Faydacı Lüks" tasarımı, modern web teknolojilerinin sınırlarını zorlayarak, bir web uygulamasının yerel bir masaüstü yazılımı kadar güçlü ve estetik olabileceğini kanıtlamaktadır. Koyu renkli "Linear" paleti, göz yorgunluğunu azaltarak uzun çalışma oturumlarına olanak tanır. Fare odaklı zeki etkileşimler (manyetik butonlar, sağ tık menüleri, sürüklenebilir paneller), CLI araçlarının verimliliğini grafik arayüzün keşfedilebilirliği ile birleştirir.

Sonuç olarak ortaya çıkan ürün, sadece bir "Ayet Okuma Uygulaması" değil; manevi ve akademik metinler üzerinde derinlemesine çalışmayı mümkün kılan, kullanıcısına saygı duyan ve odaklanmayı teşvik eden dijital bir çalışma tezgahıdır. Bu tasarım sistemi, React ekosisteminin en güncel araçlarını (Next.js 15, Tailwind v4, Radix UI) kullanarak, geleceğin web standartlarını bugünden belirlemektedir.

#### **Works cited**

1. Stunning Examples of Modern Landing Pages \- Muffin Group, accessed January 24, 2026, [https://muffingroup.com/blog/modern-landing-pages/](https://muffingroup.com/blog/modern-landing-pages/)  
2. The rise of Linear style design: origins, trends, and techniques | by Arlene Xu \- Medium, accessed January 24, 2026, [https://medium.com/design-bootcamp/the-rise-of-linear-style-design-origins-trends-and-techniques-4fd96aab7646](https://medium.com/design-bootcamp/the-rise-of-linear-style-design-origins-trends-and-techniques-4fd96aab7646)  
3. Dark Mode Web Design | SEO & UX Trends for 2025, accessed January 24, 2026, [https://designindc.com/blog/dark-mode-web-design-seo-ux-trends-for-2025/](https://designindc.com/blog/dark-mode-web-design-seo-ux-trends-for-2025/)  
4. Supabase \- Best Landing Page Examples \- Fountn, accessed January 24, 2026, [https://fountn.design/website/supabase/](https://fountn.design/website/supabase/)  
5. 8 UI design trends we're seeing in 2025 | by Gabriela Rocha | Pixelmatters | Medium, accessed January 24, 2026, [https://medium.com/pixelmatters/8-ui-design-trends-were-seeing-in-2025-2f24d0f45cb3](https://medium.com/pixelmatters/8-ui-design-trends-were-seeing-in-2025-2f24d0f45cb3)  
6. Top UX/UI Design Trends for 2025 | Fuselab Creative, accessed January 24, 2026, [https://fuselabcreative.com/ui-ux-design-trends-2026-modern-ui-trends-ux-trends-guide/](https://fuselabcreative.com/ui-ux-design-trends-2026-modern-ui-trends-ux-trends-guide/)  
7. Firecrawl \- SaaS Landing Page, accessed January 24, 2026, [https://saaslandingpage.com/firecrawl/](https://saaslandingpage.com/firecrawl/)  
8. Resend page \- SaaS Landing Page, accessed January 24, 2026, [https://saaslandingpage.com/resend/](https://saaslandingpage.com/resend/)  
9. Search Bar Examples: 30 Inspiring UI Designs \[+ UX Tips\] \- Eleken, accessed January 24, 2026, [https://www.eleken.co/blog-posts/search-bar-examples](https://www.eleken.co/blog-posts/search-bar-examples)  
10. Figma command menu ( \+K) components \- Untitled UI, accessed January 24, 2026, [https://www.untitledui.com/components/command-menus](https://www.untitledui.com/components/command-menus)  
11. Command Palette | UX Patterns \#1 \- Medium, accessed January 24, 2026, [https://medium.com/design-bootcamp/command-palette-ux-patterns-1-d6b6e68f30c1](https://medium.com/design-bootcamp/command-palette-ux-patterns-1-d6b6e68f30c1)  
12. Command Palette UI Design: Best practices, Design variants & Examples \- Mobbin, accessed January 24, 2026, [https://mobbin.com/glossary/command-palette](https://mobbin.com/glossary/command-palette)  
13. Command Palette Interfaces \- Philip Davis, accessed January 24, 2026, [https://philipcdavis.com/writing/command-palette-interfaces](https://philipcdavis.com/writing/command-palette-interfaces)  
14. Invisible details \- Building contextual menus \- Linear, accessed January 24, 2026, [https://linear.app/now/invisible-details](https://linear.app/now/invisible-details)  
15. Better menus and view options – Changelog \- Linear, accessed January 24, 2026, [https://linear.app/changelog/2020-08-26-better-menus-and-view-options](https://linear.app/changelog/2020-08-26-better-menus-and-view-options)  
16. Item \- Shadcn UI, accessed January 24, 2026, [https://ui.shadcn.com/docs/components/radix/item](https://ui.shadcn.com/docs/components/radix/item)  
17. CSS Hover Effects: 40 Engaging Animations To Try \- Prismic, accessed January 24, 2026, [https://prismic.io/blog/css-hover-effects](https://prismic.io/blog/css-hover-effects)  
18. React Dense Table \- shadcn.io, accessed January 24, 2026, [https://www.shadcn.io/patterns/table-advanced-2](https://www.shadcn.io/patterns/table-advanced-2)  
19. Browse thousands of Mouse UI images for design inspiration | Dribbble, accessed January 24, 2026, [https://dribbble.com/search/mouse-ui](https://dribbble.com/search/mouse-ui)  
20. Layout Animation — React FLIP & Shared Element \- Motion.dev, accessed January 24, 2026, [https://motion.dev/docs/react-layout-animations](https://motion.dev/docs/react-layout-animations)  
21. Bento SaaS Landing Pages for design inspiration | Saaspo, accessed January 24, 2026, [https://saaspo.com/style/bento](https://saaspo.com/style/bento)  
22. Bento Grid Design: How to Create Modern Modular Layouts in 2026 \- Landdding, accessed January 24, 2026, [https://landdding.com/blog/blog-bento-grid-design-guide](https://landdding.com/blog/blog-bento-grid-design-guide)  
23. SaaS Website Design Ideas and Inspirations for 2025, accessed January 24, 2026, [https://thefinch.design/saas-website-design-ideas/](https://thefinch.design/saas-website-design-ideas/)  
24. Is there ever a reason to have a black/dark landing page for Enterprise SaaS companies?? : r/UI\_Design \- Reddit, accessed January 24, 2026, [https://www.reddit.com/r/UI\_Design/comments/1kw0mzk/is\_there\_ever\_a\_reason\_to\_have\_a\_blackdark/](https://www.reddit.com/r/UI_Design/comments/1kw0mzk/is_there_ever_a_reason_to_have_a_blackdark/)  
25. Bento Grids — one of the 2024 website trends | by Vendula Havelkova | Medium, accessed January 24, 2026, [https://vendula-havelkova.medium.com/bento-grids-one-of-the-2024-website-trends-7b5a31d6b8c8](https://vendula-havelkova.medium.com/bento-grids-one-of-the-2024-website-trends-7b5a31d6b8c8)  
26. Bento Grids, accessed January 24, 2026, [https://bentogrids.com/](https://bentogrids.com/)  
27. Reorder — React drag-to-reorder animation \- Motion.dev, accessed January 24, 2026, [https://motion.dev/docs/react-reorder](https://motion.dev/docs/react-reorder)  
28. Radix UI, accessed January 24, 2026, [https://www.radix-ui.com/](https://www.radix-ui.com/)  
29. How to Use the Optimistic UI Pattern with the useOptimistic() Hook in React \- freeCodeCamp, accessed January 24, 2026, [https://www.freecodecamp.org/news/how-to-use-the-optimistic-ui-pattern-with-the-useoptimistic-hook-in-react/](https://www.freecodecamp.org/news/how-to-use-the-optimistic-ui-pattern-with-the-useoptimistic-hook-in-react/)  
30. Understanding optimistic UI and React's useOptimistic Hook \- LogRocket Blog, accessed January 24, 2026, [https://blog.logrocket.com/understanding-optimistic-ui-react-useoptimistic-hook/](https://blog.logrocket.com/understanding-optimistic-ui-react-useoptimistic-hook/)  
31. Shadcn Resizable, accessed January 24, 2026, [https://www.shadcn.io/ui/resizable](https://www.shadcn.io/ui/resizable)  
32. \[Shadcn/ui React Series — Part 8\] Resizable: Let Users Control Space, Not You \- Medium, accessed January 24, 2026, [https://medium.com/@rivainasution/shadcn-ui-react-series-part-8-resizable-let-users-control-space-not-you-03c018dc85c2](https://medium.com/@rivainasution/shadcn-ui-react-series-part-8-resizable-let-users-control-space-not-you-03c018dc85c2)  
33. react-resizable-panels examples \- CodeSandbox, accessed January 24, 2026, [https://codesandbox.io/examples/package/react-resizable-panels](https://codesandbox.io/examples/package/react-resizable-panels)  
34. How to make Parallel / Text Compare views not suck: Several Tips \- Logos Community, accessed January 24, 2026, [https://community.logos.com/discussion/225092/how-to-make-parallel-text-compare-views-not-suck-several-tips](https://community.logos.com/discussion/225092/how-to-make-parallel-text-compare-views-not-suck-several-tips)  
35. website design \- Multi-column articles \- User Experience Stack Exchange, accessed January 24, 2026, [https://ux.stackexchange.com/questions/39480/multi-column-articles](https://ux.stackexchange.com/questions/39480/multi-column-articles)  
36. Optimistic Updates in React: Making Your UI Feel Instant | by Ishwar T | Medium, accessed January 24, 2026, [https://medium.com/@ishwart466/optimistic-updates-in-react-making-your-ui-feel-instant-b8925145fdef](https://medium.com/@ishwart466/optimistic-updates-in-react-making-your-ui-feel-instant-b8925145fdef)  
37. UX Analysis of Perplexity AI – Citations & Follow-Up Experience \- NextLeap, accessed January 24, 2026, [https://assets.nextleap.app/submissions/UXEvaluationCaseStudyPerplexityAIsCitationsFollow-Ups-f6456a97-ce3d-4338-8ce9-f1d2f60b0f5f.pdf](https://assets.nextleap.app/submissions/UXEvaluationCaseStudyPerplexityAIsCitationsFollow-Ups-f6456a97-ce3d-4338-8ce9-f1d2f60b0f5f.pdf)  
38. Why Perplexity AI is rewriting the rules of AI-powered UX design | by Adrian Levy \- Medium, accessed January 24, 2026, [https://medium.com/design-bootcamp/why-perplexity-ai-is-rewriting-the-rules-of-ai-powered-ux-design-dc72feef915b](https://medium.com/design-bootcamp/why-perplexity-ai-is-rewriting-the-rules-of-ai-powered-ux-design-dc72feef915b)  
39. 7-examples-of-great-site-search-ui \- Algolia, accessed January 24, 2026, [https://www.algolia.com/blog/ux/7-examples-of-great-site-search-ui](https://www.algolia.com/blog/ux/7-examples-of-great-site-search-ui)  
40. React InstantSearch \- Customize existing widgets \- Algolia, accessed January 24, 2026, [https://algolia.com/doc/guides/building-search-ui/widgets/customize-an-existing-widget/react](https://algolia.com/doc/guides/building-search-ui/widgets/customize-an-existing-widget/react)  
41. Tips, Good Practices, and Pitfalls with Next.js 15 \- Staytuneed, accessed January 24, 2026, [https://www.staytuneed.com/blog/tips-good-practices-and-pitfalls-with-next-js-15](https://www.staytuneed.com/blog/tips-good-practices-and-pitfalls-with-next-js-15)  
42. Managing search parameters in Next.js with nuqs \- LogRocket Blog, accessed January 24, 2026, [https://blog.logrocket.com/managing-search-parameters-next-js-nuqs/](https://blog.logrocket.com/managing-search-parameters-next-js-nuqs/)  
43. Tailwind CSS v4.0, accessed January 24, 2026, [https://tailwindcss.com/blog/tailwindcss-v4](https://tailwindcss.com/blog/tailwindcss-v4)  
44. Build a Flawless, Multi-Theme System using New Tailwind CSS v4 & React \- Medium, accessed January 24, 2026, [https://medium.com/render-beyond/build-a-flawless-multi-theme-ui-using-new-tailwind-css-v4-react-dca2b3c95510](https://medium.com/render-beyond/build-a-flawless-multi-theme-ui-using-new-tailwind-css-v4-react-dca2b3c95510)  
45. How to browse websites using a keyboard only \- ADG \- Accessibility Developer Guide, accessed January 24, 2026, [https://www.accessibility-developer-guide.com/knowledge/keyboard-only/browsing-websites/](https://www.accessibility-developer-guide.com/knowledge/keyboard-only/browsing-websites/)  
46. Guidelines for Keyboard User Interface Design | Microsoft Learn, accessed January 24, 2026, [https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dnacc/guidelines-for-keyboard-user-interface-design](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dnacc/guidelines-for-keyboard-user-interface-design)  
47. Arc Browser: Rethinking the Web Through a Designer's Lens | by Gautham \- Medium, accessed January 24, 2026, [https://medium.com/design-bootcamp/arc-browser-rethinking-the-web-through-a-designers-lens-f3922ef2133e](https://medium.com/design-bootcamp/arc-browser-rethinking-the-web-through-a-designers-lens-f3922ef2133e)  
48. A UX analysis of Arc, Opera, and Edge: The future of browser interfaces \- LogRocket Blog, accessed January 24, 2026, [https://blog.logrocket.com/ux-design/ux-analysis-arc-opera-edge/](https://blog.logrocket.com/ux-design/ux-analysis-arc-opera-edge/)  
49. bvaughn/react-resizable-panels \- GitHub, accessed January 24, 2026, [https://github.com/bvaughn/react-resizable-panels](https://github.com/bvaughn/react-resizable-panels)  
50. How to properly manage search params in NextJS App router. Leverage the power of nuqs the right way | by Jaime Ayala | Medium, accessed January 24, 2026, [https://medium.com/@Jaimayal/how-to-properly-manage-search-params-in-nextjs-app-router-leverage-the-power-of-nuqs-the-right-way-9f7238cff76a](https://medium.com/@Jaimayal/how-to-properly-manage-search-params-in-nextjs-app-router-leverage-the-power-of-nuqs-the-right-way-9f7238cff76a)  
51. Concurrent Optimistic Updates in React Query | TkDodo's blog, accessed January 24, 2026, [https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query](https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query)