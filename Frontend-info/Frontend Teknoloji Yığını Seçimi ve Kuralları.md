# **'Utilitarian Luxury' Mimari Raporu: FastAPI Tabanlı Sistemler İçin Yüksek Doğruluklu Frontend Stratejisi**

## **Yönetici Özeti**

Bu teknik araştırma raporu, mevcut bir FastAPI backend yapısı üzerine inşa edilecek, Linear ve Raycast gibi endüstri lideri araçların belirlediği "Utilitarian Luxury" (Fayda Odaklı Lüks) standartlarını karşılayan bir frontend mimarisini tanımlamak üzere hazırlanmıştır. Kıdemli UI/UX Researcher ve Design Architect perspektifiyle hazırlanan bu doküman, yalnızca görsel estetiği değil, aynı zamanda etkileşim derinliğini, algısal performansı ve geliştirme sürecinin yapay zeka (AI) ile sürdürülebilirliğini merkeze almaktadır.

Analizler, "hazır component kullanımı" ve "AI tarafından sürdürülebilirlik" kriterlerinin, teknoloji seçiminde belirleyici faktörler olduğunu göstermektedir. Bu bağlamda, React ve Vue ekosistemleri arasında yapılan kapsamlı karşılaştırma sonucunda, **Next.js (App Router)**, **TypeScript**, **Tailwind CSS v4**, **shadcn/ui** ve **TanStack Query** bileşenlerinden oluşan teknoloji yığınının, hedeflenen kullanıcı deneyimi ve mimari sağlamlık için en uygun çözüm olduğu belirlenmiştir. Bu rapor, seçilen yığının gerekçelerini, uygulama stratejilerini ve geliştirme ekibi için oluşturulan rules.md dosyasını detaylandırmaktadır.

## ---

**1\. Giriş: 'Utilitarian Luxury' Kavramının Dekonstrüksiyonu**

"Utilitarian Luxury" (Fayda Odaklı Lüks), modern yazılım tasarımında ortaya çıkan ve Linear, Raycast, Superhuman gibi araçlarla özdeşleşen bir tasarım felsefesidir. Bu yaklaşım, yazılımın bir araç (utility) olarak sahip olması gereken ham verimliliği, lüks tüketici ürünlerinin (luxury) estetik ve dokunsal rafineliği ile birleştirir.1 Bir Kıdemli UI/UX Researcher olarak bu kavramı analiz ettiğimizde, temelinde "beklemenin yokluğu" ve "deterministik etkileşim" yattığını görürüz.

### **1.1 Gecikme Yasası ve Algısal Hız**

Linear benzeri uygulamaların kullanıcıda yarattığı "sihirli" hissin temelinde, ağ gecikmelerinin (latency) kullanıcı arayüzünden tamamen soyutlanması yatar. Geleneksel web uygulamaları "İstek \-\> Bekle \-\> Yanıt \-\> Güncelle" döngüsüyle çalışırken, Utilitarian Luxury standartları "Eylem \-\> Güncelle \-\> Arka Planda İstek" döngüsünü zorunlu kılar.2 Bu, frontend mimarisinin sunucu yanıtını beklemeden arayüzü güncellediği "Optimistic UI" (İyimser Arayüz) desenlerinin agresif bir şekilde kullanılmasını gerektirir. Kullanıcı bir görevi "Tamamlandı" olarak işaretlediğinde, arayüz milisaniyeler içinde tepki vermeli, sunucu iletişimi ise tamamen asenkron bir detay olarak kalmalıdır.

### **1.2 Bilgi Yoğunluğu ve Görsel Gürültü Yönetimi**

Bu estetik anlayış, bilgiyi saklamak yerine organize etmeyi tercih eder. Tipografi, boşluk kullanımı ve renk paleti, kullanıcının bilişsel yükünü artırmadan maksimum veriyi sunmak üzere optimize edilmelidir. Bu durum, kullanılan UI kütüphanesinin (UI Kit) son derece esnek, özelleştirilebilir ve "opinionated" (kendi kurallarını dayatan) stil dayatmalarından arınmış olmasını gerektirir.

## ---

**2\. Framework Karşılaştırması: React/Next.js vs. Vue/Nuxt**

Mevcut FastAPI backend ile entegre edilecek frontend teknolojisini belirlerken, "Vue 3 zorunlu değil" parametresi ışığında, React ve Vue ekosistemlerini "Utilitarian Luxury" ve "AI Sürdürülebilirliği" kriterlerine göre derinlemesine analiz etmek gerekmektedir.5

