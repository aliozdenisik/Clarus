# Clarus

Kuran-ı Kerim ve Incil icin **maksimum dogruluk odakli** Ultimate RAG arama sistemi.  
Karsilastirmali teolojik analiz ve Multi-Agent LLM destekli cevap uretimi ozellikleri ile.

## Ultimate RAG Pipeline

Tum en iyi RAG metodolojilerini tek bir pipeline'da birlestirir:

```
Query -> ENHANCE -> MULTI-QUERY -> PARALLEL SEARCH -> RRF FUSION -> ANSWER
                                     |
     +-------------------------------+-------------------------------+
     |                               |                               |
+----+----+    +---------+    +------+------+    +-----------------+
|  QURAN  |    |BIBLE OT |    |  BIBLE NT   |    |BIBLE APOCRYPHA  |
| 6,236   |    | 23,145  |    |   7,957     |    |     5,717       |
+---------+    +---------+    +-------------+    +-----------------+
```

| Asama | Aciklama | Teknoloji |
|-------|----------|-----------|
| **1. Query Enhancement** | LLM ile sorgu genisletme | Grok 4.1 Fast |
| **2. Multi-Query** | 3-5 farkli perspektif | Grok 4.1 Fast |
| **3. Parallel Search** | 4 testament koleksiyonda arama | OpenAI text-embedding-3-large |
| **4. RRF Fusion** | Sonuclari birlestirme | Reciprocal Rank Fusion |
| **5. Multi-Agent** | 5 uzman ajan ile cevap uretme | Gemini 2.5 Flash |

---

## Son Guncellemeler

### API-First Architecture (2026-01-22)

Frontend kaldirildi, CLI ve REST API odakli mimariye gecildi:

- **CLI**: Birincil kullanici arayuzu (`python main.py`)
- **REST API**: FastAPI backend (programatik erisim)
- **SSE Streaming**: Token-by-token cevap akisi

### Multi-Agent Answer Generation (2026-01-20)

5 uzman ajan ile paralel cevap uretimi:

| Ajan | Koleksiyon | Gorev |
|------|------------|-------|
| QuranAgent | `quran_tr` | Kuran perspektifi |
| OldTestamentAgent | `bible_ot` | Eski Ahit perspektifi |
| NewTestamentAgent | `bible_nt` | Yeni Ahit perspektifi |
| ApocryphaAgent | `bible_apocrypha` | Apokrifa perspektifi |
| SummaryAgent | - | 4 yorumu sentezler |

### 4-Testament Koleksiyon Yapisi (2026-01-20)

| Koleksiyon | Ayet Sayisi | Aciklama |
|------------|-------------|----------|
| `quran_tr` | 6,236 | Kuran (Turkce) |
| `bible_ot` | 23,145 | Eski Ahit (KJVA) |
| `bible_nt` | 7,957 | Yeni Ahit (KJVA) |
| `bible_apocrypha` | 5,717 | Apokrifa (KJVA) |

### Semantic LLM Cache (2026-01-19)

- %95 benzerlik esigi ile sorgu eslestirme
- 7 gun TTL
- %60-80 API maliyeti azaltma

---

## Performans

| Metrik | Deger |
|--------|-------|
| Overall F1 Score | **%57+** |
| Kuran Recall | **%80+** |
| Incil Recall | **%100** |
| Confidence Score | **%96** |
| Multi-Agent Latency | **~40s** |

---

## Kurulum

### 1. Qdrant'i Baslatin

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Bagimliliklari Yukleyin

```bash
pip install -r requirements.txt
```

### 3. Ortam Degiskenleri (.env dosyasi)

```env
# Zorunlu
OPENROUTER_API_KEY=your-openrouter-key

# API Kullanimi (opsiyonel)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
JWT_SECRET_KEY=your-secret-key
```

### 4. Koleksiyonlari Olusturun

```bash
python scripts/setup_all_collections.py
```

Bu script:
- Mevcut koleksiyonlari siler (temiz baslangic)
- 4 koleksiyonu async indexing ile olusturur (~2 dakika)

---

## Kullanim

### CLI Komutlari

#### Arama

```bash
# Kuran aramasi
python main.py search "sabir ve namaz"

# Incil aramasi
python main.py search-bible "love your neighbor" --translation kjva

# Semantic chunk aramasi
python main.py search-semantic "Adem'in yaratilisi"
python main.py search-bible-semantic "creation of Adam"
```

#### Soru-Cevap (Ask)

```bash
# Kuran'dan soru sor
python main.py ask "Islam'da sabir nedir?"

# Incil'den soru sor
python main.py ask-bible "What is love according to the Bible?"
```

#### Karsilastirmali Analiz

```bash
# Tek essay modu (hizli)
python main.py compare "Sabir ve dayaniklilik kavrami"

# Multi-agent modu (5 paragraf, daha detayli)
python main.py compare --multi-agent "Yaratilis hikayesi"
```

