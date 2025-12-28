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

# Semantic chunks (önerilen - daha zengin context için)
python main.py build-semantic-chunks --threshold 25 --threshold-type percentile

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
# Temel arama (tek ayet + semantic chunks paralel aranır)
python main.py search "sabır ve namaz"

# Daha fazla sonuç
python main.py search "Allah'ın rahmeti" --limit 20

# Detaylı görünüm
python main.py search "şefaat" -v
```

### Semantic Chunk Araması

```bash
# Doğrudan semantic chunk koleksiyonunda ara
python main.py search-semantic "Adem'in yaratılışı"

# Bir surenin chunk yapısını incele
python main.py analyze-chunks --surah 2
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

Her arama otomatik olarak 5 aşamadan geçer:

1. **Query Enhancement**: LLM sorgunuzu eşanlamlı kelimelerle genişletir
2. **Multi-Query**: 5 farklı perspektiften sorgu varyasyonları oluşturulur
3. **Parallel Search**: 
   - `quran_tr` (tek ayet koleksiyonu)
   - `quran_semantic_chunks` (gruplu ayetler)
4. **RRF Fusion**: Her iki koleksiyonun sonuçları birleştirilir
5. **Reranking**: Cross-encoder ile en alakalı sonuçlar seçilir

**Örnek:**
- Sorgu: "sabır ve namaz"
- Enhanced: "sabır, tahammül, tevekkül, namaz, salat, ibadet..."
- Sonuç: En alakalı 10 ayet/chunk, %99+ güven skoru

---

## 📦 Semantic Chunking Nedir?

Semantic chunking, anlam olarak ilişkili ayetleri gruplar:

| Özellik | Açıklama |
|---------|----------|
| Chunk sayısı | 1779 (6236 ayetten) |
| Ortalama boyut | ~3.5 ayet/chunk |
| Yöntem | Percentile-based boundary detection |
| Avantaj | Kıssa, hüküm grupları bütün kalır |

### Threshold Türleri

| Tür | Açıklama | Örnek |
|-----|----------|-------|
| `percentile` | En düşük X% benzerlik farkları | `--threshold 25` |
| `gradient` | Benzerlik değişim hızı | Domain-specific |
| `interquartile` | Q1 - k*IQR altı | Outlier detection |
| `std` | mean - k*std altı | Normal dağılım |
| `fixed` | Sabit threshold | `--threshold 0.45` |

### Örnekler

```bash
# Varsayılan (percentile 25 - ~3.5 ayet/chunk)
python main.py build-semantic-chunks

# Daha büyük chunk'lar (~5 ayet/chunk)
python main.py build-semantic-chunks --threshold 15

# Daha küçük chunk'lar (~2.5 ayet/chunk)
python main.py build-semantic-chunks --threshold 40

# IQR-based (otomatik)
python main.py build-semantic-chunks --threshold 1.5 --threshold-type interquartile
```

---

## 📊 Sonuç Tablosu

Sonuçlar şu formatta gösterilir:

```
┌───┬─────────────────────┬──────────┬────────────────────────────────┐
│ # │ Reference           │ Score    │ Translation                    │
├───┼─────────────────────┼──────────┼────────────────────────────────┤
│ 1 │ 2:45 El-Bakara      │ 0.998    │ Sabır ve namazla Allah'tan...  │
│ 2 │ 2:30-33 (4v)        │ 0.995    │ Hani Rabbin meleklere...       │
│   │ El-Bakara           │          │ (semantic chunk - 4 ayet)      │
└───┴─────────────────────┴──────────┴────────────────────────────────┘
```

- **Reference**: Sure:Ayet (veya aralık) ve sure adı
- **(Xv)**: Semantic chunk ise kaç ayet içerdiği
- **Score**: Reranker güven skoru (0-1)
- **Translation**: Ayetin/chunk'ın Türkçe meali

---

## ⚡ Python API Kullanımı

```python
from src.ultimate_rag import UltimateRAG

# Pipeline oluştur (semantic chunks varsayılan aktif)
rag = UltimateRAG(enable_semantic_chunks=True)

# Kur'an araması
results = rag.search_quran("şefaat kavramı", top_k=5)

for r in results:
    if hasattr(r, 'verse_id'):
        # Tek ayet sonucu
        print(f"{r.surah_id}:{r.verse_id} - {r.translation[:50]}...")
    else:
        # Semantic chunk sonucu
        print(f"{r.surah_id}:{r.start_verse}-{r.end_verse} ({r.verse_count} ayet)")
        print(f"  {r.combined_translation[:80]}...")

# Semantic chunks'ı devre dışı bırak
rag_simple = UltimateRAG(enable_semantic_chunks=False)
```

---

## ❓ Sık Sorulan Sorular

**S: Arama neden 30-60 saniye sürüyor?**
A: Ultimate RAG doğruluk odaklıdır. LLM çağrıları ve CPU'da reranking zaman alır. GPU ile 5-10x hızlanır.

**S: Semantic chunks neden gerekli?**
A: Tek ayet aramada bağlam kaybolabilir. Örneğin Adem kıssası 10+ ayet - bunları tek chunk olarak görmek daha faydalı.

**S: Hangi API key gerekli?**
A: Sadece `OPENROUTER_API_KEY`. Gemini Flash modeli kullanılır.

**S: İngilizce Kur'an var mı?**
A: Şu an sadece Türkçe meal mevcut.

**S: Semantic chunks nasıl yeniden oluşturulur?**
A: `python main.py build-semantic-chunks --recreate`

---

## 📞 Destek

Sorun yaşarsanız:
1. Qdrant'ın çalıştığından emin olun: `docker ps`
2. `.env` dosyasında API key olduğunu kontrol edin
3. `python main.py info` ile koleksiyon durumunu görün
4. Semantic chunks: `python main.py analyze-chunks --surah 1`