### **2.1 React Ekosistemi (Next.js): Endüstriyel Standart**

React, özellikle Next.js framework'ü ile birleştiğinde, "ağır" ve yüksek etkileşimli uygulamaların baskın gücü konumundadır. Linear'ın kendisi React üzerine inşa edilmiştir 6, ve Raycast eklentileri de React/TypeScript tabanlıdır.7

* **Etkileşim Sadakati (Interaction Fidelity):** "Luxury" hissini yaratan fiziksel tabanlı animasyonlar (örneğin, bir liste elemanının silinirken diğerlerinin yumuşakça kayması), React ekosistemine özgü kütüphanelerle (özellikle framer-motion) çok daha kolay hayata geçirilir. Vue'nun \<Transition\> bileşenleri güçlüdür ancak framer-motion'ın sunduğu "layout projection" (düzen projeksiyonu) yetenekleri, karmaşık arayüzlerdeki durum geçişlerini yönetmek için benzersiz bir avantaj sağlar.8  
* **AI Sürdürülebilirliği (AI Sustainability):** Büyük Dil Modelleri (LLM), GitHub üzerindeki açık kaynak kodlarla eğitilmiştir. React, sayısal üstünlüğü nedeniyle eğitim setlerinde daha fazla yer kaplar. Bu durum, AI araçlarının (Cursor, GitHub Copilot, v0) React kodunu, Vue koduna kıyasla daha yüksek doğrulukla, daha az "halüsinasyon" görerek ve daha modern pattern'leri kullanarak üretmesini sağlar.9 Özellikle Vercel'in geliştirdiği AI SDK'lar, React ve Next.js için "first-class" destek sunarken, diğer framework'ler genellikle takipçi konumundadır.11  
* **Hazır Bileşen Ekosistemi (Shadcn/ui Etkisi):** Modern web geliştirmeyi dönüştüren shadcn/ui, React için yazılmıştır. Bu kütüphane, bir npm paketi değil, kopyalanabilir bir kod tabanıdır. Vue portları (shadcn-vue) mevcut olsa da, orijinal kütüphanenin güncellemelerini, topluluk eklentilerini ve AI araçlarıyla uyumluluğunu (örneğin v0.dev) doğrudan React sürümü üzerinden takip etmek, mimari borçlanmayı azaltır.13

### **2.2 Vue Ekosistemi (Nuxt): İlerici Alternatif**

Vue 3, Composition API ile React Hooks'a benzer, hatta bazı durumlarda daha temiz bir reaktivite modeli sunar. Nuxt, geliştirici deneyimi (DX) açısından Next.js ile yarışır, hatta bazı konfigürasyon kolaylıklarında öne geçer.5

* **Shadcn-Vue Durumu:** shadcn-vue, React versiyonunun başarılı bir portudur ve özellik paritesi yüksektir.15 Ancak, bir "Design Architect" için kritik olan nokta, orijinale olan bağımlılıktır. Ana shadcn/ui deposuna yeni bir "Chart" bileşeni eklendiğinde, Vue portunun bunu uyarlamasını beklemek veya manuel olarak port etmek gerekir. Bu gecikme, hızlı iterasyon gerektiren projelerde bir risk faktörüdür.  
* **AI Kod Üretiminde Sürtünme:** LLM'ler Vue kodu üretirken bazen Options API ile Composition API'yi karıştırabilir veya Nuxt'a özgü auto-import özelliklerini tam bağlamıyla anlayamayabilir.9 React'in daha katı bileşen sınırları ve JSX'in yaygınlığı, AI asistanları için daha tutarlı bir hedef oluşturur.  
* **Kritik Kütüphane Eksikliği:** Linear benzeri bir deneyim için hayati önem taşıyan cmdk (komut paleti) kütüphanesinin orijinal ve en performanslı versiyonu React tabanlıdır. Vue için alternatifler (vue-command-palette) mevcuttur ancak bakım sıklığı ve topluluk desteği açısından React versiyonunun gerisindedir.16

### **2.3 Karar: Neden React/Next.js?**

"Utilitarian Luxury" standardını yakalamak için gereken **yüksek sadakatli etkileşim** (Framer Motion), **merkezi komut yönetimi** (cmdk) ve **AI destekli geliştirme hızı** (v0, AI SDK), ibreyi kesin olarak **React ve Next.js** ekosistemine çevirmektedir. Vue 3 mükemmel bir framework olsa da, Linear ve Raycast'in belirlediği standartlar React ekosisteminde doğmuş ve olgunlaşmıştır. Bu standartları Vue ile yeniden üretmek, akıntıya karşı kürek çekmek anlamına gelecektir. Bu nedenle, projenin frontend mimarisi **Next.js 15 (App Router)** üzerine kurulacaktır.

