# COMPREHENSIVE GUIDE: FREELY AVAILABLE DIGITAL SACRED TEXT COLLECTIONS

**Last Updated:** February 2, 2026
**Status:** Complete inventory with download links and format details

---

## TABLE OF CONTENTS
1. [Pseudepigrapha & Apocrypha](#pseudepigrapha--apocrypha)
2. [Dead Sea Scrolls](#dead-sea-scrolls)
3. [Nag Hammadi Library](#nag-hammadi-library)
4. [Church Fathers](#church-fathers)
5. [Early Christian Texts](#early-christian-texts)
6. [Biblical Texts](#biblical-texts)
7. [Hindu Sacred Texts](#hindu-sacred-texts)
8. [Web-Based Collections](#web-based-collections)
9. [Download Instructions](#download-instructions)

---

## PSEUDEPIGRAPHA & APOCRYPHA

### 1. Online Critical Pseudepigrapha (OCP)
**Repository:** https://github.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha
**License:** GPL 3.0
**Format:** Web application (Python/web2py)
**Contents:** Comprehensive pseudepigrapha database with scholarly apparatus
**Download:** `git clone https://github.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha.git`
**Data Access:** Via web interface; raw data in database backend
**Status:** Active development

### 2. Online Apocrypha and Pseudepigrapha (OAP) Data Repository
**Repository:** https://github.com/tyler-slc/pseudepigrapha
**License:** MIT
**Format:** JSON
**Contents:** 
- CAVT.json - Comprehensive catalog of pseudepigrapha with multilingual names
- References to scholarly works
- Version information and manuscript details
**Download:** `git clone https://github.com/tyler-slc/pseudepigrapha.git`
**File Size:** ~500KB
**Key Data:** CAVT numbering system, Greek/Latin/English names, scholarly references

### 3. King James Apocrypha (KJA)
**Repository:** https://github.com/1John419/kja
**License:** Other (check repo)
**Format:** JSON
**Contents:** Complete KJV Apocrypha with verse-by-verse data
**Download:** `git clone https://github.com/1John419/kja.git`
**Files:**
- `/json/kja.json` - Full apocrypha text
- `/json/kja_lists.json` - Index and metadata
**Structure:** Verse-indexed JSON with book/chapter/verse references

---

## DEAD SEA SCROLLS

### 1. Dead Sea Scrolls in Text-Fabric Format
**Repository:** https://github.com/ETCBC/dss
**License:** MIT
**Format:** Text-Fabric (TF) format + Jupyter notebooks
**Contents:** 
- Biblical DSS (Hebrew Bible fragments)
- Non-biblical DSS texts
- Linguistic annotations and morphological data
**Download:** `git clone https://github.com/ETCBC/dss.git`
**Size:** ~911 files, 43MB
**Data Structure:**
```
/parallels/tf/1.8.3/  - Text-Fabric format
/app/                 - Processing applications
/tutorial/            - Jupyter notebooks for analysis
```
**Citation:** DOI: 10.5281/zenodo.168822533
**Features:**
- Morphological analysis
- Linguistic annotations
- Parallel text alignment
- Python/Jupyter ecosystem

### 2. BiblicalDSS (JSON Format)
**Repository:** https://github.com/brando130/BiblicalDSS
**License:** Other
**Format:** JSON
**Contents:** Biblical Dead Sea Scrolls in machine-readable JSON
**Download:** `git clone https://github.com/brando130/BiblicalDSS.git`

---

## NAG HAMMADI LIBRARY

### 1. Nag Hammadi Scraping & Analysis
**Repository:** https://github.com/conradbm/nag_hammadi
**License:** Unspecified
**Format:** Jupyter Notebooks + data files
**Contents:** 
- Scraped Nag Hammadi texts
- NLP analysis
- Comparison with canonical Bible
**Download:** `git clone https://github.com/conradbm/nag_hammadi.git`
**Features:** Machine learning analysis, text comparison

### 2. Bible vs Nag Hammadi Analysis
**Repository:** https://github.com/TraxData313/Bible-vs-NagHammadi-match-score
**License:** Unspecified
**Format:** Jupyter Notebooks
**Contents:** NLP-based comparison of Nag Hammadi texts with canonical Bible
**Download:** `git clone https://github.com/TraxData313/Bible-vs-NagHammadi-match-score.git`

---

## CHURCH FATHERS

### 1. Corpus Scriptorum Ecclesiasticorum Latinorum (CSEL)
**Repository:** https://github.com/OpenGreekAndLatin/csel-dev
**License:** Public Domain (machine-corrected)
**Format:** EpiDoc XML (TEI-compliant)
**Contents:** 
- Latin Church Fathers texts
- 50+ volumes of CSEL collection
- Scholarly apparatus
**Download:** `git clone https://github.com/OpenGreekAndLatin/csel-dev.git`
**Size:** ~1,111 files, 200MB+
**File Structure:**
```
/Volumes/CSEL01.xml
/Volumes/CSEL09_2.xml
/Volumes/CSEL15.xml
... (up to CSEL57)
/UniKonstanz/  - Enhanced versions with improved numbering
```
**Features:**
- CTS-compliant URIs
- Archive.org links to original scans
- Perseus Catalog URIs
- Enhanced locus numbering (UniKonstanz versions)

### 2. Church Fathers Search Engine
**Repository:** https://github.com/pauldavidfisher/church-fathers-search
**License:** MIT
**Format:** Python application with n-gram indexing
**Contents:** Searchable Church Fathers database
**Download:** `git clone https://github.com/pauldavidfisher/church-fathers-search.git`

### 3. Church Fathers Schaff Set
**Repository:** https://github.com/kyle-mirich/church-fathers-schaff-set
**License:** Unspecified
**Format:** HTML
**Contents:** Complete CCEL Church Fathers collection
**Download:** `git clone https://github.com/kyle-mirich/church-fathers-schaff-set.git`

---

## EARLY CHRISTIAN TEXTS

### 1. Early Christian Writings Catalog
**Website:** https://www.earlychristianwritings.com
**Format:** HTML + downloadable CD
**Contents:** 
- New Testament (canonical)
- Apocrypha (50+ texts)
- Gnostic texts (30+ texts)
- Church Fathers (100+ authors)
- Non-Christian references
**Texts Included:**
- Gospel of Thomas
- Gospel of Mary
- Gospel of Peter
- Apocryphon of John
- Nag Hammadi library texts
- Acts of various apostles
- Epistles and martyrologies
**Download:** CD available for purchase; HTML browsable online
**Coverage:** 30-400 AD texts

### 2. Early Christian Writings GitHub Catalog
**Repository:** https://github.com/Mallioch/early-christian-texts
**License:** Unspecified
**Format:** Markdown/links
**Contents:** Curated catalog of early Christian text editions
**Download:** `git clone https://github.com/Mallioch/early-christian-texts.git`

---

## BIBLICAL TEXTS

### 1. OSIS Bibles Collection
**Repository:** https://github.com/gratis-bible/bible
**License:** Freely licensed (various)
**Format:** OSIS XML (standard Bible format)
**Contents:** Multiple Bible translations in OSIS format
**Download:** `git clone https://github.com/gratis-bible/bible.git`
**File Structure:**
```
/en/  - English translations
/af/  - Afrikaans
/ar/  - Arabic
/bg/  - Bulgarian
/cs/  - Czech
/de/  - German
/es/  - Spanish
/fr/  - French
/he/  - Hebrew
... (38+ language directories)
```
**Features:**
- CTS-compliant
- Multiple translation versions
- Separate branch with split XML by book
- AJAX-friendly format available

### 2. 1 Enoch in OSIS Format
**Repository:** https://github.com/open-canon/1-enoch-osis
**License:** MIT
**Format:** OSIS XML
**Contents:** R.H. Charles's translation of 1 Enoch
**Download:** `git clone https://github.com/open-canon/1-enoch-osis.git`
**File:** `/1-enoch.xml` (complete text)
**Translation:** R.H. Charles (public domain)

### 3. Free Bible API
**Repository:** https://github.com/jakecyr/freebibleapi
**License:** MIT
**Format:** REST API + Node.js library
**Contents:** Queryable biblical text database
**Download:** `git clone https://github.com/jakecyr/freebibleapi.git`
**Usage:** Node.js library for programmatic access

---

## HINDU SACRED TEXTS

### 1. DharmicData - Comprehensive Hindu Texts
**Repository:** https://github.com/bhavykhatri/DharmicData
**License:** Open Data Commons Open Database License (ODbL)
**Format:** JSON
**Contents:**
- Ramcharitmanas (7 काण्ड) - ~10,000 chaupais
- Srimad Bhagavad Gita (18 chapters) - 700 verses
- Mahabharata (18 books) - ~100,000 shlokas
- Valmiki Ramayana (7 kaands) - ~24,000 shlokas
- Rigveda (10 mandalas) - 10,000+ hymns
- Yajurveda (2 samhitas) - ~3,900 verses
- Atharvaveda (20 kaandas) - ~6,000 verses
**Download:** `git clone https://github.com/bhavykhatri/DharmicData.git`
**Size:** ~100MB
**File Structure:**
```
/Ramcharitmanas/
  - 1_बाल_काण्ड_data.json
  - 2_अयोध्या_काण्ड_data.json
  ... (7 files total)
/SrimadBhagvadGita/
  - bhagavad_gita_chapter_1.json
  ... (18 files)
/Mahabharata/
  - (18 books)
/ValmikiRamayana/
  - 1_balakanda.json
  ... (7 kaands)
/Rigveda/
  - rigveda_mandala_1.json
  ... (10 mandalas)
/Yajurveda/
  - vajasaneyi_madhyandina_samhita.json
  - vajasaneyi_kanva_samhita_chapters.json
/AtharvaVeda/
  - (20 kaandas)
```
**Sources:**
- IIT Kanpur Ramcharitmanas Project
- Gita Supersite by IIT Kanpur
- Vedic Heritage Portal
- Sacred Texts Mahabharata
**Features:**
- Structured JSON format
- Verse-by-verse organization
- Multilingual support (Sanskrit + English)
- Well-documented metadata

---

## WEB-BASED COLLECTIONS

### 1. Internet Sacred Text Archive (ISTA)
**Website:** https://sacred-texts.com
**Format:** HTML + downloadable collections
**Contents:**
- Bible (multiple translations)
- Apocrypha
- Gnosticism texts
- Church Fathers
- Eastern religions
- Mythology
- Esoteric texts
**Download:** 
- Online browsing: Free
- ISTA Flash Drive 9.0: ~1,700 books (commercial)
- Individual text downloads: Available
**Coverage:** Comprehensive multi-tradition archive

### 2. Early Christian Writings
**Website:** https://www.earlychristianwritings.com
**Format:** HTML + CD
**Contents:** 
- 200+ early Christian texts
- Dated chronologically (30-400 AD)
- Scholarly commentary
- Cross-references
**Texts Available:**
- All canonical NT books
- 50+ apocryphal gospels and acts
- 30+ gnostic texts
- 100+ church fathers
- Non-Christian references (Josephus, Tacitus, etc.)
**Download:** CD available; online browsable

### 3. New Advent - Catholic Encyclopedia & Church Fathers
**Website:** https://www.newadvent.org/fathers/
**Format:** HTML
**Contents:**
- Complete Church Fathers collection
- Catholic Encyclopedia
- Bible (Douay-Rheims)
**Coverage:** Comprehensive patristic texts
**Download:** Browsable online; some texts downloadable

### 4. Wesley Center Online
**Website:** https://www.wesleycenter.emory.edu/
**Format:** HTML
**Contents:**
- Non-canonical Christian texts
- Early Methodist texts
- Apocryphal gospels
- Pseudepigrapha
**Download:** Online browsable

---

## DOWNLOAD INSTRUCTIONS

### Method 1: GitHub Clone (Recommended for bulk data)
```bash
# Clone repository
git clone https://github.com/[owner]/[repo].git

# Clone with depth (faster for large repos)
git clone --depth 1 https://github.com/[owner]/[repo].git

# Clone specific branch
git clone -b [branch] https://github.com/[owner]/[repo].git
```

### Method 2: Direct Download
```bash
# Download as ZIP
wget https://github.com/[owner]/[repo]/archive/refs/heads/main.zip

# Extract
unzip main.zip
```

### Method 3: GitHub API
```bash
# Get raw file
curl -O https://raw.githubusercontent.com/[owner]/[repo]/main/[filepath]

# Get all files in directory
curl -s https://api.github.com/repos/[owner]/[repo]/contents/[directory] | \
  grep '"download_url"' | cut -d '"' -f 4 | xargs -n 1 curl -O
```

### Method 4: Web Scraping (for HTML sites)
```bash
# Using wget
wget -r -A.html https://www.earlychristianwritings.com

# Using curl
curl -s https://sacred-texts.com/[path] > output.html
```

---

## QUICK REFERENCE TABLE

| Collection | Format | Size | License | Download |
|-----------|--------|------|---------|----------|
| OAP Pseudepigrapha | JSON | 500KB | MIT | `git clone https://github.com/tyler-slc/pseudepigrapha.git` |
| Dead Sea Scrolls | Text-Fabric | 43MB | MIT | `git clone https://github.com/ETCBC/dss.git` |
| Church Fathers CSEL | EpiDoc XML | 200MB+ | Public Domain | `git clone https://github.com/OpenGreekAndLatin/csel-dev.git` |
| OSIS Bibles | OSIS XML | 50MB+ | Various | `git clone https://github.com/gratis-bible/bible.git` |
| 1 Enoch | OSIS XML | 1MB | MIT | `git clone https://github.com/open-canon/1-enoch-osis.git` |
| DharmicData | JSON | 100MB | ODbL | `git clone https://github.com/bhavykhatri/DharmicData.git` |
| KJA Apocrypha | JSON | 5MB | Other | `git clone https://github.com/1John419/kja.git` |

---

## INTEGRATION RECOMMENDATIONS

### For Your Clarus Project:
1. **Pseudepigrapha:** Use `tyler-slc/pseudepigrapha` (JSON, MIT license)
2. **Apocrypha:** Use `1John419/kja` (JSON, structured)
3. **Church Fathers:** Use `OpenGreekAndLatin/csel-dev` (XML, comprehensive)
4. **Dead Sea Scrolls:** Use `ETCBC/dss` (Text-Fabric, scholarly)
5. **Early Christian:** Scrape `earlychristianwritings.com` or use `Mallioch/early-christian-texts`

### Data Pipeline:
```
GitHub Repos (JSON/XML) 
  ↓
Parse & normalize format
  ↓
Semantic chunking (existing Clarus pipeline)
  ↓
Embedding generation
  ↓
Qdrant indexing
```

---

## NOTES

- All repositories are publicly accessible and free to download
- Most use permissive licenses (MIT, GPL, ODbL, Public Domain)
- Formats are standardized (JSON, XML, OSIS) for easy integration
- Web-based collections require scraping or manual download
- Text-Fabric format (DSS) requires Python ecosystem but provides rich annotations
- OSIS format is Bible-standard and widely supported

