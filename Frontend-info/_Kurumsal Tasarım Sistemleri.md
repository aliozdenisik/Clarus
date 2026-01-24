**Modern React Uygulama Mühendisliği: Yüksek Performanslı SaaS Tasarım Desenlerinin Kapsamlı** 

**Analizi1. Yönetici Özeti: Faydacı Lüks Çağı ve Yazılım Zanaatkarlığı**

Yazılım endüstrisi, 2020'lerin ortalarında, kullanıcı arayüzü tasarımında ve teknik mimaride belirgin bir olgunlaşma evresine girmiştir. Notion, Linear, Raycast, Superhuman, Perplexity ve Slack gibi uygulamaların öncülük ettiği bu yeni standart, "faydacı lüks" (utilitarian luxury) veya "yazılım zanaatkarlığı" olarak tanımlanabilir. Bu standart, görsel süslemelerden arındırılmış, ancak etkileşim hızı, klavye odaklı navigasyon ve bilgi yoğunluğu açısından saplantılı bir mükemmeliyetçilik barındıran arayüzlerle karakterize edilir. Bu uygulamalar, kullanıcı arayüzünü (UI) bir meta olmaktan çıkarıp, üstün bir etkileşim modelinin savunulabilir bir rekabet avantajı olduğunu kanıtlamıştır.

Modern bir **React** mühendisi için, bu kalite seviyesine ulaşmak, Material UI veya Ant Design gibi standart bileşen kütüphanelerinin ötesine geçmeyi gerektirir. Bu rapor, söz konusu endüstri liderlerinin tasarım ve teknik DNA'sını parçalarına ayırarak, kanonik bir **React uygulama stratejisine** dönüştürmektedir. Analiz, özellikle **React Hooks, Zustand/Redux Toolkit ve Radix UI/Aria** gibi modern React ekosistemi araçlarına odaklanarak, bu referans uygulamaların performansıyla eşleşecek ve potansiyel olarak onları aşacak bir mimariyi tanımlamayı amaçlamaktadır.

Linear'ın karar yorgunluğunu azaltan "doğrusal" akışı, Raycast'in işletim sistemi katmanında birleşen komut paleti ve Superhuman'ın 100ms kuralı, "uygulama kabuğu"nun (application shell) ortadan kalktığı ve içeriğin ön plana çıktığı yeni bir dönemi işaret etmektedir. Bu raporda sunulan veriler ve analizler, rules.md dosyasının oluşturulması için teorik ve pratik temeli oluşturacaktır.**2\. "Linear" Estetiğinin Yapısökümü: Tasarım Sistemi Temelleri**

Modern SaaS uygulamalarının görsel dili aldatıcı derecede basittir. Bu sadelik, titiz boşluk ölçeklerine, kasıtlı tipografiye ve kontrastı stilistik bir seçimden ziyade işlevsel bir araç olarak ele alan "önce karanlık mod" (dark-mode-first) zihniyetine dayanır. Bu estetik, kullanıcının bilişsel yükünü azaltmayı ve "akış" (flow) durumunda kalmasını sağlamayı hedefler.**2.1. Mikro-Etkileşimlerin Fiziği: Yay (Spring) Animasyonları**

Linear veya Raycast gibi uygulamaların "hissiyatı" tesadüfi değildir; bu, UI geçişlerinde standart "easing" (yumuşatma) eğrileri yerine yay (spring) fiziğinin uygulanmasının bir sonucudur. Standart CSS geçişleri (örneğin, ease-in-out), kat edilen mesafeden bağımsız olarak sabit bir süreye sahip oldukları için genellikle mekanik ve yapay hissettirir. Buna karşılık, sertlik (stiffness), sönümleme (damping) ve kütle (mass) ile tanımlanan yay animasyonları, sürekli bir hızı (velocity) korur. Bu, animasyonların kesintiye uğraması durumunda (örneğin, bir kullanıcı açılan bir modalı aniden kapatmak istediğinde) hareketin doğal ve akıcı kalmasını sağlar.**2.1.1. Yay Konfigürasyon Standartları ve React Entegrasyonu**

React ekosisteminde bu hissi yakalamak için standart CSS transition özellikleri yetersiz kalmaktadır. Bunun yerine, fizik tabanlı animasyon motorları olan **Framer Motion** veya **React Spring** tercih edilmelidir. Bu kütüphaneler, React'ın reaktif durumuyla birleşerek fizik tabanlı yetenekleri sunar.

Analizler, "profesyonel" hissettiren arayüzlerin belirli yay parametreleri etrafında kümelendiğini göstermektedir:

**Tablo 1: Yüksek Performanslı Arayüzler İçin Yay (Spring) Parametreleri**

| Etkileşim Tipi | Stiffness (Sertlik) | Damping (Sönümleme) | Mass (Kütle) | Hissiyat Tanımı | Kullanım Alanı |
| ----- | ----- | ----- | ----- | ----- | ----- |
| **Keskin (Snappy)** | 300 \- 400 | 30 \- 35 | 1 | Hızlı, minimum salınım, anında tepki. | Dropdown menüler, Tooltip'ler, Toggle butonları. |
| **Akışkan (Fluid)** | 170 \- 200 | 20 \- 26 | 1 | Yumuşak yerleşme, fiziksel ağırlık hissi. | Sayfa geçişleri, Modal açılışları, Panel kaymaları. |
| **Yumuşak (Gentle)** | 100 \- 120 | 14 \- 20 | 1 | Yavaş, belirgin salınım, sakinleştirici. | Büyük içerik bloklarının yerleşimi, İskelet yükleme çıkışları. |
| **Hatalı (Wobbly)** | \< 100 | \< 10 | 1 | Aşırı yaylanma, ciddiyetsiz, yavaş. | *Kurumsal SaaS uygulamalarında kaçınılmalıdır.* |

Linear estetiği, özellikle "wobbly" (sallanan) yay ön ayarlarından kaçınır. Bunun yerine, nesnenin salınım yapmadan hedefe yerleştiği ancak mekanik bir duruş sergilemediği "kritik sönümlü" (critically damped) yayları kullanır. Bu, kullanıcıya "oyunsu" değil, "hassas" bir araç kullandığı hissini verir. React'te `useSpring` hook'u kullanılarak bu değerler reaktif durumlara bağlanmalı ve dinamik olarak yönetilmelidir.**2.2. Tipografi ve Bilgi Yoğunluğu**

Tüketici uygulamaları etkileşim için beyaz boşluğu (white space) önceliklendirirken, Slack ve Linear gibi kurumsal araçlar, okunabilirlikten ödün vermeden bilgi yoğunluğunu maksimize etmeyi hedefler. Bu denge, son derece hassas bir tipografik ölçeklendirme ile sağlanır.**2.2.1. Inter Font Yığını ve Sistem Varsayılanları**

Bu uygulamaların çoğu, arayüzün "kişiliğini" minimize etmek ve içeriği öne çıkarmak için Inter yazı tipini veya işletim sisteminin varsayılan font yığınını (System Font Stack) kullanır. Bu strateji, sadece estetik bir tercih değil, aynı zamanda performans odaklı bir karardır. Sistem fontları, ağ üzerinden font dosyası indirme gereksinimini ortadan kaldırarak İlk Boyalı İçerik (FCP) ve Düzen Kayması (CLS) metriklerini iyileştirir.

**Önerilen React CSS Font Yığını:**  
font-family: 'Inter var', \-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";  
font-feature-settings: 'cv05', 'cv08', 'ss01';  
Buradaki kritik detay, `font-feature-settings` kullanımıdır. Linear, `cv05` (küçük harf 'l' karakterinin kuyruklu olması) ve `ss01` gibi OpenType özelliklerini kullanarak, kod blokları veya ID numaraları gibi teknik metinlerde karakterlerin (örneğin I, l, 1\) birbirine karışmasını engeller. Bu, geliştirici odaklı araçlar için hayati bir UX detayıdır.**2.2.2. Dinamik Tipografik Ölçekler**

Notion'ın tipografisi, "blok" tabanlı yapısı nedeniyle benzersizdir, ancak temel ölçek genellikle başlıklar için **Büyük Üçlü (Major Third \- 1.250)** veya **Tam Dörtlü (Perfect Fourth \- 1.333)** oranlarını takip eder. Ancak, Linear ve Slack gibi yoğun veri içeren arayüzlerde, UI kontrolleri (etiketler, butonlar) için çok daha sıkı bir ölçek kullanılır. Genellikle **Küçük İkili (Minor Second \- 1.067)** oranı tercih edilir. Bu, yazı boyutları arasında dramatik sıçramalar olmamasını ve dikey ritmin (vertical rhythm) bozulmamasını sağlar.

**Tablo 2: Kurumsal SaaS İçin Anlamsal Tipografi Ölçeği**