## ---

**3\. UI Mimarisi: 'Headless' ve 'Copy-Paste' Devrimi**

Geleneksel UI kütüphaneleri (Material UI, Ant Design), geliştiriciyi belirli bir tasarım diline hapseder. "Utilitarian Luxury" ise tam tersine, tamamen özelleştirilmiş, marka kimliğiyle bütünleşmiş bir arayüz talep eder. Bu noktada, "Headless" (Stilsiz) bileşenler ve "Copy-Paste" (Kopyala-Yapıştır) mimarisi devreye girer.

### **3.1 Shadcn/ui Paradigması ve Sahiplik İlkesi**

Seçilen UI Kit stratejisi **shadcn/ui** olacaktır. Bu seçim, "hazır component kullanma" kriterini karşılarken, "AI tarafından sürdürülebilirlik" kriterini de en üst düzeye çıkarır.13

* **Kod Sahipliği:** Shadcn/ui bir node\_modules bağımlılığı değildir. Bileşenler (Button, Dialog, Input) projenizin components/ui klasörüne kaynak kod olarak eklenir. Bu, mimarın bileşen üzerinde tam kontrole sahip olmasını sağlar. Örneğin, bir input alanına Raycast tarzı bir "sağ taraf aksiyon ikonu" eklemek istediğinizde, kütüphanenin API'siyle savaşmak yerine doğrudan bileşenin kodunu düzenlersiniz.19  
* **AI Modifiye Edilebilirliği:** AI asistanları (Cursor gibi), kaynak kodu projenin içinde olan bileşenleri okuyup anlamakta çok daha başarılıdır. Kapalı kutu bir kütüphanenin (MUI) dokümantasyonunu hatırlamaya çalışmak yerine, AI doğrudan components/ui/button.tsx dosyasını analiz ederek, stil veya mantık değişikliğini hatasız bir şekilde uygulayabilir.  
* **Radix UI Temeli:** Shadcn/ui, tabanda **Radix UI** kullanır. Radix, erişilebilirlik (A11y), klavye navigasyonu ve odak yönetimi gibi zorlu konuları çözerken stil dayatmaz. Bu, "Utilitarian" kısmını (işlevsellik) Radix'in, "Luxury" kısmını (görünüm) ise Tailwind CSS ve bizim tasarım kararlarımızın üstlenmesini sağlar.20

### **3.2 Tailwind CSS v4 ve CSS Değişkenleri**

Stil motoru olarak **Tailwind CSS v4** kullanılacaktır. V4 sürümü, JavaScript tabanlı konfigürasyon dosyalarından (tailwind.config.js) uzaklaşarak, yerel CSS değişkenlerine (@theme) dayalı bir yapıya geçmiştir.21

* **Dinamik Tema Yönetimi:** Linear benzeri uygulamalarda sıkça görülen "kullanıcı tanımlı tema" veya "takım bazlı renk paleti" özellikleri, CSS değişkenleri sayesinde çalışma zamanında (runtime) performans kaybı olmadan yönetilebilir.  
* **Okunabilirlik:** Renklerin ve tasarım token'larının CSS içinde tanımlanması, hem geliştiriciler hem de AI araçları için daha doğal bir bağlam oluşturur.

### **3.3 İkonografi ve Tipografi**

"Utilitarian Luxury" arayüzlerde ikonlar, metin kadar önemlidir. **Lucide React**, tutarlı çizgi kalınlıkları, temiz geometrisi ve geniş kütüphanesiyle bu estetik için endüstri standardıdır.23 Tipografi için, sistem fontlarına (San Francisco, Inter) öncelik veren, okuma hızını artıran bir font yığını (font stack) kurgulanacaktır.24

## ---

**4\. Backend Entegrasyonu: FastAPI ve Tür Güvenliği**

Frontend'in lüks hissettirmesi için hatasız çalışması gerekir. Bu güvenilirlik, backend (FastAPI) ile frontend (React) arasındaki veri kontratının sağlamlığına bağlıdır.

### **4.1 'Schema-First' Yaklaşımı ve Kod Üretimi**

