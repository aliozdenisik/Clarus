# Sacred Texts Ultimate RAG Search 🚀

Kuran-ı Kerim ve İncil için **maksimum doğruluk odaklı** Ultimate RAG arama sistemi.

## ✨ Ultimate RAG Pipeline

Tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:

```
Query → ENHANCE → MULTI-QUERY → SEMANTIC SEARCH → RERANK → Results
```

| Aşama | Açıklama | Teknoloji |
|-------|----------|-----------|
| **1. Query Enhancement** | LLM ile sorgu genişletme | Gemini Flash |
| **2. Multi-Query** | 3-5 farklı perspektif | LLM |
| **3. Semantic Search** | Anlam tabanlı arama | OpenAI text-embedding-3-large |
| **4. Reranking** | Cross-encoder final sıralaması | Qwen3-Reranker |

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
# Kuran (Türkçe)
python main.py index

# İncil - Türkçe
python main.py index-bible --translation turhadi

# İncil - İngilizce (KJVA)
python main.py index-bible --translation kjva
```

---

## 📖 Kullanım

### Kuran Araması

```bash
# Temel arama (Ultimate RAG otomatik)
python main.py search "sabır ve namaz"

# Daha fazla sonuç
python main.py search "Allah'ın rahmeti" --limit 10

# Detaylı sonuç görüntüleme
python main.py search "şefaat" -v
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

rag = UltimateRAG()

# Kur'an araması
results = rag.search_quran("şefaat kavramı", top_k=5)

# İncil araması
results = rag.search_bible("İsa'nın öğretileri", translation="turhadi")
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
│   ├── bible_turhadi.json     # İncil (Türkçe)
│   └── bible_kjva.json        # İncil (İngilizce)
└── src/
    ├── ultimate_rag.py        # 🚀 Ana pipeline
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

---

## 📚 Örnek Aramalar

| Kaynak | Sorgu | Sonuç |
|--------|-------|-------|
| Kuran | "sabır ve namaz" | Bakara 45, 153, 155 |
| Kuran | "şefaat kavramı" | Zuhruf 86, Meryem 87 |
| Kuran | "miras hukuku" | Nisa 11-12, 176 |
| İncil | "İsa'nın doğumu" | Matta 1-2, Luka 2 |

---

## 📄 Lisans

MIT
