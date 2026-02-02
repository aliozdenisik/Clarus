#!/bin/bash
# Sacred Texts Bulk Download Script
# Downloads all major freely available sacred text collections

set -e

OUTPUT_DIR="${1:-.}/sacred_texts_collections"
mkdir -p "$OUTPUT_DIR"

echo "📚 Sacred Texts Collection Downloader"
echo "======================================"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Function to clone with error handling
clone_repo() {
    local name=$1
    local url=$2
    local dir="$OUTPUT_DIR/$name"
    
    echo "📥 Downloading: $name"
    if git clone --depth 1 "$url" "$dir" 2>/dev/null; then
        echo "   ✅ Success"
    else
        echo "   ⚠️  Failed (may already exist)"
    fi
}

# Pseudepigrapha & Apocrypha
echo ""
echo "=== PSEUDEPIGRAPHA & APOCRYPHA ==="
clone_repo "pseudepigrapha_oap" "https://github.com/tyler-slc/pseudepigrapha.git"
clone_repo "kja_apocrypha" "https://github.com/1John419/kja.git"
clone_repo "ocp_pseudepigrapha" "https://github.com/OnlineCriticalPseudepigrapha/Online-Critical-Pseudepigrapha.git"

# Dead Sea Scrolls
echo ""
echo "=== DEAD SEA SCROLLS ==="
clone_repo "dss_textfabric" "https://github.com/ETCBC/dss.git"
clone_repo "dss_biblical_json" "https://github.com/brando130/BiblicalDSS.git"

# Nag Hammadi
echo ""
echo "=== NAG HAMMADI LIBRARY ==="
clone_repo "nag_hammadi_analysis" "https://github.com/conradbm/nag_hammadi.git"

# Church Fathers
echo ""
echo "=== CHURCH FATHERS ==="
clone_repo "csel_church_fathers" "https://github.com/OpenGreekAndLatin/csel-dev.git"
clone_repo "church_fathers_search" "https://github.com/pauldavidfisher/church-fathers-search.git"
clone_repo "church_fathers_schaff" "https://github.com/kyle-mirich/church-fathers-schaff-set.git"

# Early Christian Texts
echo ""
echo "=== EARLY CHRISTIAN TEXTS ==="
clone_repo "early_christian_catalog" "https://github.com/Mallioch/early-christian-texts.git"

# Biblical Texts
echo ""
echo "=== BIBLICAL TEXTS ==="
clone_repo "osis_bibles" "https://github.com/gratis-bible/bible.git"
clone_repo "1_enoch_osis" "https://github.com/open-canon/1-enoch-osis.git"
clone_repo "free_bible_api" "https://github.com/jakecyr/freebibleapi.git"

# Hindu Sacred Texts
echo ""
echo "=== HINDU SACRED TEXTS ==="
clone_repo "dharmic_data" "https://github.com/bhavykhatri/DharmicData.git"

echo ""
echo "======================================"
echo "✅ Download complete!"
echo ""
echo "📊 Summary:"
find "$OUTPUT_DIR" -maxdepth 1 -type d ! -name "sacred_texts_collections" | wc -l | xargs echo "   Collections downloaded:"
du -sh "$OUTPUT_DIR" | awk '{print "   Total size: " $1}'
echo ""
echo "📖 Next steps:"
echo "   1. Review /memory-bank/sacred_texts_collections.md"
echo "   2. Parse JSON/XML files into normalized format"
echo "   3. Integrate with Clarus semantic chunking pipeline"
echo "   4. Generate embeddings and index in Qdrant"
