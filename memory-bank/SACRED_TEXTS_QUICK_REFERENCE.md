# Sacred Texts Collections - Quick Reference

## 🎯 IMMEDIATE ACTION ITEMS

### Download Everything (One Command)
```bash
bash backend/scripts/download_sacred_texts.sh ./sacred_texts_data
```

### Download Individual Collections
```bash
# Pseudepigrapha (500KB, JSON)
git clone https://github.com/tyler-slc/pseudepigrapha.git

# King James Apocrypha (5MB, JSON)
git clone https://github.com/1John419/kja.git

# Hindu Sacred Texts (100MB, JSON)
git clone https://github.com/bhavykhatri/DharmicData.git

# Dead Sea Scrolls (43MB, Text-Fabric)
git clone https://github.com/ETCBC/dss.git

# Church Fathers (200MB+, EpiDoc XML)
git clone https://github.com/OpenGreekAndLatin/csel-dev.git

# OSIS Bibles (50MB+, OSIS XML)
git clone https://github.com/gratis-bible/bible.git

# 1 Enoch (1MB, OSIS XML)
git clone https://github.com/open-canon/1-enoch-osis.git
```

## 📊 COLLECTIONS AT A GLANCE

| Name | Format | Size | License | URL |
|------|--------|------|---------|-----|
| Pseudepigrapha OAP | JSON | 500KB | MIT | https://github.com/tyler-slc/pseudepigrapha |
| KJA Apocrypha | JSON | 5MB | Other | https://github.com/1John419/kja |
| DharmicData | JSON | 100MB | ODbL | https://github.com/bhavykhatri/DharmicData |
| Dead Sea Scrolls | Text-Fabric | 43MB | MIT | https://github.com/ETCBC/dss |
| Church Fathers CSEL | EpiDoc XML | 200MB+ | PD | https://github.com/OpenGreekAndLatin/csel-dev |
| OSIS Bibles | OSIS XML | 50MB+ | Various | https://github.com/gratis-bible/bible |
| 1 Enoch | OSIS XML | 1MB | MIT | https://github.com/open-canon/1-enoch-osis |

## 🔗 WEB-BASED COLLECTIONS

- **Early Christian Writings**: https://www.earlychristianwritings.com (200+ texts)
- **Sacred Texts Archive**: https://sacred-texts.com (1,700+ texts)
- **New Advent**: https://www.newadvent.org/fathers/ (Church Fathers)

## 📚 WHAT'S INCLUDED

✅ **Pseudepigrapha** - 1 Enoch, Jubilees, Testaments, etc.
✅ **Apocrypha** - Tobit, Judith, Wisdom, Sirach, Maccabees, etc.
✅ **Dead Sea Scrolls** - Biblical fragments + non-biblical texts
✅ **Nag Hammadi** - Gnostic texts (Gospel of Thomas, etc.)
✅ **Church Fathers** - 50+ volumes of patristic texts
✅ **Early Christian** - Pre-325 AD texts
✅ **Biblical** - Multiple translations in OSIS format
✅ **Hindu Texts** - Vedas, Ramayana, Mahabharata, Bhagavad Gita

## 🚀 INTEGRATION STEPS

1. **Download** - Run download script
2. **Parse** - Convert JSON/XML to normalized format
3. **Chunk** - Apply semantic chunking (existing Clarus pipeline)
4. **Embed** - Generate embeddings (text-embedding-3-large)
5. **Index** - Store in Qdrant collections
6. **Test** - Validate cross-collection search
7. **Deploy** - Add to production API

## 📖 DOCUMENTATION

- **Full Guide**: `/memory-bank/sacred_texts_collections.md`
- **Findings Report**: `/memory-bank/SACRED_TEXTS_FINDINGS.txt`
- **Download Script**: `/backend/scripts/download_sacred_texts.sh`

## ⚖️ LICENSING

All collections are **freely available** for research/educational use:
- MIT License (most permissive)
- Public Domain
- ODbL (Open Data Commons)
- GPL 3.0

## 💡 TIPS

- **JSON files** are easiest to parse (start here)
- **OSIS XML** is Bible-standard format
- **EpiDoc XML** has scholarly apparatus
- **Text-Fabric** requires Python but has rich annotations
- **Web sources** require scraping but are comprehensive

## ❓ QUESTIONS?

See full documentation in `/memory-bank/sacred_texts_collections.md`