FastAPI'nin en güçlü özelliği, Pydantic modellerinden otomatik olarak **OpenAPI (Swagger)** şeması üretmesidir.26 Biz bu şemayı, frontend geliştirme sürecinin merkezine koyacağız. Manuel olarak fetch fonksiyonları yazmak veya TypeScript arayüzlerini elle güncellemek, "sürdürülebilir" değildir ve insan hatasına açıktır.

Kullanılacak araç: **@hey-api/openapi-ts** (veya alternatif olarak orval).

Bu araçlar, FastAPI'nin sunduğu openapi.json dosyasını tarayarak şunları otomatik olarak üretir:

1. **TypeScript Interface'leri:** Backend'deki Pydantic modellerinin birebir karşılığı olan TypeScript tipleri. Backend'de bir alan Optional\[str\] ise, frontend'de otomatik olarak string | undefined olur.27  
2. **TanStack Query Hook'ları:** Her endpoint için useQuery ve useMutation hook'larını otomatik üretir (örneğin: useGetIssues, useCreateProject).

Bu akış, "AI tarafından sürdürülebilirlik" için kritiktir. AI asistanına "Yeni bir 'Issue' oluşturma formu yap" dediğinizde, AI projedeki useCreateIssue hook'unu ve Issue tipini analiz ederek, form validasyonunu (Zod) ve API çağrısını %100 tip güvenliğiyle yazabilir.

### **4.2 Veri Doğrulama: Zod ve Pydantic Uyumu**

Frontend formlarında (React Hook Form), validasyon şeması olarak **Zod** kullanılacaktır. Zod, yapısı itibariyle Pydantic'e çok benzer ve TypeScript ile mükemmel uyum sağlar. Gelişmiş senaryolarda, Pydantic modellerinden otomatik Zod şemaları üreten araçlar da kullanılabilir, ancak manuel eşleşme genellikle AI desteğiyle daha esnek yönetilir.

## ---

**5\. Durum Yönetimi ve Optimistic UI**

Linear hissini yakalamanın anahtarı, ağ isteklerinin kullanıcı arayüzünü bloke etmesine izin vermemektir.

### **5.1 TanStack Query (React Query) v5**

Veri çekme, önbellekleme ve senkronizasyon için tartışmasız lider **TanStack Query**'dir.28 Ancak bu projede TanStack Query, basit bir veri çekme aracından öte, bir "uygulama durumu yöneticisi" olarak kullanılacaktır.

* **Otomatik Arka Plan Güncellemeleri:** Kullanıcı pencereye odaklandığında (window focus) verilerin sessizce güncellenmesi, verinin her zaman taze olduğu hissini yaratır.  
* **Yapısal Paylaşım (Structural Sharing):** Gereksiz render'ları önleyerek uygulamanın tepkiselliğini korur.

### **5.2 Optimistic Updates (İyimser Güncellemeler) Stratejisi**

Linear klonlarında mutasyonlar (veri değiştirme işlemleri) şu pattern ile yazılmalıdır 30:

1. **onMutate:** Devam eden sorguları iptal et. Mevcut verinin bir kopyasını al (snapshot). Hedeflenen değişikliği (örneğin bir görevin tamamlandı olarak işaretlenmesi) anında önbelleğe (cache) uygula. UI anında güncellenir.  
2. **onError:** Eğer sunucu hatası dönerse, alınan snapshot'ı geri yükle (rollback) ve kullanıcıya bildir (Sonner ile).  
3. **onSettled:** Başarılı da olsa başarısız da olsa, verinin sunucudaki en güncel halini almak için sorguyu geçersiz kıl (invalidate) ve arka planda yeniden çek.

Bu döngü, kullanıcının eyleminin sonucunu beklemesini ortadan kaldırır.

## ---

**6\. Etkileşim Mühendisliği ve Kritik Kütüphaneler**

"Utilitarian Luxury" standartlarına ulaşmak için, standart bileşenlerin ötesine geçen özel etkileşim kütüphaneleri gereklidir.

### **6.1 Komut Merkezi: cmdk**

Uygulamanın kalbinde yer alan Command+K menüsü için, shadcn/ui'ın da temel aldığı **cmdk** kütüphanesi kullanılacaktır.17

* **Virtualization:** Binlerce komut veya veri satırı olsa bile performans kaybı yaşatmaz.  
* **Filtreleme:** Hatalı yazımları tolere eden (fuzzy search) gelişmiş filtreleme algoritmaları sunar.  
* **Composable:** Tamamen stilsizdir, bu sayede Tailwind ile üzerine Linear tarzı "buzlu cam" (backdrop-blur) efektleri ve animasyonlar eklenebilir.