| Token | Boyut (px) | Satır Yüksekliği (Line Height) | Letter Spacing | Kullanım Alanı |
| ----- | ----- | ----- | ----- | ----- |
| text-xs | 12px | 16px | 0.02em | Meta veriler, zaman damgaları, rozetler |
| text-sm | 13px | 18px | 0.01em | İkincil etiketler, ipuçları, yoğun liste öğeleri |
| text-base | 14px | 20px | 0 | Birincil gövde metni, giriş (input) değerleri |
| text-md | 16px | 24px | \-0.01em | Modal başlıkları, büyük girişler |
| text-lg | 18px | 28px | \-0.02em | Bölüm başlıkları |
| text-xl | 24px | 32px | \-0.02em | Sayfa başlıkları |

*Derinlemesine Analiz:* 13px boyutuna dikkat edilmelidir. Standart web varsayılanı 14px olmasına rağmen, Linear ve Slack gibi araçlar, ekranın "katlanma çizgisinin" (above the fold) üzerine daha fazla satır sığdırabilmek ve tarama hızını artırmak için liste öğelerinde varsayılan olarak 13px kullanmayı tercih ederler. Bu 1 piksellik fark, binlerce satırlık bir veri setinde önemli bir alan kazanımı sağlar.**2.3. Renk Sistemleri ve Karanlık Mod Fiziği**

Bu uygulamalarda karanlık mod, sadece renklerin tersine çevrilmesi değildir; derinliği belirtmek için gri tonlarının "anlamsal katmanları"nın kullanılmasıdır.

* **Linear'ın Yaklaşımı:** Saf siyah (\#000000) yerine hafifçe tonlanmış koyu griler (örneğin \#0e0c0c veya \#191919) kullanılır. Bu, OLED ekranlarda "smearing" (sürüklenme) etkisini azaltır, göz yorgunluğunu önler ve gölgelerin (box-shadow) görünür kalmasını sağlar, böylece katman hissi korunur.  
* **Derinlik Haritalama:** Kenarlıklar (border) yerine, derinlik genellikle hafif parlaklık (lightness) varyasyonları ile iletilir. Örneğin, arka plan hsl(0, 0%, 8%) iken, bir kart hsl(0, 0%, 12%) ve üzerine gelindiğinde (hover) hsl(0, 0%, 16%) olabilir.  
* **Oklch İnterpolasyonu:** Modern CSS renk uzayları, özellikle **Oklch**, gradyanlar ve durum değişiklikleri için kullanılmalıdır. sRGB'nin aksine, Oklch algısal olarak üniformdur; bu da renklerin parlaklığını değiştirirken tonun (hue) kaymamasını ve "çamurlu" (muddy) geçişlerin oluşmamasını sağlar. Özellikle Linear tarzı "glow" efektlerinde bu teknik kritik öneme sahiptir.

**3\. Mimari Analiz: "Önce Yerel" (Local-First) Zorunluluğu**

Linear, Superhuman ve Raycast'in teknik açıdan en büyük farkı, "yükleniyor çarkı"nı (loading spinner) mimari düzeyde reddetmeleridir. Bu uygulamalar, esasen arka planda bulut ile senkronize olan yerel uygulamalar gibi davranır; yerel olarak önbelleğe alan bulut uygulamaları gibi değil.**3.1. Optimistik UI ve İşlemsel Durum (Transactional State)**

Geleneksel bir React uygulamasında, kullanıcı bir eylem gerçekleştirdiğinde (örneğin, bir görevi arşivleme), bir API çağrısı tetiklenir ve UI yalnızca sunucudan yanıt (promise) döndüğünde güncellenir. "Linear mimarisinde" ise UI, optimistik bir işlem (transaction) aracılığıyla *anında* güncellenir.**3.1.1. React ile Uygulama (Zustand/Redux Toolkit \+ React Query)**

Bu davranışı replike etmek için durum yönetimi katmanının "geri alma" (rollback) yeteneklerini desteklemesi gerekir.

1. **Kullanıcı Eylemi:** Kullanıcı "Arşivle" butonuna tıklar.  
2. **Optimistik Mutasyon:** Yerel Zustand deposu veya **React Query** önbelleği anında güncellenir. Öğe listeden görsel olarak kaldırılır.  
3. **Arka Plan Senkronizasyonu:** API isteği sunucuya gönderilir.  
4. **Uzlaşma (Reconciliation):**  
   * *Başarı:* Sunucu yanıtı yeni durumu onaylar (genellikle güncellenmiş bir `updatedAt` zaman damgası döndürür).  
   * *Başarısızlık:* Mutasyon geri alınır (rollback) ve kullanıcıya bir toast bildirimi ile hata gösterilir.

**React Stratejisi:** **React Query**'nin `onMutate` geri çağrısı (callback), önceki durumu anlık görüntü (snapshot) olarak kaydetmek için kullanılır. `onError` durumunda bu görüntü geri yüklenir. Bu yaklaşım, UI etkileşimini ağ gecikmesinden (latency) tamamen ayırır.**3.2. Çevrimdışı Öncelikli (Offline-First) Veri Katmanları**

