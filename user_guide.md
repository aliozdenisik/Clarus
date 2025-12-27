# 📖 Kutsal Metinler Hibrit Arama - Kullanıcı Kılavuzu

Bu uygulama, Kuran-ı Kerim ve İncil metinleri içinde hem anlam olarak (semantik) hem de kelime bazlı (anahtar kelime) arama yapmanızı sağlar. Teknik bilgisi olmayan kullanıcılar için adım adım kurulum rehberi aşağıdadır.

## 🛠 1. Hazırlık (Gereksinimler)

Uygulamayı çalıştırmadan önce bilgisayarınızda şu yazılımların kurulu olması gerekir:

1.  **Python**: Uygulamanın çalışması için gereklidir. [python.org](https://www.python.org/downloads/) adresinden Windows için en güncel sürümü indirin ve kurun. **Kurulum sırasında "Add Python to PATH" kutucuğunu işaretlediğinizden emin olun.**
2.  **Docker Desktop**: Veritabanının (Qdrant) çalışması için gereklidir. [docker.com](https://www.docker.com/products/docker-desktop/) adresinden indirin ve kurun. Kurulumdan sonra bilgisayarınızı yeniden başlatmanız gerekebilir.
3.  **OpenRouter API Anahtarı**: Aramaların anlamını anlamak için bir yapay zeka anahtarı gerekir. [openrouter.ai](https://openrouter.ai/) adresine kayıt olun, bir miktar kredi yükleyin (birkaç dolar yeterli olacaktır) ve bir "API Key" oluşturun.

## 🚀 2. Kurulum Adımları

### A. Veritabanını Başlatın
Docker Desktop uygulamasını açın. Ardından bir terminal (PowerShell veya Komut İstemi) açın ve şu komutu yazıp Enter'a basın:
```powershell
docker run -p 6333:6333 qdrant/qdrant
```
Bu komut, verileri saklayacak olan Qdrant sistemini çalıştırır. Pencereyi kapatmayın.

### B. Uygulama Ayarlarını Yapın
Yeni bir terminal penceresi açın ve uygulamanın bulunduğu klasöre (`qdrant`) gidin. Gerekli kütüphaneleri yüklemek için şu komutu çalıştırın:
```powershell
pip install -r requirements.txt
```

Ardından, aldığınız API anahtarını bilgisayarınıza tanıtın (bu komutu her yeni terminal açtığınızda yazmanız gerekebilir):
```powershell
set OPENROUTER_API_KEY=buraya_api_anahtarinizi_yazın
```

## 📚 3. Verileri Hazırlama (İndeksleme)

Arama yapabilmek için önce kutsal metinleri sisteme yüklememiz gerekir. Bu işlem bir kez yapılır.

**Kuran-ı Kerim (Türkçe) yüklemek için:**
```powershell
python main.py index
```

**İncil (Türkçe) yüklemek için:**
```powershell
python main.py index-bible --translation turhadi
```

## 🔍 4. Arama Yapma

Artık arama yapmaya hazırsınız!

**Kuran'da arama:**
```powershell
python main.py search "sabır ve namaz"
```

**İncil'de arama:**
```powershell
python main.py search-bible "sevgi ve şefkat"
```

### İpuçları:
- **Detaylı Görünüm**: Bir ayetin tam metni ve arapçasını (Kuran için) görmek istiyorsanız komutun sonuna `-v` ekleyin:
  `python main.py search "yardımlaşma" -v`
- **Sonuç Sayısı**: Daha fazla sonuç listelemek için `--limit` kullanın:
  `python main.py search "cennet" --limit 5`

## ❓ Sorun Giderme

- **"Connection Error" (Bağlantı Hatası)**: Docker Desktop'ın açık olduğundan ve Qdrant komutunun çalıştığından emin olun.
- **"API Key Missing"**: `set OPENROUTER_API_KEY=...` komutunu doğru yazdığınızdan ve anahtarın aktif olduğundan emin olun.
- **Python Bulunamadı**: Python kurarken "Add to PATH" kutucuğunu işaretlemediyseniz Python komutları çalışmayabilir. Python'u tekrar kurup o seçeneği işaretleyin.
