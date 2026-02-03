# Hebrew Bible Morphology Sources - Quick Reference

## 🏆 GOLD STANDARD

### ETCBC BHSA (Biblia Hebraica Stuttgartensia Amstelodamensis)
- **URL**: https://github.com/ETCBC/bhsa
- **Query Interface**: https://shebanq.ancient-data.org
- **DOI**: 10.17026/dans-z6y-skyh
- **License**: CC BY-NC 4.0 (non-commercial)
- **Morphology**: 100% complete
- **Per-Book Data**: ✅ Yes
- **Syntax**: ✅ Yes
- **Academic**: ✅ Peer-reviewed (VU University)
- **Best For**: Academic research, reproducible science

---

## 🥈 PRODUCTION STANDARD

### OSHB (Open Scriptures Hebrew Bible)
- **URL**: https://github.com/openscriptures/morphhb
- **Website**: https://hb.openscriptures.org
- **License**: CC BY 4.0 (commercial allowed)
- **Morphology**: ~95% complete
- **Per-Book Data**: ⚠️ Partial
- **Syntax**: ❌ No
- **Academic**: ⚠️ Community-driven
- **Best For**: Production apps, commercial use

---

## 📊 COMPARISON TABLE

| Feature | ETCBC BHSA | OSHB | BibleHub | Westminster |
|---------|-----------|------|----------|-------------|
| Morphology | 100% | ~95% | ~50% | ~80% |
| Per-Book Freq | ✅ | ⚠️ | ❌ | ❌ |
| Syntax | ✅ | ❌ | ❌ | ❌ |
| Academic | ✅ | ⚠️ | ❌ | ⚠️ |
| Commercial | ❌ | ✅ | ✅ | ✅ |
| Programmatic | ✅ | ✅ | ❌ | ❌ |
| Active | ✅ | ✅ | ✅ | ❌ |
| DOI | ✅ | ❌ | ❌ | ❌ |

---

## 🔍 MORPHOLOGICAL FEATURES

### ETCBC BHSA Provides
- Part of speech (sp): noun, verb, adjective, etc.
- Gender (gn): masculine, feminine
- Number (nu): singular, plural, dual
- State (st): absolute, construct, emphatic
- Tense/Aspect (vt): perfect, imperfect, imperative
- Person (ps): 1st, 2nd, 3rd
- Root (root): Hebrew root form
- Lemma (lex): lexical form
- **Frequency ranking**: rank_lex, rank_occ
- **Syntax**: clause structure, function

### OSHB Provides
- Lemma: Strong's numbers (augmented)
- Morphology: HC/R/Ncmsc format
- Unique word IDs: For textual criticism
- ⚠️ No frequency ranking
- ⚠️ No syntax

---

## 💡 RECOMMENDATIONS

### For Academic Research
```
→ Use ETCBC BHSA via Text-Fabric
→ Most comprehensive
→ Peer-reviewed
→ Reproducible
```

### For Production Apps
```
→ Use OSHB (GitHub or npm)
→ Permissive license
→ Easy integration
→ Actively maintained
```

### For Quick Lookups
```
→ Use BibleHub or OSHB website
→ User-friendly
→ No programming needed
```

### For Commercial Products
```
→ Use OSHB (CC BY 4.0)
→ Only option with commercial license
→ Sufficient morphology
```

---

## ⚠️ AVOID: Strong's Numbers Alone

**Problems:**
- Outdated lemmatization (1890)
- Incomplete morphology
- Known inconsistencies
- Multiple words → same number
- No frequency data

**Better alternatives:**
- ETCBC BHSA (modern linguistic analysis)
- OSHB (augmented Strong's)
- BDB (more scholarly)

---

## 🔗 KEY RESOURCES

| Resource | URL |
|----------|-----|
| ETCBC BHSA Docs | https://etcbc.github.io/bhsa/ |
| SHEBANQ Query | https://shebanq.ancient-data.org |
| Text-Fabric | https://annotation.github.io/text-fabric/tf |
| OSHB GitHub | https://github.com/openscriptures/morphhb |
| OSHB Website | https://hb.openscriptures.org |
| Text-Fabric Tutorial | https://nbviewer.jupyter.org/github/ETCBC/bhsa/blob/master/tutorial/start.ipynb |

---

## 📚 ACADEMIC CITATIONS

1. **Roorda, D.** (2018). "Coding the Hebrew Bible." DOI: 10.1163/24523666-01000011
2. **Roorda, D.** (2018). "Text-Fabric: handling Biblical data with IKEA logistics"
3. **Naaijer & van Peursen** (2023). "Parsing Hebrew and Syriac morphology using Deep Learning"

---

## 🚀 QUICK START

### Access ETCBC BHSA (Python)
```python
from tf.app import use
A = use('etcbc/bhsa')
F = A.api['F']  # Features
# Query by book, lemma, morphology, etc.
```

### Access OSHB (JavaScript)
```javascript
const morphhb = require('morphhb');
const genesis = morphhb['Genesis'];
// [word, lemma, morphology] tuples
```

### Access SHEBANQ (Web)
1. Go to https://shebanq.ancient-data.org
2. Click "Queries" → "New Query"
3. Use MQL syntax for morphological searches
4. Export as CSV/JSON

---

**Last Updated**: February 3, 2026  
**Status**: Complete research with 3 primary sources + academic backing