#### Sistem Komutlari

```bash
# Koleksiyon bilgisi
python main.py info

# Cache istatistikleri
python main.py cache-info

# Cache temizle
python main.py cache-clear
```

### REST API

API'yi baslatmak icin:

```bash
# PostgreSQL + Qdrant
docker compose up -d

# FastAPI server
uvicorn app.main:app --reload
```

API Endpoints:

| Endpoint | Method | Aciklama |
|----------|--------|----------|
| `/api/auth/register` | POST | Kullanici kaydi |
| `/api/auth/login` | POST | JWT ile giris |
| `/api/search/quran` | POST | Kuran aramasi |
| `/api/search/bible` | POST | Incil aramasi |
| `/api/stream/search` | GET | SSE streaming arama |
| `/api/compare/` | POST | Multi-agent karsilastirma |
| `/docs` | GET | OpenAPI dokumantasyonu |

### Python API

```python
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

# === Ultimate RAG ===
rag = UltimateRAG(enable_semantic_chunks=True)

# Arama
results = rag.search_quran("sefaat kavrami", top_k=5)
results = rag.search_bible("forgiveness", translation="kjva")

# Soru-Cevap
answer = rag.ask_quran("Namaz nasil kilinir?")
answer = rag.ask_bible("How to love your neighbor?")

# === Comparative RAG ===
comp = ComparativeRAG()

# Tek essay modu
essay = comp.compare("Yaratilis ve insanin kokeni")
print(essay['essay'])

# Multi-agent modu (5 paragraf)
result = comp.compare_multi_agent("Yaratilis ve insanin kokeni")
print(result['paragraphs'])
```

---

## Proje Yapisi

```
qdrant/
├── main.py                         # CLI entrypoint
├── requirements.txt                # Dependencies
├── docker-compose.yml              # PostgreSQL + Qdrant
│
├── app/                            # FastAPI backend (REST API)
│   ├── main.py                     # ASGI entrypoint
│   ├── config.py                   # Pydantic settings
│   ├── db.py                       # SQLAlchemy async
│   ├── models.py                   # User, SearchHistory
│   ├── auth/                       # JWT + OAuth
│   └── api/                        # Route handlers
│
├── src/                            # RAG pipeline modulleri
│   ├── ultimate_rag.py             # Ana RAG pipeline
│   ├── comparative_rag.py          # Karsilastirmali RAG
│   ├── multi_agent_answer_generator.py  # 5-Ajan sistemi
│   ├── comparative_answer_generator.py  # Essay uretici
│   ├── answer_generator.py         # LLM cevap uretici
│   ├── semantic_chunker.py         # Kuran semantic chunking
│   ├── bible_semantic_chunker.py   # Incil semantic chunking
│   ├── query_enhancer.py           # LLM sorgu genisletme
│   ├── llm_cache.py                # Semantic LLM cache
│   ├── search.py                   # Arama modulleri
│   ├── embeddings.py               # Dense + Sparse encoders
│   ├── indexer.py                  # Qdrant indeksleme
│   ├── data_loader.py              # Kuran veri yukleyici
│   └── bible_loader.py             # Incil veri yukleyici
│
├── data/
│   ├── quran_tr.json               # Kuran (Turkce)
│   └── bible_kjva.json             # Incil (KJVA)
│
├── scripts/
│   ├── setup_all_collections.py    # Unified indeksleme
│   └── dev.sh                      # Development startup
│
├── tests/
│   └── test_data.json              # Retrieval accuracy test
│
└── memory-bank/                    # Proje context dosyalari
```

---

## Teknik Detaylar

| Bilesen | Teknoloji |
|---------|-----------|
| Dense Encoder | `openai/text-embedding-3-large` (3072 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| LLM (Enhancement) | Grok 4.1 Fast via OpenRouter |
| LLM (Answers) | Gemini 2.5 Flash via OpenRouter |
| Fusion | Reciprocal Rank Fusion (RRF, k=60) |
| Cache | Semantic LLM Cache (theta=0.95, 7-day TTL) |
| Backend | FastAPI + SQLAlchemy async |
| Auth | JWT + Google OAuth |

---

## Ornek Sorgular

| Komut | Sorgu | Aciklama |
|-------|-------|----------|
| `search` | "sabir ve namaz" | Kuran'da sabir konusu |
| `ask` | "Oruc nasil tutulur?" | Detayli cevap + kaynaklar |
| `search-bible` | "love your enemies" | Incil aramasi |
| `ask-bible` | "What is salvation?" | Incil soru-cevap |
| `compare` | "Yaratilis hikayesi" | Kuran-Incil karsilastirma |
| `compare --multi-agent` | "Affetme kavrami" | 5 ajan ile detayli analiz |

---

## Lisans

MIT