Linear ve Superhuman gibi uygulamalar için "çevrimdışı olmak" bir hata durumu değil, tamamen işlevsel bir moddur. Bu, sadece bellek içi (in-memory) durum yerine, istemci tarafı kalıcı bir veritabanı gerektirir.**3.2.1. React için RxDB ve ElectricSQL Karşılaştırması**

* **RxDB (Reactive Database):** Tarayıcıda (IndexedDB üzerinde) çalışan, NoSQL tabanlı bir JavaScript veritabanıdır. Reaktif sorgulara izin vermesi, React'ın durumu ve hook'ları ile mükemmel bir uyum sağlar. Bir React bileşeni, bir RxDB sorgusuna abone olabilir; böylece yerel veri değiştiğinde (ister kullanıcı eylemiyle, ister arka plan senkronizasyonuyla), UI otomatik olarak güncellenir.  
* **ElectricSQL:** Postgres veritabanını tarayıcıdaki yerel bir SQLite/PGlite örneğiyle senkronize etmeye odaklanır. İlişkisel veriler için güçlüdür ancak WASM yükü nedeniyle daha ağırdır.

*Öneri:* Bir React "Linear-klonu" için, JSON API yapılarıyla doğal uyumu ve React Hooks ile doğrudan entegre olabilen reaktif veri kaynağı yeteneği nedeniyle **RxDB** üstün bir seçimdir. RxDB'nin "Observer" yetenekleri, veritabanı değişikliklerini anlık olarak React bileşenlerine yansıtır, bu da karmaşık `useEffect` bağımlılık zincirlerine olan ihtiyacı azaltır.**3.3. Performans: 100ms Kuralı ve React Optimizasyonları**

Superhuman'ın ünlü "100ms kuralı", hiçbir etkileşimin görsel olarak tamamlanmasının 100ms'den uzun sürmemesini dikte eder.