### **6.2 Bildirimler: Sonner**

Geleneksel "Toast" kütüphaneleri genellikle hantal ve çirkindir. **Sonner**, Emil Kowalski tarafından geliştirilen, "opinionated" (belirli bir görüşe sahip) ve yüksek estetik standartlara sahip bir kütüphanedir.32

* **Stacking:** Bildirimler üst üste yığılır, bu da ekranı kaplamadan kullanıcının tarihçeyi görmesini sağlar.  
* **Promise Desteği:** Bir işlem başladığında "Yükleniyor" ikonunu gösterip, işlem bittiğinde yumuşak bir animasyonla "Başarılı" ikonuna dönüşmesi, Optimistic UI ile mükemmel uyum sağlar.

### **6.3 Veri Tabloları: TanStack Table**

Linear'ın listeleri karmaşık sıralama, filtreleme ve çoklu seçim özelliklerine sahiptir. **TanStack Table**, "headless" yapısıyla bu karmaşıklığı yönetirken, DOM üzerindeki kontrolü tamamen bize bırakır.34 Shadcn/ui içindeki DataTable bileşeni, bu kütüphane üzerine kuruludur ve özelleştirilebilir bir başlangıç noktası sunar.

## ---

**7\. AI Sürdürülebilirliği: Kod Üretim Kuralları**

Seçilen teknolojilerin ötesinde, bu teknolojilerin *nasıl* kullanılacağı, AI asistanlarının verimliliğini belirler. Proje kök dizinine eklenecek rules.md dosyası, AI modeline (Cursor/Windsurf) projenin mimari kısıtlamalarını ve kodlama standartlarını öğreten bir "Sistem Talimatı" (System Prompt) görevi görecektir.

### **rules.md Dosyası**

Aşağıdaki içerik, projenin kök dizinine rules.md olarak kaydedilmelidir. Bu dosya, AI asistanlarının projeye özgü "Utilitarian Luxury" standartlarına uymasını garanti altına alır.

# **Project Rules & Architecture Guidelines**

## **1\. Design Philosophy: Utilitarian Luxury**

This project adheres to the "Linear/Raycast" aesthetic.

* **Speed is a Feature:** All user interactions must provide immediate feedback. Use Optimistic UI for all mutations.  
* **Keyboard First:** Primary actions must be accessible via Command Menu (Cmd+K) or keyboard shortcuts.  
* **Density:** Information density should be high but legible. Use smaller text sizes (13px/14px) with careful spacing.  
* **Micro-interactions:** Use framer-motion for subtle layout transitions. No jarring jumps.

## **2\. Tech Stack & Standards**

* **Framework:** Next.js 15 (App Router). Use Server Components by default.  
* **Styling:** Tailwind CSS v4. Use CSS variables for theming (e.g., var(--color-primary)).  
* **Components:** shadcn/ui. Do NOT install external UI libraries. Use npx shadcn@latest add \[component\].  
* **Icons:** lucide-react.  
* **State:** TanStack Query for server state. nuqs for URL search params state. Zustand for complex global client state.

## **3\. Code Generation Rules (AI Instructions)**

### **A. Component Composition**

* Always use shadcn/ui primitives.  
* When creating new UI elements, compose them using cva (Class Variance Authority) for variant management.  
* Ensure all interactive elements have focus states (ring-offset-background, focus-visible:ring-2).

### **B. FastAPI Integration**

* **Do not write manual fetch functions.** Use the generated hooks from @/lib/api.  
* If a new endpoint is added to FastAPI:  
  1. Remind the user to run npm run codegen.  
  2. Use the generated types for the response data.  
* **Optimistic Updates:** When writing a mutation:  
  * Use onMutate to cancel queries and snapshot context.  
  * Update the cache optimistically using queryClient.setQueryData.  
  * Implement onError rollback and onSettled invalidation.

### **C. Styling & Animation**

* Use tailwind-merge (cn utility) for all class merging.  
* For animations, use framer-motion. Prefer layout prop for smooth list reordering.  
* Use AnimatePresence for exit animations.

### **D. File Structure**

* **Colocation:** Keep related components, hooks, and types in the same feature folder (e.g., app/(dashboard)/issues/\_components).  
* **Server Actions:** Put server actions in \_actions.ts files within the feature folder.

### **E. AI & Sustainability**

* Write self-documenting code.  
* Prefer small, composable components over large monolithic files.  
* If a complex logic block is generated, add a comment explaining the "why".

