"""
Test script for QueryEnhancer and SearchEvaluator modules.
Analyzes search quality and identifies gaps.
"""
import os
import sys

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.search import QuranSearcher

print("=" * 60)
print("SEARCH QUALITY ANALYSIS")
print("=" * 60)

# Initialize searcher
print("\n1. Initializing QuranSearcher...")
searcher = QuranSearcher()
print("   OK: QuranSearcher initialized")

# Test queries with expected content
test_queries = [
    ("Allah'in rahmeti", ["rahmet", "merhamet"]),
    ("sabir ve namaz", ["sabir", "namaz", "sabır"]),
    ("cennet ve cehennem", ["cennet", "cehennem"]),
    ("dogru yol", ["yol", "sırat", "doğru"]),
    ("sukur etmek", ["şükr", "sukur", "şükür"]),
]

print("\n2. Analyzing search results...")
print("-" * 60)

analysis_results = []

for query, expected_terms in test_queries:
    print(f"\nQuery: '{query}'")
    
    # Get results from all modes
    hybrid_results = searcher.hybrid_search(query, limit=10)
    semantic_results = searcher.semantic_search(query, limit=10)
    keyword_results = searcher.keyword_search(query, limit=10)
    
    # Analyze quality
    def analyze_results(results, expected):
        if not results:
            return 0, 0
        
        matches = 0
        for r in results:
            text_lower = r.translation.lower()
            if any(term.lower() in text_lower for term in expected):
                matches += 1
        
        return matches, len(results)
    
    hybrid_match, hybrid_total = analyze_results(hybrid_results, expected_terms)
    semantic_match, semantic_total = analyze_results(semantic_results, expected_terms)
    keyword_match, keyword_total = analyze_results(keyword_results, expected_terms)
    
    print(f"  Expected terms: {expected_terms}")
    print(f"  Hybrid:   {hybrid_match}/{hybrid_total} matches ({hybrid_match/hybrid_total*100:.0f}%)")
    print(f"  Semantic: {semantic_match}/{semantic_total} matches ({semantic_match/semantic_total*100:.0f}%)")
    print(f"  Keyword:  {keyword_match}/{keyword_total} matches ({keyword_match/keyword_total*100:.0f}%)")
    
    # Show top 3 hybrid results
    print(f"\n  Top 3 Hybrid Results:")
    for i, r in enumerate(hybrid_results[:3], 1):
        text = r.translation[:60] + "..." if len(r.translation) > 60 else r.translation
        print(f"    {i}. {r.surah_name} {r.surah_id}:{r.verse_id} (score: {r.score:.4f})")
        print(f"       '{text}'")
    
    analysis_results.append({
        "query": query,
        "hybrid_rate": hybrid_match/hybrid_total*100 if hybrid_total > 0 else 0,
        "semantic_rate": semantic_match/semantic_total*100 if semantic_total > 0 else 0,
        "keyword_rate": keyword_match/keyword_total*100 if keyword_total > 0 else 0,
    })

# Mode comparison
print("\n" + "=" * 60)
print("MODE COMPARISON SUMMARY")
print("=" * 60)

print(f"\n{'Query':<25} {'Hybrid':<10} {'Semantic':<10} {'Keyword':<10}")
print("-" * 55)
for r in analysis_results:
    print(f"{r['query']:<25} {r['hybrid_rate']:.0f}%{'':<6} {r['semantic_rate']:.0f}%{'':<6} {r['keyword_rate']:.0f}%")

avg_hybrid = sum(r["hybrid_rate"] for r in analysis_results) / len(analysis_results)
avg_semantic = sum(r["semantic_rate"] for r in analysis_results) / len(analysis_results)
avg_keyword = sum(r["keyword_rate"] for r in analysis_results) / len(analysis_results)

print("-" * 55)
print(f"{'AVERAGE':<25} {avg_hybrid:.0f}%{'':<6} {avg_semantic:.0f}%{'':<6} {avg_keyword:.0f}%")

# Identify issues
print("\n" + "=" * 60)
print("IDENTIFIED GAPS AND ISSUES")
print("=" * 60)

issues = []

# Issue 1: Low match rates
if avg_hybrid < 50:
    issues.append(f"LOW MATCH RATE: Hybrid average is {avg_hybrid:.0f}% (expected >50%)")

# Issue 2: Keyword performs better than hybrid
if avg_keyword > avg_hybrid:
    issues.append(f"KEYWORD OUTPERFORMS HYBRID: Keyword ({avg_keyword:.0f}%) > Hybrid ({avg_hybrid:.0f}%)")

# Issue 3: Check score distribution
print("\n1. Score Distribution Check...")
test_results = searcher.hybrid_search("Allah", limit=10)
scores = [r.score for r in test_results]
print(f"   Min score: {min(scores):.4f}")
print(f"   Max score: {max(scores):.4f}")
print(f"   Score range: {max(scores) - min(scores):.4f}")

if max(scores) - min(scores) < 0.001:
    issues.append("NARROW SCORE RANGE: Results have very similar scores (RRF fusion issue)")

# Issue 4: Check semantic vs keyword overlap
print("\n2. Mode Coverage Analysis...")
query = "Allah'in rahmeti"
sem_ids = set(f"{r.surah_id}:{r.verse_id}" for r in searcher.semantic_search(query, limit=10))
kw_ids = set(f"{r.surah_id}:{r.verse_id}" for r in searcher.keyword_search(query, limit=10))
hybrid_ids = set(f"{r.surah_id}:{r.verse_id}" for r in searcher.hybrid_search(query, limit=10))

only_semantic = sem_ids - kw_ids
only_keyword = kw_ids - sem_ids
overlap = sem_ids & kw_ids
hybrid_unique = hybrid_ids - (sem_ids | kw_ids)

print(f"   Semantic only: {len(only_semantic)} results")
print(f"   Keyword only: {len(only_keyword)} results")
print(f"   Overlap: {len(overlap)} results")
print(f"   In hybrid: {len(hybrid_ids)} total, {len(hybrid_unique)} unique")

# Issue 5: Check if hybrid combines results effectively
in_hybrid_from_sem = len(hybrid_ids & sem_ids)
in_hybrid_from_kw = len(hybrid_ids & kw_ids)
print(f"   Hybrid from semantic: {in_hybrid_from_sem}")
print(f"   Hybrid from keyword: {in_hybrid_from_kw}")

if in_hybrid_from_sem < 3 or in_hybrid_from_kw < 3:
    issues.append("POOR FUSION: Hybrid not effectively combining semantic and keyword results")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if issues:
    print(f"\n{len(issues)} issues/gaps found:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("\nNo critical issues found! Search system is working well.")

print("\n" + "=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)

print("""
1. GROUND TRUTH: Create manual relevance judgments for proper
   evaluation metrics (precision@k, NDCG, MRR)

2. RRF K PARAMETER: Current k=60 may need tuning based on results.
   Try k=2 (original) vs k=60 to compare

3. PREFETCH LIMIT: Increasing prefetch_limit (20->50) may improve
   hybrid result diversity

4. QUERY ENHANCEMENT: Use QueryEnhancer to expand/rewrite queries
   for better recall
""")

print("Test completed.")
