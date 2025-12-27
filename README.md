# Quran Hybrid Search 🔍

Kuran-ı Kerim Türkçe meali için **semantik** ve **BM25 (keyword)** aramayı birleştiren hibrit arama sistemi.

## Özellikler

- 🧠 **Semantik Arama**: Anlam tabanlı arama (dense vectors)
- 🔤 **Keyword Arama**: Kelime eşleşmesi (BM25 sparse vectors)
- ⚡ **Hibrit Arama**: RRF fusion ile her iki yöntemin birleşimi
- 📖 6236 ayet, 114 sure - tam Türkçe meal

## Kurulum

### 1. Qdrant'ı Başlatın

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 3. Veriyi İndeksleyin

```bash
python main.py index
```

## Kullanım

### Hibrit Arama (Önerilen)

```bash
python main.py search "Allah'ın rahmeti"
python main.py search "namaz kılmak" --limit 5
```

### Sadece Semantik Arama

```bash
python main.py search "yardım isteme" --mode semantic
```

### Sadece Keyword Arama

```bash
python main.py search "Rahman Rahim" --mode keyword
```

### Detaylı Sonuç

```bash
python main.py search "cennet" -v
```

### Koleksiyon Bilgisi

```bash
python main.py info
```

## Proje Yapısı

```
qdrant/
├── main.py              # CLI entrypoint
├── requirements.txt     # Dependencies
├── README.md           
├── data/
│   └── quran_tr.json   # Cached Quran data
└── src/
    ├── __init__.py
    ├── data_loader.py   # Veri yükleme ve chunking
    ├── embeddings.py    # Dense ve sparse embeddings
    ├── indexer.py       # Qdrant indeksleme
    └── search.py        # Hybrid search API
```

## Ortam Değişkenleri

```bash
# OpenRouter API anahtarınızı ayarlayın
export OPENROUTER_API_KEY="your-api-key-here"  # Linux/Mac
set OPENROUTER_API_KEY=your-api-key-here        # Windows
```

## Teknik Detaylar

| Bileşen | Teknoloji |
|---------|-----------|
| Dense Encoder | `qwen/qwen3-embedding-8b` via OpenRouter API (4096 dim) |
| Sparse Encoder | `Qdrant/bm25` via FastEmbed |
| Vector DB | Qdrant |
| Fusion | Reciprocal Rank Fusion (RRF) |

## Örnek Aramalar

| Sorgu | Açıklama |
|-------|----------|
| "sabretmek" | Sabır konusundaki ayetler |
| "cennet ve cehennem" | Ahiret konuları |
| "anne baba" | Ebeveynlere davranış |
| "namaz zekat" | İbadet konuları |

## Lisans

MIT
