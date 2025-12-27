"""Debug script for 'cinler' search analysis - writes to file"""
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from src.search import QuranSearcher

query = 'cinler'
searcher = QuranSearcher()

# Write to file for clear output
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write(f"Query: '{query}'\n")
    f.write("="*70 + "\n")

    # Test semantic
    f.write("\n" + "="*70 + "\n")
    f.write("1. SEMANTIC SEARCH (Dense only)\n")
    f.write("="*70 + "\n")
    results = searcher.semantic_search(query, limit=10)
    for i, r in enumerate(results, 1):
        has_word = "cinler" in r.translation.lower() or "cin" in r.translation.lower()
        marker = "[✓]" if has_word else "[✗]"
        f.write(f"{i}. {marker} [{r.surah_id}:{r.verse_id}] {r.surah_name} (score={r.score:.4f})\n")
        f.write(f"   {r.translation[:100]}...\n")

    # Test keyword
    f.write("\n" + "="*70 + "\n")
    f.write("2. KEYWORD/BM25 SEARCH (Sparse only)\n")
    f.write("="*70 + "\n")
    results = searcher.keyword_search(query, limit=10)
    for i, r in enumerate(results, 1):
        has_word = "cinler" in r.translation.lower() or "cin" in r.translation.lower()
        marker = "[✓]" if has_word else "[✗]"
        f.write(f"{i}. {marker} [{r.surah_id}:{r.verse_id}] {r.surah_name} (score={r.score:.4f})\n")
        f.write(f"   {r.translation[:100]}...\n")

    # Test hybrid
    f.write("\n" + "="*70 + "\n")
    f.write("3. HYBRID SEARCH (RRF fusion)\n")
    f.write("="*70 + "\n")
    results = searcher.hybrid_search(query, limit=10)
    for i, r in enumerate(results, 1):
        has_word = "cinler" in r.translation.lower() or "cin" in r.translation.lower()
        marker = "[✓]" if has_word else "[✗]"
        f.write(f"{i}. {marker} [{r.surah_id}:{r.verse_id}] {r.surah_name} (score={r.score:.4f})\n")
        f.write(f"   {r.translation[:100]}...\n")

    # Summary
    f.write("\n" + "="*70 + "\n")
    f.write("SUMMARY\n")
    f.write("="*70 + "\n")

    for mode in ["semantic", "keyword", "hybrid"]:
        if mode == "semantic":
            results = searcher.semantic_search(query, limit=30)
        elif mode == "keyword":
            results = searcher.keyword_search(query, limit=30)
        else:
            results = searcher.hybrid_search(query, limit=30)
        
        count = sum(1 for r in results if "cinler" in r.translation.lower() or "cin" in r.translation.lower())
        f.write(f"{mode.upper():12} - Found 'cin/cinler' in {count}/30 results\n")

print("Results written to debug_output.txt")