## **4\. Anti-Patterns (Do Not Use)**

* ❌ Do not use useEffect for data fetching. Use useQuery.  
* ❌ Do not use axios. Use standard fetch or the generated client.  
* ❌ Do not use default HTML alert() or confirm(). Use Sonner toast or Dialog component.  
* ❌ Do not create "wrappers" around shadcn components unless strictly necessary for repeated logic.

## ---

**8\. Detaylı Teknoloji Yığını ve Gerekçelendirme Tablosu**

Aşağıdaki tablo, seçilen her bir teknolojinin "Utilitarian Luxury" felsefesine ve teknik gereksinimlere nasıl hizmet ettiğini özetlemektedir.

| Kategori | Teknoloji | Seçim Gerekçesi ve "Luxury" Katkısı |
| :---- | :---- | :---- |
| **Framework** | **Next.js 15 (App Router)** | React Server Components (RSC) ile sunucu yükünü azaltır, Vercel AI SDK ile yerel entegrasyon sunar. Performans ve SEO optimizasyonu standarttır. |
| **Dil** | **TypeScript** | FastAPI Pydantic modelleri ile %100 tip güvenliği sağlar. Büyük kod tabanlarında yeniden düzenleme (refactoring) güvenliği sunar. |
| **Stil Motoru** | **Tailwind CSS v4** | CSS değişkenleri tabanlı yeni yapısıyla çalışma zamanı temalandırmayı kolaylaştırır. "Utility-first" yaklaşımı, AI'ın stil üretmesini hızlandırır. |
| **UI Kütüphanesi** | **shadcn/ui** | Bileşen sahipliği sağlar. Radix UI tabanlı olduğu için erişilebilirlik (A11y) sorunsuzdur. Tamamen özelleştirilebilir. |
| **State Yönetimi** | **TanStack Query v5** | Optimistic UI, arka plan senkronizasyonu ve sunucu durumu yönetimi için endüstri standardıdır. |
| **Komut Paleti** | **cmdk** | Linear tarzı Cmd+K menüsü için en performanslı, stilsiz ve erişilebilir React çözümüdür. |
| **Bildirimler** | **Sonner** | "Stackable" (yığılabilir) yapısı ve estetik animasyonlarıyla, kullanıcıyı rahatsız etmeden bilgilendiren en iyi toast kütüphanesidir. |
| **Validasyon** | **Zod** | TypeScript ile tam uyumlu şema validasyonu. Pydantic mantığına çok yakındır. |
| **İkonlar** | **Lucide React** | Tutarlı çizgi kalınlıkları ve minimalist tasarımıyla "Utilitarian" estetiğine en uygun ikon setidir. |
| **Animasyon** | **Framer Motion** | Deklaratif animasyon API'si ile karmaşık arayüz geçişlerini (layout animations) lüks bir hisle sunar. |
| **API Entegrasyonu** | **@hey-api/openapi-ts** | FastAPI'den otomatik tip güvenli istemci (client) üretimi. Manuel API yazımını ortadan kaldırır. |

## ---

**9\. Sonuç ve Uygulama Yol Haritası**

Yapılan analizler, "Utilitarian Luxury" standardının, hazır UI kütüphanelerinin (MUI, AntD) konfor alanından çıkılarak, "Headless" primitiflerin (Radix, TanStack) üzerine inşa edilen özel bir mimariyle mümkün olduğunu göstermektedir. React/Next.js ekosistemi, bu mimariyi destekleyen araçların olgunluğu ve yapay zeka ile entegrasyon kapasitesi bakımından Vue ekosistemine göre belirgin bir üstünlüğe sahiptir.

Kıdemli Mimar olarak önerilen uygulama yol haritası şöyledir:

1. **Başlangıç:** create-next-app ile proje iskeletini kurun ve rules.md dosyasını kök dizine yerleştirin.  
2. **Temel Kurulum:** shadcn/ui başlatın (New York stili, daha kompakt ve profesyoneldir) ve temel bileşenleri (Button, Input, Dropdown) ekleyin.  
3. **Lüks Katmanı:** cmdk, sonner ve framer-motion kütüphanelerini entegre edin. Global bir Cmd+K sağlayıcısı (Context) oluşturun.  
4. **Backend Bağlantısı:** FastAPI'den openapi.json çıktısını alın ve @hey-api/openapi-ts ile ilk istemci kodunu (client generation) oluşturun.  
5. **Geliştirme Döngüsü:** AI asistanınızı (Cursor/Windsurf) rules.md dosyasını okuması için yönlendirin ve ilk özelliği (örneğin "Proje Listeleme ve Oluşturma") Optimistic UI prensipleriyle geliştirmeye başlayın.

