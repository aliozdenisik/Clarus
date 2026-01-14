# 🔐 Güvenlik Politikası

Sacred Texts Ultimate RAG Search projesinin güvenlik politikası ve en iyi uygulamaları.

---

## 📋 İçindekiler

- [API Anahtarı Güvenliği](#-api-anahtarı-güvenliği)
- [Ortam Değişkenleri](#-ortam-değişkenleri)
- [Qdrant Veritabanı Güvenliği](#-qdrant-veritabanı-güvenliği)
- [Veri Güvenliği](#-veri-güvenliği)
- [Güvenlik Açığı Bildirme](#-güvenlik-açığı-bildirme)
- [Desteklenen Sürümler](#-desteklenen-sürümler)

---

## 🔑 API Anahtarı Güvenliği

### Gerekli API Anahtarları

| Servis | Değişken Adı | Kullanım Alanı |
|--------|--------------|----------------|
| OpenRouter | `OPENROUTER_API_KEY` | LLM sorgulama (Gemini) |
| SiliconFlow | `SILICONFLOW_API_KEY` | Reranker (Qwen3) |

### ⚠️ Önemli Kurallar

1. **API anahtarlarını asla commit etmeyin**
   ```bash
   # .gitignore'da bu satırın olduğundan emin olun
   .env
   ```

2. **Anahtarları kodda hardcode etmeyin**
   ```python
   # ❌ YANLIŞ
   api_key = "sk-abc123..."
   
   # ✅ DOĞRU
   api_key = os.getenv("OPENROUTER_API_KEY")
   ```

3. **Düzenli anahtar rotasyonu yapın**
   - Her 90 günde bir anahtarları yenileyin
   - Şüpheli aktivite görürseniz hemen değiştirin

---

## 🌍 Ortam Değişkenleri

### `.env` Dosya Şablonu

```env
# === API Anahtarları ===
OPENROUTER_API_KEY=your-openrouter-key
SILICONFLOW_API_KEY=your-siliconflow-key

# === Opsiyonel Ayarlar ===
QDRANT_HOST=localhost
QDRANT_PORT=6333
# QDRANT_API_KEY=your-qdrant-api-key  # Aktifse kullanın
```

### Dosya İzinleri

```bash
# .env dosyasını sadece sahibi okuyabilsin
chmod 600 .env
```

---

## 🗄️ Qdrant Veritabanı Güvenliği

### Yerel Geliştirme

Varsayılan Docker kurulumu güvenlik olmadan çalışır:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Üretim Ortamı İçin Öneriler

1. **API Key Aktifleştirin**
   ```yaml
   # config.yaml
   service:
     api_key: "güçlü-rastgele-anahtar-üretin"
   ```

2. **TLS/HTTPS Kullanın**
   ```bash
   docker run -p 6333:6333 \
     -v $(pwd)/tls:/qdrant/tls:ro \
     -e QDRANT__SERVICE__ENABLE_TLS=true \
     qdrant/qdrant
   ```

3. **Ağ İzolasyonu**
   - Qdrant portunu dışarıya açmayın
   - Docker network veya VPN kullanın

4. **Düzenli Yedekleme**
   ```bash
   # Snapshot oluştur
   curl -X POST 'http://localhost:6333/collections/quran_tr/snapshots'
   ```

---

## 📊 Veri Güvenliği

### Depolanan Veriler

| Koleksiyon | İçerik | Hassasiyet |
|------------|--------|------------|
| `quran_tr` | Kuran ayetleri (Türkçe) | Düşük |
| `quran_tr_semantic_chunks` | Semantik gruplar | Düşük |
| `bible_kjva` | İncil (KJVA) | Düşük |
| `bible_kjva_semantic_chunks` | Semantik gruplar | Düşük |

### Cache Güvenliği

- Cache dosyaları `cache/` dizininde saklanır
- Hassas sorgu verileri içerebilir
- Paylaşılan sistemlerde dikkatli olun

```bash
# Cache temizleme
python main.py cache-clear
```

---

## 🚨 Güvenlik Açığı Bildirme

### Bildirme Süreci

1. **Gizli Tutun**: Açığı kamuya açıklamayın
2. **Detaylı Raporlayın**:
   - Açığın tanımı
   - Yeniden üretme adımları
   - Potansiyel etki
   - Varsa çözüm önerisi

3. **İletişim**:
   - GitHub Issues üzerinden **gizli** issue açın
   - Veya proje sahibine doğrudan ulaşın

### Yanıt Süreci

| Aşama | Süre |
|-------|------|
| İlk yanıt | 48 saat içinde |
| Değerlendirme | 7 gün içinde |
| Yama yayını | Kritik: 7 gün, Orta: 30 gün |

### Kapsam Dışı

- DoS saldırıları (zaten yerel/özel kullanım için)
- Sosyal mühendislik
- Fiziksel erişim saldırıları

---

## 📦 Desteklenen Sürümler

| Sürüm | Durum | Notlar |
|-------|-------|--------|
| `main` branch | ✅ Aktif | En güncel, desteklenen |
| Eski commit'ler | ❌ Desteklenmiyor | Güncel sürüme geçin |

---

## 🛡️ Güvenlik Kontrol Listesi

Üretim ortamına geçmeden önce kontrol edin:

- [ ] `.env` dosyası `.gitignore`'da
- [ ] API anahtarları güçlü ve benzersiz
- [ ] Qdrant API key aktif (üretim için)
- [ ] TLS/HTTPS etkin (üretim için)
- [ ] Dosya izinleri kısıtlı (`chmod 600 .env`)
- [ ] Düzenli yedekleme planı var
- [ ] Cache verileri gözden geçirildi

---

## 📚 Ek Kaynaklar

- [Qdrant Security Best Practices](https://qdrant.tech/documentation/guides/security/)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [OWASP API Security](https://owasp.org/www-project-api-security/)

---

*Son güncelleme: Ocak 2026*
