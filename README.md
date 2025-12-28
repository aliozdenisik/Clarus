# Sacred Texts Ultimate RAG Search 🚀

Kuran-ı Kerim ve İncil için **maksimum doğruluk odaklı** Ultimate RAG arama sistemi.

## ✨ Ultimate RAG Pipeline

Tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:

```
Query → ENHANCE → MULTI-QUERY → PARALLEL SEARCH → RRF FUSION → RERANK → Results
                                    ↓
                          ┌─────────┴─────────┐
                          │                   │
                    Single-Verse      Semantic Chunks
                    (quran_tr)    (quran_semantic_chunks)
```

| Aşama | Açıklama | Teknoloji |
|-------|----------|-----------|
| **1. Query Enhancement** | LLM ile sorgu genişletme | Gemini Flash |
| **2. Multi-Query** | 3-5 farklı perspektif | Gemini Flash |
| **3. Parallel Search** | Tek ayet + Semantic chunk araması | OpenAI text-embedding-3-large |
| **4. RRF Fusion** | Sonuçları birleştirme | Reciprocal Rank Fusion |
| **5. Reranking** | Cross-encoder final sıralaması | Qwen3-Reranker |

### 📦 Semantic Chunking (YENİ!)

Semantik olarak ilişkili ayetleri gruplar:
- **1779 semantic chunk** (ortalama ~3.5 ayet/chunk)
- Tematik bütünlük korunur (kıssa, hüküm grupları)
- Paralel arama ile daha zengin context

### 📊 Performans

- **%84+ isabet oranı** (Kur'an aramaları)
- **%90+ keyword eşleşme** (enhance modunda)
- **Score: 0.99+** (rerank sonrası)

---

## 🛠️ Kurulum

### 1. Qdrant'ı Başlatın

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenleri (.env dosyası)

```env
OPENROUTER_API_KEY=your-api-key-here
```

### 4. Veriyi İndeksleyin

```bash
# Kuran (Türkçe) - Tek ayet koleksiyonu
python main.py index

# Semantic chunks (paralel arama için)
python main.py build-semantic-chunks --threshold 25 --threshold-type percentile

# İncil - Türkçe
python main.py index-bible --translation turhadi

# İncil - İngilizce (KJVA)
python main.py index-bible --translation kjva
```

---

## 📖 Kullanım

### Kuran Araması

```bash
# Temel arama (Ultimate RAG + Semantic Chunks otomatik)
python main.py search "sabır ve namaz"

# Daha fazla sonuç
python main.py search "Allah'ın rahmeti" --limit 10

# Detaylı sonuç görüntüleme
python main.py search "şefaat" -v
```

### Semantic Chunk Araması

```bash
# Doğrudan semantic chunk koleksiyonunda ara
python main.py search-semantic "Adem'in yaratılışı"

# Belirli surenin chunk yapısını analiz et
python main.py analyze-chunks --surah 2
```

### İncil Araması

```bash
# Türkçe İncil
python main.py search-bible "İsa Mesih'in doğumu"

# İngilizce İncil
python main.py search-bible "love your neighbor" --translation kjva
```

### Python API

```python
from src.ultimate_rag import UltimateRAG

# Pipeline oluştur (semantic chunks varsayılan olarak aktif)
rag = UltimateRAG(enable_semantic_chunks=True)

# Kur'an araması
results = rag.search_quran("şefaat kavramı", top_k=5)

# İncil araması
results = rag.search_bible("İsa'nın öğretileri", translation="turhadi")

# Semantic chunks'ı devre dışı bırak
rag = UltimateRAG(enable_semantic_chunks=False)
```

### Koleksiyon Bilgisi

```bash
python main.py info
```

---

## 📁 Proje Yapısı

```
qdrant/
├── main.py                    # CLI entrypoint
├── requirements.txt           # Dependencies
├── README.md                  # Bu dosya
├── user_guide.md              # Kullanıcı rehberi
├── .env                       # API keys
├── data/
│   ├── quran_tr.json          # Kuran (Türkçe)
│   ├── semantic_chunks.json   # Semantic chunk verileri
│   ├── bible_turhadi.json     # İncil (Türkçe)
│   └── bible_kjva.json        # İncil (İngilizce)
└── src/
    ├── ultimate_rag.py        # 🚀 Ana pipeline
    ├── semantic_chunker.py    # 📦 Semantic chunking modülü
    ├── query_enhancer.py      # LLM sorgu genişletme
    ├── reranker.py            # Cross-encoder reranking
    ├── search.py              # Semantic/Keyword/Hybrid search
    ├── embeddings.py          # Dense + Sparse encoders
    ├── indexer.py             # Qdrant indeksleme
    ├── data_loader.py         # Kur'an veri yükleyici
    └── bible_loader.py        # İncil veri yükleyici
```

---

## ⚙️ Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Dense Encoder | `openai/text-embedding-3-large` (3072 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| Reranker | `Qwen3-Reranker-0.6B-seq-cls` |
| LLM | Gemini 2.5 Flash Lite via OpenRouter |
| Fusion | Reciprocal Rank Fusion (RRF, k=60) |
| Semantic Chunking | Percentile-based boundary detection |

### Semantic Chunking Parametreleri

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `--threshold` | 25 | Percentile değeri (düşük = daha fazla chunk) |
| `--threshold-type` | percentile | percentile, gradient, interquartile, std, fixed |
| `--max-size` | 10 | Maksimum ayet/chunk |

---

## 📚 Örnek Aramalar

| Kaynak | Sorgu | Sonuç |
|--------|-------|-------|
| Kuran | "sabır ve namaz" | Bakara 45, 153, 155 |
| Kuran | "şefaat kavramı" | Zuhruf 86, Meryem 87 |
| Kuran | "miras hukuku" | Nisa 11-12, 176 |
| Kuran | "Adem'in yaratılışı" | Bakara 30-39 (semantic chunk) |
| İncil | "İsa'nın doğumu" | Matta 1-2, Luka 2 |

---

## 📄 Lisans

MIT
