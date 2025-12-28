# 📖 Kutsal Metinler Hibrit Arama - Kullanıcı Kılavuzu

Bu uygulama, Kuran-ı Kerim ve İncil metinleri içinde hem anlam olarak (semantik) hem de kelime bazlı (anahtar kelime) arama yapmanızı sağlar. Teknik bilgisi olmayan kullanıcılar için adım adım kurulum rehberi aşağıdadır.

---

## 🛠 1. Hazırlık (Gereksinimler)

Uygulamayı çalıştırmadan önce bilgisayarınızda şu yazılımların kurulu olması gerekir:

1. **Python**: [python.org](https://www.python.org/downloads/) adresinden indirin. **Kurulum sırasında "Add Python to PATH" kutucuğunu işaretleyin.**

2. **Docker Desktop**: [docker.com](https://www.docker.com/products/docker-desktop/) adresinden indirin ve kurun.

3. **OpenRouter API Anahtarı**: [openrouter.ai](https://openrouter.ai/) adresine kayıt olun ve bir API Key oluşturun.

---

## 🚀 2. Kurulum Adımları

### A. Veritabanını Başlatın
Docker Desktop'ı açın, ardından PowerShell'de:
```powershell
docker run -p 6333:6333 qdrant/qdrant
```

### B. (Opsiyonel) Graf Veritabanını Başlatın
Gelişmiş kavramsal arama için Neo4j:
```powershell
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password123 neo4j:5
```

### C. Kütüphaneleri Yükleyin
```powershell
cd qdrant
pip install -r requirements.txt
```

### D. API Anahtarını Ayarlayın
Proje klasöründeki `.env` dosyasını düzenleyin:
```
OPENROUTER_API_KEY=buraya_api_anahtarinizi_yazin
NEO4J_PASSWORD=password123
```

---

## 📚 3. Verileri Hazırlama (İndeksleme)

Arama yapabilmek için önce metinleri sisteme yüklemeniz gerekir (bir kez yapılır):

```powershell
# Kuran-ı Kerim (Türkçe)
python main.py index

# İncil (Türkçe)
python main.py index-bible --translation turhadi

# (Opsiyonel) Bilgi Grafiği Oluştur
python main.py build-graph --collection quran_tr
```

---

## 🔍 4. Arama Yapma

### Temel Aramalar

**Kuran'da arama:**
```powershell
python main.py search "sabır ve namaz"
```

**İncil'de arama:**
```powershell
python main.py search-bible "sevgi ve şefkat"
```

### Gelişmiş Arama Seçenekleri

| Seçenek | Açıklama | Örnek |
|---------|----------|-------|
| `-v` | Detaylı görünüm | `python main.py search "yardımlaşma" -v` |
| `--limit N` | N sonuç listele | `python main.py search "cennet" --limit 5` |
| `--rerank` | Sonuçları yeniden sırala | `python main.py search "sabır" --rerank` |
| `--enhance` | Sorguyu genişlet | `python main.py search "şükür" --enhance` |
| `--graph` | Graf destekli arama | `python main.py search "Hz. Musa" --graph` |
| `--no-cache` | Cache'i atla | `python main.py search "rahmet" --no-cache` |

### Örnek Kullanımlar

```powershell
# Basit arama
python main.py search "Allah'ın rahmeti"

# Detaylı sonuç
python main.py search "namaz" -v --limit 3

# En iyi sonuçlar için reranking
python main.py search "sabır nedir" --rerank

# Kavramsal ilişkileri keşfet (Neo4j gerekir)
python main.py search "Hz. İbrahim" --graph
```

---

## 🗂 5. Cache ve Graf Yönetimi

### Cache Komutları
Benzer sorguların hızlı yanıtlanması için otomatik önbellekleme:

```powershell
# Cache durumunu gör
python main.py cache-info

# Cache'i temizle
python main.py cache-clear
```

### Graf Komutları
```powershell
# Graf istatistikleri
python main.py graph-info

# Grafı yeniden oluştur
python main.py build-graph --clear
```

### Sistem Bilgisi
```powershell
python main.py info
```

---

## ❓ 6. Sorun Giderme

| Hata | Çözüm |
|------|-------|
| "Connection Error" | Docker Desktop açık mı? Qdrant çalışıyor mu? |
| "API Key Missing" | `.env` dosyasında `OPENROUTER_API_KEY` ayarlandı mı? |
| "Neo4j Error" | Neo4j container çalışıyor mu? `NEO4J_PASSWORD` doğru mu? |
| Python bulunamadı | Python kurarken "Add to PATH" işaretleyin |

### Servisleri Kontrol Etme
```powershell
# Docker container'ları listele
docker ps

# Qdrant'ı yeniden başlat
docker restart qdrant

# Neo4j'yi yeniden başlat
docker restart neo4j
```

---

## 💡 İpuçları

1. **İlk arama yavaş olabilir** - Model yüklenir. Sonraki aramalar hızlıdır.
2. **Cache sayesinde** aynı/benzer sorular anında yanıtlanır.
3. **Graf araması** ilişkili kavramları keşfetmenizi sağlar (peygamberler, olaylar, yerler).
4. **Reranking** en alakalı sonuçları en üste taşır.

---

## 📊 Performans Bilgileri

| İşlem | Süre |
|-------|------|
| İlk arama | ~2-3 saniye |
| Önbellekten arama | <0.1 saniye |
| Graf destekli arama | ~3-4 saniye |
| Reranking | +1-2 saniye |

İyi aramalar! 🔍