Bu mimari, yalnızca bugünün gereksinimlerini karşılamakla kalmayıp, geleceğin yapay zeka destekli geliştirme süreçlerine de tam uyumlu, sürdürülebilir ve yüksek performanslı bir temel sunmaktadır.

---

**Rapor Sonu**

*22 Ocak 2026*

#### **Works cited**

1. How to Use Linear: Setup, Best Practices, and Hidden Features Guide \- Morgen, accessed January 22, 2026, [https://www.morgen.so/blog-posts/linear-project-management](https://www.morgen.so/blog-posts/linear-project-management)  
2. A Guide to Building Linear-like App For Developers \- DhiWise, accessed January 22, 2026, [https://www.dhiwise.com/post/build-your-own-linear-app-developers-guide](https://www.dhiwise.com/post/build-your-own-linear-app-developers-guide)  
3. Raycast \- Your shortcut to everything, accessed January 22, 2026, [https://www.raycast.com/](https://www.raycast.com/)  
4. Stacks \- Raycast Store, accessed January 22, 2026, [https://www.raycast.com/sourabh\_rathour/stacks](https://www.raycast.com/sourabh_rathour/stacks)  
5. Choosing Tech Stack in 2025: A Practical Guide \- DEV Community, accessed January 22, 2026, [https://dev.to/dimeloper/choosing-tech-stack-in-2025-a-practical-guide-4gll](https://dev.to/dimeloper/choosing-tech-stack-in-2025-a-practical-guide-4gll)  
6. Linear Tech Stack | Himalayas, accessed January 22, 2026, [https://himalayas.app/companies/linear/tech-stack](https://himalayas.app/companies/linear/tech-stack)  
7. Raycast Tech Stack | Himalayas, accessed January 22, 2026, [https://himalayas.app/companies/raycast/tech-stack](https://himalayas.app/companies/raycast/tech-stack)  
8. Rebuilding Linear.app's website with Next.js, Tailwind and Framer Motion. \- GitHub, accessed January 22, 2026, [https://github.com/frontendfyi/rebuilding-linear.app](https://github.com/frontendfyi/rebuilding-linear.app)  
9. React or Vue for AI based project? : r/vuejs \- Reddit, accessed January 22, 2026, [https://www.reddit.com/r/vuejs/comments/1nzdw9g/react\_or\_vue\_for\_ai\_based\_project/](https://www.reddit.com/r/vuejs/comments/1nzdw9g/react_or_vue_for_ai_based_project/)  
10. The Best Frontend AI Tools Developers Should Know \- Plain Concepts, accessed January 22, 2026, [https://www.plainconcepts.com/the-best-frontend-ai-tools-developers-should-know/](https://www.plainconcepts.com/the-best-frontend-ai-tools-developers-should-know/)  
11. AI SDK by Vercel, accessed January 22, 2026, [https://ai-sdk.dev/docs/introduction](https://ai-sdk.dev/docs/introduction)  
12. Reference: AI SDK UI, accessed January 22, 2026, [https://ai-sdk.dev/docs/reference/ai-sdk-ui](https://ai-sdk.dev/docs/reference/ai-sdk-ui)  
13. shadcn/ui vs Untitled UI: The Ultimate Comparison Guide for Modern UI Development | by Jeff Shomali | Medium, accessed January 22, 2026, [https://medium.com/@jeffshomali/shadcn-ui-vs-untitled-ui-the-ultimate-comparison-guide-for-modern-ui-development-91ac228d7e68](https://medium.com/@jeffshomali/shadcn-ui-vs-untitled-ui-the-ultimate-comparison-guide-for-modern-ui-development-91ac228d7e68)  
14. Why shadcn/ui is Different | Vercel Academy, accessed January 22, 2026, [https://vercel.com/academy/shadcn-ui/why-shadcn-ui-is-different](https://vercel.com/academy/shadcn-ui/why-shadcn-ui-is-different)  
15. Shadcn Vue – Elegant, Customizable UI Components for Modern Vue Apps, accessed January 22, 2026, [https://dev.to/jacobandrewsky/shadcn-vue-elegant-customizable-ui-components-for-modern-vue-apps-cd](https://dev.to/jacobandrewsky/shadcn-vue-elegant-customizable-ui-components-for-modern-vue-apps-cd)  
16. vue-command-palette \- NPM, accessed January 22, 2026, [https://www.npmjs.com/package/vue-command-palette](https://www.npmjs.com/package/vue-command-palette)  
17. dip/cmdk: Fast, unstyled command menu React component. \- GitHub, accessed January 22, 2026, [https://github.com/dip/cmdk](https://github.com/dip/cmdk)  
18. AI-First UIs: Why shadcn/ui's Model is Leading the Pack \- Refine dev, accessed January 22, 2026, [https://refine.dev/blog/shadcn-blog/](https://refine.dev/blog/shadcn-blog/)  
19. Introduction \- shadcn/vue, accessed January 22, 2026, [https://www.shadcn-vue.com/docs/introduction](https://www.shadcn-vue.com/docs/introduction)  
20. Shadcn/UI just overtook Material UI\! : r/react \- Reddit, accessed January 22, 2026, [https://www.reddit.com/r/react/comments/1o20sep/shadcnui\_just\_overtook\_material\_ui/](https://www.reddit.com/r/react/comments/1o20sep/shadcnui_just_overtook_material_ui/)  
21. Tailwind CSS v4.0, accessed January 22, 2026, [https://tailwindcss.com/blog/tailwindcss-v4](https://tailwindcss.com/blog/tailwindcss-v4)  
22. Theme variables \- Core concepts \- Tailwind CSS, accessed January 22, 2026, [https://tailwindcss.com/docs/theme](https://tailwindcss.com/docs/theme)  
23. Code Block \- AI SDK, accessed January 22, 2026, [https://ai-sdk.dev/elements/components/code-block](https://ai-sdk.dev/elements/components/code-block)  
24. font \- CSS \- MDN Web Docs \- Mozilla, accessed January 22, 2026, [https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/font)  
25. System font stack CSS organized by typeface classification for every modern operating system \- GitHub, accessed January 22, 2026, [https://github.com/system-fonts/modern-font-stacks](https://github.com/system-fonts/modern-font-stacks)  
26. Design, Generate, Deploy: Our Contract-First API Strategy with FastAPI and OpenAPI | by Evelyne Groen | Dec, 2025 | malt-engineering, accessed January 22, 2026, [https://blog.malt.engineering/design-generate-deploy-our-contract-first-api-strategy-with-fastapi-and-openapi-15bb3e855dff](https://blog.malt.engineering/design-generate-deploy-our-contract-first-api-strategy-with-fastapi-and-openapi-15bb3e855dff)  
27. TanStack Query v5 Plugin \- Hey API, accessed January 22, 2026, [https://heyapi.dev/openapi-ts/plugins/tanstack-query](https://heyapi.dev/openapi-ts/plugins/tanstack-query)  
28. \[Architecture\] @tanstack/react-query best practices · Issue \#96 \- GitHub, accessed January 22, 2026, [https://github.com/reboottime/ReactDevEveryday/issues/96](https://github.com/reboottime/ReactDevEveryday/issues/96)  
29. TanStack Query Community Resources, accessed January 22, 2026, [https://tanstack.com/query/v5/docs/community-resources](https://tanstack.com/query/v5/docs/community-resources)  
30. Concurrent Optimistic Updates in React Query | TkDodo's blog, accessed January 22, 2026, [https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query](https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query)  
31. Optimistic Updates | TanStack Query React Docs, accessed January 22, 2026, [https://tanstack.com/query/v4/docs/react/guides/optimistic-updates](https://tanstack.com/query/v4/docs/react/guides/optimistic-updates)  
32. Shadcn Sonner, accessed January 22, 2026, [https://www.shadcn.io/ui/sonner](https://www.shadcn.io/ui/sonner)  
33. Sonner — The Toast Library That Made My UI Feel Alive | by Subash Natrayan R M | Medium, accessed January 22, 2026, [https://medium.com/@subashnatrayan28/%EF%B8%8F-sonner-the-toast-library-that-made-my-ui-feel-alive-cf77452eb2c8](https://medium.com/@subashnatrayan28/%EF%B8%8F-sonner-the-toast-library-that-made-my-ui-feel-alive-cf77452eb2c8)  
34. Next.js & shadcn/ui Admin Dashboard Template \- Vercel, accessed January 22, 2026, [https://vercel.com/new/templates/next.js/next-js-and-shadcn-ui-admin-dashboard](https://vercel.com/new/templates/next.js/next-js-and-shadcn-ui-admin-dashboard)