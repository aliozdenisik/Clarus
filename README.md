# Sacred Texts Hybrid Search 🔍

Kuran-ı Kerim ve İncil için **semantik** ve **BM25 (keyword)** aramayı birleştiren hibrit arama sistemi.

## Özellikler

- 🧠 **Semantik Arama**: Anlam tabanlı arama (dense vectors)
- 🔤 **Keyword Arama**: Kelime eşleşmesi (BM25 sparse vectors)
- ⚡ **Hibrit Arama**: RRF fusion ile her iki yöntemin birleşimi
- 📖 Kuran: 6236 ayet, 114 sure - Türkçe meal
- 📕 İncil: Türkçe (HADI) ve İngilizce (KJVA - Apocrypha dahil)

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
# Kuran (Türkçe)
python main.py index

# İncil - Türkçe
python main.py index-bible --translation turhadi

# İncil - İngilizce (Apocrypha dahil)
python main.py index-bible --translation kjva
```

## Kullanım

### Kuran Araması

```bash
# Hibrit Arama (Önerilen)
python main.py search "Allah'ın rahmeti"
python main.py search "namaz kılmak" --limit 5

# Sadece Semantik
python main.py search "yardım isteme" --mode semantic

# Sadece Keyword
python main.py search "Rahman Rahim" --mode keyword
```

### İncil Araması

```bash
# Türkçe İncil
python main.py search-bible "İsa Mesih" --translation turhadi

# İngilizce İncil (Apocrypha dahil)
python main.py search-bible "love your neighbor" --translation kjva

# Detaylı sonuç
python main.py search-bible "sevgi" -v
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
│   ├── quran_tr.json     # Kuran (Türkçe)
│   ├── bible_turhadi.json # İncil (Türkçe)
│   └── bible_kjva.json    # İncil (İngilizce + Apocrypha)
└── src/
    ├── __init__.py
    ├── data_loader.py    # Kuran veri yükleme
    ├── bible_loader.py   # İncil veri yükleme
    ├── embeddings.py     # Dense ve sparse embeddings
    ├── indexer.py        # Qdrant indeksleme
    └── search.py         # Hybrid search API
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

## Mevcut Çeviriler

| Çeviri | Kod | Açıklama |
|--------|-----|----------|
| 🕋 Kuran | `quran_tr` | Türkçe meal (6,236 ayet) |
| 📖 İncil (TR) | `turhadi` | Türkçe Easy-to-Read (7,959 ayet, NT only) |
| 📖 İncil (EN) | `kjva` | King James + Apocrypha (36,819 ayet) |

## Örnek Aramalar

| Kaynak | Sorgu | Açıklama |
|--------|-------|----------|
| Kuran | "sabretmek" | Sabır konusundaki ayetler |
| Kuran | "cennet ve cehennem" | Ahiret konuları |
| İncil | "İsa Mesih" | İsa ile ilgili bölümler |
| İncil | "love" | Sevgi konusu (İngilizce) |

## Lisans

MIT
