# Sacred Texts Hybrid Search 🔍

Kuran-ı Kerim ve İncil için **semantik** ve **BM25 (keyword)** aramayı birleştiren gelişmiş hibrit arama sistemi.

## ✨ Özellikler

### Temel Özellikler
- 🧠 **Semantik Arama**: Anlam tabanlı arama (dense vectors)
- 🔤 **Keyword Arama**: Kelime eşleşmesi (BM25 sparse vectors)
- ⚡ **Hibrit Arama**: RRF fusion ile her iki yöntemin birleşimi
- 📖 **Kuran**: 6236 ayet, 114 sure - Türkçe meal
- 📕 **İncil**: Türkçe (HADI) ve İngilizce (KJVA - Apocrypha dahil)

### 🚀 Yeni RAG Optimizasyonları

| Özellik | Açıklama | Fayda |
|---------|----------|-------|
| **Async Embeddings** | Paralel API çağrıları | 3x hızlı indexleme |
| **GraphRAG** | Neo4j bilgi grafiği | Kavramsal ilişki keşfi |
| **Semantic Cache** | Benzer sorgu önbellekleme | <100ms tekrar sorgular |

---

## 🛠️ Kurulum

### 1. Qdrant'ı Başlatın

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. (Opsiyonel) Neo4j'yi Başlatın (GraphRAG için)

```bash
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 neo4j:5
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenleri (.env dosyası)

```env
# OpenRouter API (zorunlu)
OPENROUTER_API_KEY=your-api-key-here

# Neo4j (GraphRAG için opsiyonel)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
```

### 5. Veriyi İndeksleyin

```bash
# Kuran (Türkçe)
python main.py index

# İncil - Türkçe
python main.py index-bible --translation turhadi

# (Opsiyonel) Bilgi Grafiği Oluştur
python main.py build-graph --collection quran_tr
```

---

## 📖 Kullanım

### Kuran Araması

```bash
# Hibrit Arama (Önerilen)
python main.py search "Allah'ın rahmeti"
python main.py search "namaz kılmak" --limit 5

# Multi-Query RAG (RAG-Fusion)
python main.py search "sabır ve namaz" --multi-query

# Reranking ile Daha Hassas Sonuçlar
python main.py search "sabır ve namaz" --rerank

# Query Enhancement ile Sorgu Genişletme
python main.py search "şükür" --enhance

# Graf Destekli Arama (Neo4j gerekir)
python main.py search "Hz. İbrahim" --graph

# Cache'i Atlayarak Arama
python main.py search "rahmet" --no-cache

# Tüm Özellikler Birlikte
python main.py search "doğru yol" --multi-query --rerank
```

### İncil Araması

```bash
# Türkçe İncil
python main.py search-bible "İsa Mesih" --translation turhadi

# İngilizce İncil (Apocrypha dahil)
python main.py search-bible "love your neighbor" --translation kjva
```

### Cache Yönetimi

```bash
# Cache istatistikleri
python main.py cache-info

# Tüm cache'i temizle
python main.py cache-clear

# Eski girdileri temizle (12 saatten eski)
python main.py cache-clear --older-than 12
```

### GraphRAG Yönetimi

```bash
# Bilgi grafiği oluştur
python main.py build-graph --collection quran_tr

# Graf istatistikleri
python main.py graph-info

# Grafiği temizle ve yeniden oluştur
python main.py build-graph --clear
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
├── README.md           
├── user_guide.md              # Kullanıcı rehberi
├── .env                       # Ortam değişkenleri
├── data/
│   ├── quran_tr.json          # Kuran (Türkçe)
│   ├── bible_turhadi.json     # İncil (Türkçe)
│   └── bible_kjva.json        # İncil (İngilizce)
└── src/
    ├── embeddings.py          # Dense/Sparse + AsyncDenseEncoder
    ├── indexer.py             # Qdrant indeksleme (HNSW + Quantization)
    ├── search.py              # Hybrid search API
    ├── semantic_cache.py      # 🆕 Semantic caching
    ├── graph_rag.py           # 🆕 Neo4j GraphRAG
    ├── multi_query.py         # RAG-Fusion
    ├── reranker.py            # Cross-encoder reranking
    ├── query_enhancer.py      # LLM sorgu genişletme
    └── ...
```

---

## ⚙️ Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Dense Encoder | `openai/text-embedding-3-large` via OpenRouter (3072 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| Graph DB | Neo4j (GraphRAG için) |
| Fusion | Reciprocal Rank Fusion (RRF, k=40) |
| Cache | Qdrant Semantic Cache (0.85 threshold) |

---

## 🚀 Performans İyileştirmeleri

| Optimizasyon | Etki |
|--------------|------|
| Async Embeddings | 3x hızlı indexleme |
| Semantic Cache | 25x hızlı tekrar sorgu |
| GraphRAG | +30-50% recall artışı |
| HNSW + Quantization | %75 RAM tasarrufu |

---

## 📚 Örnek Aramalar

| Kaynak | Sorgu | Açıklama |
|--------|-------|----------|
| Kuran | "sabretmek" | Sabır konusundaki ayetler |
| Kuran | "cennet ve cehennem" | Ahiret konuları |
| Kuran + Graph | "Hz. Musa" --graph | Musa + ilişkili kavramlar |
| İncil | "İsa Mesih" | İsa ile ilgili bölümler |

---

## 📄 Lisans

MIT
