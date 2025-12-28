# Sacred Texts Ultimate RAG - Kullanıcı Rehberi

Bu rehber, Sacred Texts Ultimate RAG sisteminin nasıl kullanılacağını açıklar.

## 🚀 Hızlı Başlangıç

### 1. Qdrant'ı Başlatın

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Veriyi İndeksleyin (İlk Kurulum)

```bash
# Kur'an
python main.py index

# İncil (Türkçe)
python main.py index-bible --translation turhadi
```

### 3. Aramaya Başlayın

```bash
python main.py search "sorgunuz"
```

---

## 📖 Arama Komutları

### Kur'an Araması

```bash
# Temel arama
python main.py search "sabır ve namaz"

# Daha fazla sonuç
python main.py search "Allah'ın rahmeti" --limit 20

# Detaylı görünüm
python main.py search "şefaat" -v
```

### İncil Araması

```bash
# Türkçe İncil
python main.py search-bible "İsa Mesih"

# İngilizce İncil
python main.py search-bible "forgiveness" --translation kjva
```

---

## 🔍 Ultimate RAG Pipeline Nasıl Çalışır?

Her arama otomatik olarak 4 aşamadan geçer:

1. **Query Enhancement**: LLM sorgunuzu eşanlamlı kelimelerle genişletir
2. **Multi-Query**: 5 farklı perspektiften sorgu varyasyonları oluşturulur
3. **Semantic Search**: Tüm sorgularla arama yapılır ve sonuçlar birleştirilir
4. **Reranking**: Cross-encoder ile en alakalı sonuçlar seçilir

**Örnek:**
- Sorgu: "sabır ve namaz"
- Enhanced: "sabır, tahammül, tevekkül, namaz, salat, ibadet..."
- Sonuç: En alakalı 10 ayet, %99+ güven skoru

---

## 📊 Sonuç Tablosu

Sonuçlar şu formatta gösterilir:

```
┌───┬─────────────────┬──────────┬────────────────────────────────┐
│ # │ Reference       │ Score    │ Translation                    │
├───┼─────────────────┼──────────┼────────────────────────────────┤
│ 1 │ 2:45 El-Bakara  │ 0.998    │ Sabır ve namazla Allah'tan...  │
│ 2 │ 2:153 El-Bakara │ 0.996    │ Ey inananlar! Sabredin ve...   │
└───┴─────────────────┴──────────┴────────────────────────────────┘
```

- **Reference**: Sure:Ayet numarası ve sure adı
- **Score**: Reranker güven skoru (0-1)
- **Translation**: Ayetin Türkçe meali

---

## ⚡ Python API Kullanımı

```python
from src.ultimate_rag import UltimateRAG

# Pipeline oluştur
rag = UltimateRAG()

# Kur'an araması
results = rag.search_quran("şefaat kavramı", top_k=5)

for r in results:
    print(f"{r.surah_id}:{r.verse_id} - {r.translation[:50]}...")
```

---

## ❓ Sık Sorulan Sorular

**S: Arama neden 30-60 saniye sürüyor?**
A: Ultimate RAG doğruluk odaklıdır. LLM çağrıları ve CPU'da reranking zaman alır. GPU ile 5-10x hızlanır.

**S: Hangi API key gerekli?**
A: Sadece `OPENROUTER_API_KEY`. Gemini Flash modeli kullanılır.

**S: İngilizce Kur'an var mı?**
A: Şu an sadece Türkçe meal mevcut.

---

## 📞 Destek

Sorun yaşarsanız:
1. Qdrant'ın çalıştığından emin olun: `docker ps`
2. `.env` dosyasında API key olduğunu kontrol edin
3. `python main.py info` ile koleksiyon durumunu görün