* **JavaScript Yürütme:** Ağır hesaplamalar (arama indeksleme, büyük veri filtreleme) ana iş parçacığından (main thread) alınarak **Web Workers**'a taşınmalıdır.  
* **Sanallaştırma (Virtualization):** Binlerce öğe içeren listeler (Slack kanalı veya Linear backlog'u gibi) sanallaştırılmalıdır. **TanStack Virtual**, kaydırma fiziğini korurken yalnızca görünür görünüm alanındaki (viewport) DOM düğümlerini render ederek endüstri standardı haline gelmiştir.  
* **Memoization ve Callback Optimizasyonu:** React'te gereksiz yeniden render işlemlerini önlemek için `React.memo`, `useMemo` ve `useCallback` agresif bir şekilde kullanılmalıdır. Özellikle büyük listeleri veya karmaşık bileşen ağaçlarını içeren yerlerde bu kritik öneme sahiptir.

**4\. Bileşen Derinlemesine İnceleme ve React Uygulaması**

Hedef uygulamaların imza niteliğindeki bileşenlerini analiz ederek, bunların React ile nasıl yeniden inşa edileceğini inceleyelim.**4.1. Komut Paleti (Raycast / Linear Tarzı)**

Komut Paleti (Cmd+K), bu uygulamaların merkezi sinir sistemidir. Basit bir arama çubuğu değil, bir eylem dağıtıcısıdır. Bulanık arama (fuzzy search), klavye navigasyonu ve modal yönetimi gerektirir.

* **Tasarım Deseni:**  
  * **Stilsiz İlkel Bileşenler (Unstyled Primitives):** Render hattı üzerinde tam kontrol sağlamak için önceden stillendirilmiş kütüphaneler yerine **Radix UI Primitives** veya **React Aria Components** kullanılmalıdır. Bu, erişilebilirlik (ARIA rolleri, odak yönetimi) yükünü framework'e devrederken görsel özgürlük sağlar.  
  * **Bulanık Arama:** Fuse.js veya Command Score algoritmaları doğrudan istemci tarafına entegre edilmelidir. Ağ gecikmesini önlemek için arama işlemi yerel veri üzerinde yapılmalıdır.  
  * **Odak Yönetimi:** Palet açıkken odak hapsedilmeli (focus trap) ve kapatıldığında önceki öğeye geri döndürülmelidir. **React Aria**'nın `useFocusTrap` hook'u bu işlevselliği standartlaştırır.

**Kavramsal React Kod Yapısı:**  
import \* as Dialog from '@radix-ui/react-dialog';  
import { Command } from 'cmdk';

function CommandPalette() {  
  const \[open, setOpen\] \= React.useState(false);

  return (  
    \<Dialog.Root open={open} onOpenChange={setOpen}\>  
      \<Dialog.Portal\>  
        \<Dialog.Overlay className="command-palette-overlay" /\>  
        \<Dialog.Content className="command-palette-content"\>  
          \<Command label="Global Command Palette"\>  
            \<Command.Input placeholder="Bir komut yazın..." className="palette-input" /\>  
            \<Command.List\>  
              {filteredItems.map((item) \=\> (  
                \<Command.Item key={item.id} value={item.label}\>  
                  \<Icon name={item.icon} /\>  
                  {item.label}  
                \</Command.Item\>  
              ))}  
            \</Command.List\>  
          \</Command\>  
        \</Dialog.Content\>  
      \</Dialog.Portal\>  
    \</Dialog.Root\>  
  );

* }

*İçgörü:* Raycast'in "Actions" (Eylemler) sistemi, seçili öğeler üzerinde ikincil operasyonlara (örneğin Cmd+Enter ile kopyalama) izin verir. Bu, bileşen içinde değiştirici tuşları (modifier keys) yönetmek için sağlam bir olay veriyolu (event bus) veya durum makinesi gerektirir.**4.2. Blok Editörü (Notion Tarzı)**

Notion'ın çekirdeği blok tabanlı editörüdür. Her paragraf, başlık veya resim bağımsız bir varlıktır.

* **Veri Modeli:** Her düğümün `id`, `type`, `content` ve `children` dizisine sahip olduğu yinelemeli (recursive) bir ağaç yapısıdır.  
* **Teknik Zorluk:** Yinelemeli bir ağacı React'te render etmek basittir, ancak derinlik arttıkça performans düşer.  
* **React Optimizasyonu:** Dinamik render işlemi için bir bileşen haritalaması kullanılmalıdır. Kritik olarak, tek bir blok değiştiğinde tüm dökümanın yeniden render edilmesini önlemek için **`React.memo`** ve uygun şekilde memoize edilmiş prop'lar kullanılmalıdır.  
* **Contenteditable:** Kök dizinde tek bir `contenteditable="true"` kullanmaktan kaçınılmalıdır. Bunun yerine, her metin bloğu kendi kontrollü girişi veya zengin metin karmaşıklığı yüksekse özelleştirilmiş bir **Tiptap/ProseMirror** (React wrapper'ları) örneği olmalıdır.

**4.3. Yüksek Yoğunluklu Veri Tabloları (Linear Tarzı)**

Linear'ın sorun listesi (issue list), bilgi yoğunluğu konusunda bir ustalık sınıfıdır.

* **Grid vs. Flex:** Sütunların (Öncelik, ID, Başlık, Atanan) katı hizalanmasını sağlamak ve başlık sütununun esnekçe genişlemesine izin vermek için ana düzende **CSS Grid** kullanılmalıdır.  
* **Etkileşimler:**  
  * **Çoklu Seçim:** Shift+Click ve Cmd+Click yönetimi. Bu mantık, tekrar kullanılabilirlik için özel bir `useSelection` hook'u içine soyutlanmalıdır.  
  * **Bağlam Menüleri:** İşletim sistemi davranışını taklit eden ancak uygulamaya özgü eylemler sunan özel bağlam menüleri (**Radix UI ContextMenu** veya **React Aria Menu**) kullanılmalıdır.  
* **Render:** Dikey liste için **TanStack Virtual** kullanılmalıdır. Linear'da satır yükseklikleri genellikle sabittir (örneğin 34px) veya katı adım değerlerine uyar, bu da sanallaştırma matematiğini basitleştirir.

**4.4. Bildirimler ve Toast Mesajları (Sonner / Shadcn)**

Bildirimler engelleyici olmamalı, istiflenebilmeli ve erişilebilir olmalıdır.

* **Tasarım:** Linear ve Vercel panolarında bulunan, sağ alttan veya üst merkezden istiflenen, üzerine gelindiğinde genişleyen "**Sonner**" tarzı toastlar.  
* **Erişilebilirlik:** Durum güncellemeleri için `aria-live="polite"` ve kritik hatalar için `aria-live="assertive"` kullanılmalıdır. Ekran okuyucuların bildirimi tamamlamadan odak değiştirmemesi sağlanmalıdır.  
* **React Uygulaması:** Popüler **Sonner** kütüphanesi veya **Radix UI Toast** ilkel bileşenleri, hedeflediğimiz istifleme fiziğini ve kaydırma (swipe) hareketlerini tam olarak sağlar.

**5\. React Ekosistem Stratejisi**

"Linear kalitesinde" uygulamalar geliştirmek için, React ekosisteminin ağır toplarını doğru seçmek kritiktir.**5.1. Headless UI Kütüphaneleri: Radix UI / React Aria**

* **Kazanan: Radix UI Primitives / React Aria.**  
  * *Gerekçe:* **Radix UI**, bileşenlerin görsel özgürlüğünü en üst düzeye çıkarırken karmaşık erişilebilirlik gereksinimlerini (ARIA nitelikleri, odak yönetimi) yerleşik olarak çözer. **React Aria**, özellikle etkileşim desenleri (liste yönetimi, sürükleme/bırakma) ve klavye etkileşimlerinde daha derin bir soyutlama sunar. Çoğu proje bu iki kütüphanenin hibrit kullanımını tercih eder.  
  * *Alternatif:* **Headless UI (Tailwind Labs)**, daha küçük projeler veya daha az karmaşık etkileşimler için basit bir alternatiftir.

**5.2. Durum Yönetimi: Zustand / Redux Toolkit**

* **Desen:** Küresel, paylaşılan durum için hafif ve minimalist bir çözüm olan **Zustand** tercih edilmelidir. React bağlamından (Context) daha hızlı ve daha az boilerplate gerektirir. TanStack Query ile entegrasyonu basittir.  
* **Yapı:** Depolar (stores) etki alanına (domain) göre ayrılmalıdır (örneğin `useIssueStore`, `useUserStore`).  
* **Veri Alma (Data Fetching):** Sunucu durumu yönetimi için tartışmasız endüstri standardı olan **React Query (TanStack Query)** kullanılmalıdır. Yerel durum (UI state) ile sunucu durumu (Server state) arasındaki ayrımı keskinleştirmek performansı ve geliştirici deneyimini artırır.

**5.3. Stil: Tailwind CSS v4 \+ CSS Değişkenleri**

* **Yaklaşım:** Düzen (layout) için "utility-first" yaklaşımı, ancak tema (renkler, boşluklar, yarıçaplar) için anlamsal CSS değişkenleri kullanılmalıdır.  
* **Değişkenler:** Tasarım sistemi CSS değişkenlerinde tanımlanmalıdır (örneğin `--color-bg-primary`, `--space-4`). Bu, bileşenleri yeniden render etmeden anında tema değiştirmeyi (Açık/Koyu/Yüksek Kontrast) mümkün kılar, bu da performans için kritiktir.  
* **Linear Gradyan Hilesi:** Linear, düz renkleri yumuşatmak için ince gürültü (noise) dokuları ve sofistike gradyanlar (Oklch) kullanır. Bunlar Tailwind içinde özel utility sınıfları olarak tanımlanmalıdır.

**6\. İkinci ve Üçüncü Dereceden İçgörüler6.1. "Yükleme Çarkı Yok" Epistemolojisi**

Linear ve Superhuman'dan alınan en derin içgörü, *gecikmenin bir güven sorunu olduğudur*. Bir kullanıcı bir yükleme çarkı gördüğünde, sistemin güvenilirliğinden şüphe duyar. Optimistik UI'ya geçerek uygulama kullanıcıya şunu söyler: "Niyetine güveniyorum ve senkronizasyonu ben halledeceğim." Bu, mühendislik yükünü "yükleme durumlarını yönetmekten", "senkronizasyon hatalarını yönetmeye" kaydırır. Bunun dalga etkisi, hata işlemenin (toastlar, geri alma eylemleri, yeniden deneme butonları) sonradan düşünülen bir şey değil, birincil bir UI vatandaşı olması zorunluluğudur.**6.2. Döküman ve Uygulamanın Yakınsaması**

Notion, döküman ve uygulama arasındaki çizgiyi bulanıklaştırdı. Linear ve Slack, her nesneyi (bir sorun, bir mesaj) genişletilebilen, gömülebilen ve üzerinde işbirliği yapılabilen ayrı adreslenebilir bir varlık olarak ele alarak bu trendi takip etti.

* *Çıkarım:* **React Router** yapınız son derece sağlam olmalıdır. Her modal, yan panel veya katman esasen bir rota olmalı veya URL sorgu parametrelerini güncellemelidir. Böylece durum, sayfa yenilendiğinde kalıcı olur ve paylaşılabilir hale gelir. "Rota olarak modal" deseni burada kritiktir.

**6.3. Yüksek Performanslı Etkileşim Olarak Erişilebilirlik**

Erişilebilirlik (A11y) genellikle yasal uyumluluk çerçevesinde ele alınır. Ancak Raycast ve Linear gibi araçlarda, A11y uygulaması (ARIA rolleri, odak yönetimi), "güçlü kullanıcı" (power user) özellikleri için bir altyapı görevi görür. Bir ekran okuyucu bir listeyi verimli bir şekilde gezebiliyorsa, bir klavye kullanıcısı da gezebilir. Bu nedenle, WCAG standartlarına sıkı sıkıya bağlılık sadece etik değil; "klavye öncelikli" bir üretkenlik aracı oluşturmanın teknik ön koşuludur.**rules.md: Yüksek Performanslı React Uygulamaları İçin Mühendislik Standartları**

Aşağıdaki kurallar seti, Notion, Linear, Raycast ve diğerlerinin derinlemesine analizine dayanarak, modern bir React kurumsal uygulaması için mimari ve stilistik standartları tanımlar.**Mühendislik Standartları: React Yüksek Performans Paketi (The Linear Stack)1. Temel Mimari ve Felsefe**

* **Önce-Yerel (Local-First) Zihniyeti:** Kullanıcının çevrimdışı olduğunu varsayın. Okuma ve yazma işlemleri anında yerel önbelleğe/depoya (store) vurmalıdır. Ağ senkronizasyonu arka planda gerçekleşir.  
  * *Uygulama:* Asenkron durumlar için agresif `staleTime` ve `onMutate` ile optimistik güncellemeler sağlayan **React Query (TanStack Query)** kullanın. Karmaşık veri gereksinimleri için **RxDB** entegre edin.  
* **100ms Etkileşim Bütçesi:** Hiçbir etkileşim ana iş parçacığını (main thread) 100ms'den fazla bloke etmemelidir.  
  * *Uygulama:* Ağır veri işleme (arama, sıralama) için **Web Workers** kullanın. Gereksiz yeniden render işlemlerini önlemek için `React.memo` ve `useMemo`/`useCallback` kullanın.  
* **Tip Güvenliği:** Katı (Strict) TypeScript pazarlık edilemez. Tüm proplar, olaylar (events) ve store durumları tiplendirilmelidir. API yanıtlarının çalışma zamanı doğrulaması için **zod** kullanın.

**2\. Teknoloji Yığını Seçimi**

* **Framework:** React (Functional Components \+ Hooks).  
* **Derleme Aracı:** Vite/Next.js/Remix (agresif kod bölme \- code splitting için yapılandırılmış).  
* **Durum Yönetimi:** Zustand (veya Redux Toolkit).  
* **Headless UI:** Tüm etkileşimli ilkel bileşenler (Dialogs, Popovers, Dropdowns, Toggles) için **Radix UI Primitives** veya **React Aria Components**. Karmaşık erişilebilirlik mantığını sıfırdan oluşturmayın.  
* **Stil:** Temalandırma için anlamsal CSS değişkenleri ile **Tailwind CSS v4**.  
* **Hareket (Motion):** Yay (spring) fiziği için **Framer Motion** veya **React Spring**.  
* **Sanallaştırma:** 50 öğeyi aşan herhangi bir liste için **TanStack Virtual**.

**3\. Tasarım Sistemi ve UI Desenleri ("Linear Standardı")3.1. Tipografi**

* **Font Yığını:** Maksimum okunabilirlik ve sıfır düzen kayması (CLS) için Inter veya sistem font yığınını kullanın.  
* **Boyutlandırma:** Kompakt bir ölçek kullanın. Temel boyut 14px (veya yüksek yoğunluklu listeler için 13px).  
* **Ağırlıklar:** Destekleniyorsa ince hiyerarşi için değişken font ağırlıkları (örn. 450, 550\) kullanın.

**3.2. Boşluk ve Düzen**

* **4px Izgarası:** Tüm boşluklar 4px'in katları olmalıdır (`spacing-1 = 4px`).  
* **Yoğunluk:** Aşırı dolgudan (padding) kaçının. Buton yükseklikleri kompakt olmalıdır (örn. eylemler için 28px veya 32px, birincil girişler için 36px).  
* **Derinlik:** Katmanları tanımlamak için kenarlık renklerini ve ince gölgeleri (`box-shadow`) kullanın. Karanlık modda yüksek kontrastlı kenarlıklardan kaçının.

**3.3. Hareket ve Etkileşim**

* **Easing Eğrisi Yok:** Tüm etkileşimli geçişler için **Yay Fiziği (Spring Physics)** kullanın.  
  * *Keskin (Snappy):* `{ stiffness: 300, damping: 30 }` (Dropdownlar, Toastlar).  
  * *Akışkan (Fluid):* `{ stiffness: 170, damping: 26 }` (Modallar, Sayfa geçişleri).  
* **Giriş/Çıkış:** Öğeler sadece kaybolmamalı, animasyonla çıkmalıdır. **Framer Motion'ın AnimatePresence** veya eşdeğerlerini kullanın.

**4\. Bileşen Mühendislik Kuralları4.1. Komut Paleti (Raycast Tarzı)**

* **Global Erişim:** Her yerden Cmd+K (Mac) veya Ctrl+K (Windows) ile erişilebilir olmalıdır.  
* **Odak Hapsi (Focus Trap):** Açıkken odağı kesinlikle modal içinde hapsetmelidir.  
* **Bulanık Arama:** Anında geri bildirim için sonuçları istemci tarafında filtreleyin.  
* **Klavye Navigasyonu:** Gezinmek için ok tuşları, seçmek için Enter, kapatmak için Esc.

**4.2. Formlar ve Girişler**

* **Doğrulama:** Her tuş vuruşunda değil, blur (odak kaybı) veya submit anında doğrulama yapın (parola gücü ölçer hariç).  
* **Otomatik Odaklama:** Bir modal açıldığında birincil girişe akıllı otomatik odaklama (`autofocus` veya `useFocus` hook'u) yapın.  
* **Etiketler:** Tüm girişlerin ilişkili `<Label>` bileşenleri olmalıdır (**Radix UI Label**).

**4.3. Listeler ve Tablolar**

* **Sanallaştırma:** 50 öğeden büyük veri setleri için zorunludur.  
* **İskelet Yükleme (Skeleton):** Genel dönen çarklar yerine, içeriğin tam geometrisiyle eşleşen iskeletler kullanın.  
* **Sonsuz Kaydırma:** İçerik akışları için sayfalandırma yerine "daha fazla yükle" tetikleyicilerini veya sonsuz kaydırmayı tercih edin.

**5\. Erişilebilirlik (A11y) Standartları**

* **Klavye Desteği:** Her etkileşimli öğe klavye ile ulaşılabilir ve kullanılabilir olmalıdır.  
* **Odak Göstergeleri:** Özel bir `:focus-visible` stili sağlamadan asla `outline` özelliğini kaldırmayın.  
* **Ekran Okuyucular:** Sadece ikon içeren butonlar için `aria-label` kullanın. Toggle'lar için `aria-expanded` ve `aria-controls` kullanın.  
* **Kontrast:** Metin kontrastı için, özellikle karanlık modda, APCA veya WCAG AA uyumluluğunu sağlayın.

**6\. Kod Konvansiyonları**

* **Hooks:** Mantığı `use...` hook'ları içine çıkarın (örn. `useKeyboard`, `useSelection`).  
* **Bileşen Yapısı:**  
  * Props tipleri TypeScript ile tanımlanmalı.  
  * Durum (`useState`, `useReducer`).  
  * Efektler (`useEffect`).  
  * Memoization (`useMemo`, `useCallback`).  
  * İşleyiciler (Handlers).  
* **İsimlendirme:** Bileşenler için PascalCase (`BaseButton.tsx`), prop/olaylar için camelCase.

**7\. Performans Kontrol Listesi**

* Kümülatif Düzen Kayması (CLS) \> 0.1 olmamalı.  
* İlk Boyalı İçerik (FCP) \< 1.0s.  
* Sonraki Boyayla Etkileşim (INP) \< 200ms.  
* Paket boyutu izlenmeli (`rollup-plugin-visualizer` veya benzeri kullanın).  
* Görseller optimize edilmeli (WebP/AVIF) ve tembel yükleme (`lazy-load`) uygulanmalı.

**7\. Sonuç**

Notion, Linear, Raycast, Superhuman, Perplexity ve Slack'in analizi, web uygulaması tasarımının geleceği üzerinde bir uzlaşı olduğunu ortaya koymaktadır. Bu gelecek; yerel öncelikli, anlık tepki veren ve klavye merkezli bir yapıyı desteklemektedir. Bu raporda ana hatları çizilen ve **Radix UI, React Query** ve **Yay Fiziği** ile güçlendirilen React mimarisini benimseyen geliştiriciler, geleneksel SPA'ların sınırlarını aşabilir ve yüksek performanslı yerel uygulamalardan ayırt edilemeyen yazılımlar üretebilirler. Sağlanan rules.md, bu standarda ulaşmak için katı ve uygulanabilir bir plan sunarak, "faydacı lüks" kavramının sadece bir tasarım hedefi değil, bir mühendislik gerçeği olmasını sağlar.