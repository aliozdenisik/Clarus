# Sacred Texts Ultimate RAG Search 🚀

Kuran-ı Kerim ve İncil için **maksimum doğruluk odaklı** Ultimate RAG arama sistemi.  
Karşılaştırmalı teolojik analiz ve Multi-Agent LLM destekli cevap üretimi özellikleri ile.

## ✨ Ultimate RAG Pipeline

Tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:

---

Query → ENHANCE → MULTI-QUERY → PARALLEL SEARCH → RRF FUSION → ANSWER
                                     ↓
     ┌───────────────────────────────┼───────────────────────────────┐
     │                               │                               │
┌────┴────┐    ┌─────────┐    ┌──────┴──────┐    ┌─────────────────┐
│  QURAN  │    │BIBLE OT │    │  BIBLE NT   │    │BIBLE APOCRYPHA  │
│ 6,236   │    │ 23,145  │    │   7,957     │    │     5,717       │
└─────────┘    └─────────┘    └─────────────┘    └─────────────────┘

---

| Aşama | Açıklama | Teknoloji |
|-------|----------|-----------|
| **1. Query Enhancement** | LLM ile sorgu genişletme | Grok 4.1 Fast |
| **2. Multi-Query** | 3-5 farklı perspektif | Grok 4.1 Fast |
| **3. Parallel Search** | 4 testament koleksiyonda arama | OpenAI text-embedding-3-large |
| **4. RRF Fusion** | Sonuçları birleştirme | Reciprocal Rank Fusion |
| **5. Multi-Agent** | 5 uzman ajan ile cevap üretme | Gemini 2.5 Flash |

---

## 🆕 Son Güncellemeler

### 🤖 Multi-Agent Answer Generation (2026-01-20)

5 uzman ajan ile paralel cevap üretimi:

| Ajan | Koleksiyon | Görev |
|------|------------|-------|
| QuranAgent | `quran_tr` | Kuran perspektifi |
| OldTestamentAgent | `bible_ot` | Eski Ahit perspektifi |
| NewTestamentAgent | `bible_nt` | Yeni Ahit perspektifi |
| ApocryphaAgent | `bible_apocrypha` | Apokrifa perspektifi |
| SummaryAgent | - | 4 yorumu sentezler |

### � 4-Testament Koleksiyon Yapısı (2026-01-20)

Bible tek koleksiyondan 3 ayrı koleksiyona bölündü:

| Koleksiyon | Ayet Sayısı | Açıklama |
|------------|-------------|----------|
| `quran_tr` | 6,236 | Kuran (Türkçe) |
| `bible_ot` | 23,145 | Eski Ahit (KJVA) |
| `bible_nt` | 7,957 | Yeni Ahit (KJVA) |
| `bible_apocrypha` | 5,717 | Apokrifa (KJVA) |

### ⚡ Semantic LLM Cache (2026-01-19)

LLM yanıtları için semantic cache:

- %95 benzerlik eşiği ile sorgu eşleştirme
- 7 gün TTL
- %60-80 API maliyeti azaltma

### 🎯 Comparative RAG (Karşılaştırmalı Analiz)

Kuran ve İncil'i tek sorguda arayıp teolojik karşılaştırma üretir:

- 4 paralel arama (her testten 20 ayet)
- 80 ayet analizi
- İki mod: Tek essay veya 5-paragraf multi-agent

---

## 📊 Performans

| Metrik | Değer |
|--------|-------|
| Overall F1 Score | **%57+** |
| Kuran Recall | **%80+** |
| İncil Recall | **%100** |
| Confidence Score | **%96** |
| Multi-Agent Latency | **~40s** |

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
```

### 4. Koleksiyonları Oluşturun

```bash
# Tek komutla tüm koleksiyonları oluştur (Önerilen)
python scripts/setup_all_collections.py
```

Bu script:

- Mevcut koleksiyonları siler (temiz başlangıç)
- `quran_tr` (6,236 ayet)
- `bible_ot` (23,145 ayet)
- `bible_nt` (7,957 ayet)
- `bible_apocrypha` (5,717 ayet)

koleksiyonlarını async indexing ile oluşturur (~2 dakika).

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
# Tek essay modu (hızlı)
python main.py compare "Sabır ve dayanıklılık kavramı"

# Multi-agent modu (5 paragraf, daha detaylı)
python main.py compare --multi-agent "Yaratılış hikayesi"
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

# Tek essay modu
essay = comp.compare("Yaratılış ve insanın kökeni")
print(essay['essay'])

# Multi-agent modu (5 paragraf)
result = comp.compare_multi_agent("Yaratılış ve insanın kökeni")
print(result['paragraphs'])
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
│   └── bible_kjva.json             # İncil (KJVA)
├── scripts/
│   └── setup_all_collections.py    # 🔧 Unified indeksleme script
├── src/
│   ├── ultimate_rag.py             # 🚀 Ana RAG pipeline
│   ├── comparative_rag.py          # ⚖️ Karşılaştırmalı RAG
│   ├── multi_agent_answer_generator.py  # 🤖 5-Ajan sistemi
│   ├── comparative_answer_generator.py  # Essay üretici
│   ├── answer_generator.py         # 💬 LLM cevap üretici
│   ├── semantic_chunker.py         # 📦 Kuran semantic chunking
│   ├── bible_semantic_chunker.py   # 📦 İncil semantic chunking
│   ├── query_enhancer.py           # LLM sorgu genişletme
│   ├── llm_cache.py                # Semantic LLM cache
│   ├── search.py                   # Arama modülleri
│   ├── embeddings.py               # Dense + Sparse encoders
│   ├── indexer.py                  # Qdrant indeksleme
│   ├── data_loader.py              # Kuran veri yükleyici
│   └── bible_loader.py             # İncil veri yükleyici
├── tests/
│   └── test_data.json              # Retrieval accuracy test data
└── memory-bank/                    # Proje context dosyaları
```

---

## ⚙️ Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Dense Encoder | `openai/text-embedding-3-large` (3072 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| LLM (Enhancement) | Grok 4.1 Fast via OpenRouter |
| LLM (Answers) | Gemini 2.5 Flash via OpenRouter |
| Fusion | Reciprocal Rank Fusion (RRF, k=60) |
| Cache | Semantic LLM Cache (θ=0.95, 7-day TTL) |

---

## 📚 Örnek Sorgular

| Komut | Sorgu | Açıklama |
|-------|-------|----------|
| `search` | "sabır ve namaz" | Kuran'da sabır konusu |
| `ask` | "Oruç nasıl tutulur?" | Detaylı cevap + kaynaklar |
| `search-bible` | "love your enemies" | İncil araması |
| `ask-bible` | "What is salvation?" | İncil soru-cevap |
| `compare` | "Yaratılış hikayesi" | Kuran-İncil karşılaştırma |
| `compare --multi-agent` | "Affetme kavramı" | 5 ajan ile detaylı analiz |

---

## 📄 Lisans

MIT
