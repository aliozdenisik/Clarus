# Sacred Texts Ultimate RAG Search 🚀

Kuran-ı Kerim ve İncil için **maksimum doğruluk odaklı** Ultimate RAG arama sistemi.  
Karşılaştırmalı teolojik analiz ve LLM destekli cevap üretimi özellikleri ile.

## ✨ Ultimate RAG Pipeline

Tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:

```
Query → ENHANCE → MULTI-QUERY → PARALLEL SEARCH → RRF FUSION → RERANK → ANSWER
                                    ↓
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
    ┌─────┴─────┐                                     ┌───────┴───────┐
    │   QURAN   │                                     │     BIBLE     │
    ├───────────┤                                     ├───────────────┤
    │Single-Verse│                                    │ Single-Verse  │
    │ + Semantic │                                    │  + Semantic   │
    │   Chunks   │                                    │    Chunks     │
    └───────────┘                                     └───────────────┘
```

| Aşama | Açıklama | Teknoloji |
|-------|----------|-----------|
| **1. Query Enhancement** | LLM ile sorgu genişletme | Gemini Flash |
| **2. Multi-Query** | 3-5 farklı perspektif | Gemini Flash |
| **3. Parallel Search** | Tek ayet + Semantic chunk araması | OpenAI text-embedding-3-large |
| **4. RRF Fusion** | Sonuçları birleştirme | Reciprocal Rank Fusion |
| **5. Reranking** | Cross-encoder final sıralaması | Qwen3-Reranker (SiliconFlow) |
| **6. Answer Generation** | LLM ile cevap üretme | Gemini 2.5 Flash |

---

## 🆕 Son Güncellemeler

### 🎯 Comparative RAG (Karşılaştırmalı Analiz)

Kuran ve İncil'i tek sorguda arayıp teolojik karşılaştırma makalesi üretir:

- 4 paralel arama (Kuran/İncil × Normal/Semantic)
- 80 ayet analizi (her aramadan 20)
- Akademik formatta karşılaştırmalı essay

### 💬 Answer Generation (Soru-Cevap)

Bulunan ayetlerden kapsamlı cevap üretir:

- Kaynak alıntıları ile
- Türkçe veya İngilizce

### 📦 Bible Semantic Chunks

İncil için semantik gruplama:

- Tematik bütünlük
- Kitap ve bölüm bazlı analiz

### ⚡ Multi-Query RAG

Sorguyu farklı perspektiflerden genişletir:

- Query caching ile optimizasyon
- Paralel arama

---

## 📊 Performans

| Metrik | Değer |
|--------|-------|
| Kuran isabet oranı | **%84+** |
| İncil isabet oranı | **%75+** |
| Keyword eşleşme | **%90+** |
| Rerank score | **0.99+** |

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
OPENROUTER_API_KEY=your-openrouter-key
SILICONFLOW_API_KEY=your-siliconflow-key  # Reranker için
```

### 4. Tek Komutla Kurulum (Önerilen)

```bash
# Tüm koleksiyonları oluştur (Kuran, İncil, Semantic Chunks)
python main.py setup
```

### 4b. Manuel Kurulum (Alternatif)

```bash
# Kuran (Türkçe)
python main.py index

# Kuran Semantic Chunks
python main.py build-semantic-chunks --threshold 25 --threshold-type percentile

# İncil (KJVA)
python main.py index-bible --translation kjva

# İncil Semantic Chunks
python main.py build-bible-semantic-chunks
```

---

## 📖 Kullanım

### 🔍 Arama Komutları

```bash
# Kuran araması
python main.py search "sabır ve namaz"

# İncil araması
python main.py search-bible "love your neighbor" --translation kjva

# Semantic chunk araması
python main.py search-semantic "Adem'in yaratılışı"
python main.py search-bible-semantic "creation of Adam"
```

### 💬 Soru-Cevap (Ask)

```bash
# Kuran'dan soru sor
python main.py ask "İslam'da sabır nedir?"

# İncil'den soru sor
python main.py ask-bible "What is love according to the Bible?"
```

### ⚖️ Karşılaştırmalı Analiz

```bash
# Kuran ve İncil'de ortak temayı karşılaştır
python main.py compare "Sabır ve dayanıklılık kavramı"
python main.py compare "Yaratılış hikayesi"
python main.py compare "Affetme ve merhamet"
```

### 📊 Sistem Komutları

```bash
# Koleksiyon bilgisi
python main.py info

# Cache istatistikleri
python main.py cache-info

# Cache temizle
python main.py cache-clear

# Chunk analizi
python main.py analyze-chunks --surah 2
```

---

## 🐍 Python API

```python
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

# === Ultimate RAG ===
rag = UltimateRAG(enable_semantic_chunks=True)

# Arama
results = rag.search_quran("şefaat kavramı", top_k=5)
results = rag.search_bible("forgiveness", translation="kjva")

# Soru-Cevap
answer = rag.ask_quran("Namaz nasıl kılınır?")
answer = rag.ask_bible("How to love your neighbor?")

# === Comparative RAG ===
comp = ComparativeRAG()
essay = comp.compare("Yaratılış ve insanın kökeni")
print(essay['essay'])
```

---

## 📁 Proje Yapısı

```
qdrant/
├── main.py                         # CLI entrypoint
├── requirements.txt                # Dependencies
├── README.md                       # Bu dosya
├── data/
│   ├── quran_tr.json               # Kuran (Türkçe)
│   ├── semantic_chunks.json        # Kuran semantic chunks
│   ├── bible_kjva.json             # İncil (KJVA)
│   └── bible_kjva_semantic_chunks.json  # İncil semantic chunks
└── src/
    ├── ultimate_rag.py             # 🚀 Ana RAG pipeline
    ├── comparative_rag.py          # ⚖️ Karşılaştırmalı RAG
    ├── comparative_answer_generator.py  # Karşılaştırmalı essay üretici
    ├── answer_generator.py         # 💬 LLM cevap üretici
    ├── semantic_chunker.py         # 📦 Kuran semantic chunking
    ├── bible_semantic_chunker.py   # 📦 İncil semantic chunking
    ├── query_enhancer.py           # LLM sorgu genişletme
    ├── reranker.py                 # Cross-encoder reranking
    ├── search.py                   # Arama modülleri
    ├── embeddings.py               # Dense + Sparse encoders
    ├── indexer.py                  # Qdrant indeksleme
    ├── data_loader.py              # Kuran veri yükleyici
    └── bible_loader.py             # İncil veri yükleyici
```

---

## ⚙️ Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Dense Encoder | `openai/text-embedding-3-large` (3072 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| Reranker | `Qwen3-Reranker-8B` via SiliconFlow |
| LLM (Enhancement) | Gemini 2.5 Flash Lite via OpenRouter |
| LLM (Answers) | Gemini 2.5 Flash via OpenRouter |
| Fusion | Reciprocal Rank Fusion (RRF, k=60) |

---

## 📚 Örnek Sorgular

| Komut | Sorgu | Açıklama |
|-------|-------|----------|
| `search` | "sabır ve namaz" | Kuran'da sabır konusu |
| `ask` | "Oruç nasıl tutulur?" | Detaylı cevap + kaynaklar |
| `search-bible` | "love your enemies" | İncil araması |
| `ask-bible` | "What is salvation?" | İncil soru-cevap |
| `compare` | "Yaratılış hikayesi" | Kuran-İncil karşılaştırma |

---

## 📄 Lisans

MIT
