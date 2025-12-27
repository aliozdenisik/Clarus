"""
Search Mode Comparison

Dual-vector vs Hybrid vs Semantic arama karşılaştırması.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.search import QuranSearcher

# Test queries
TEST_QUERIES = [
    ("sabir ve namaz", 2, 45),   # ASCII yazım
    ("sabır ve namaz", 2, 45),   # Türkçe yazım
    ("rahman rahim", 1, 1),      # Fatiha
    ("Allah yardım", 2, 45),     # Yardım sorgusu
]

def find_rank(results, surah_id, verse_id):
    """Find the rank of a specific verse in results"""
    for i, r in enumerate(results, 1):
        if r.surah_id == surah_id and r.verse_id == verse_id:
            return i
    return -1

def compare_modes():
    print("="*70)
    print("SEARCH MODE COMPARISON")
    print("="*70)
    
    searcher = QuranSearcher()
    
    # Results table
    results_table = []
    
    for query, target_surah, target_verse in TEST_QUERIES:
        print(f"\nQuery: '{query}' → Target: {target_surah}:{target_verse}")
        print("-"*50)
        
        row = {"query": query, "target": f"{target_surah}:{target_verse}"}
        
        # Test each mode
        modes = ["dual-vector", "hybrid", "semantic", "keyword"]
        
        for mode in modes:
            try:
                if mode == "dual-vector":
                    results = searcher.dual_vector_search(query, limit=30)
                elif mode == "hybrid":
                    results = searcher.hybrid_search(query, limit=30)
                elif mode == "semantic":
                    results = searcher.semantic_search(query, limit=30)
                elif mode == "keyword":
                    results = searcher.keyword_search(query, limit=30)
                
                rank = find_rank(results, target_surah, target_verse)
                
                if rank > 0:
                    status = f"#{rank}"
                else:
                    status = "N/F"
                
                row[mode] = rank if rank > 0 else 999
                print(f"  {mode:16}: {status}")
                
            except Exception as e:
                print(f"  {mode:16}: ERROR - {e}")
                row[mode] = 999
        
        results_table.append(row)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Query':<25} {'Target':>10} {'Dual-Vec':>10} {'Hybrid':>10} {'Semantic':>10} {'Keyword':>10}")
    print("-"*75)
    
    for row in results_table:
        q = row['query'][:23]
        t = row['target']
        dv = row.get('dual-vector', 999)
        hy = row.get('hybrid', 999)
        se = row.get('semantic', 999)
        kw = row.get('keyword', 999)
        
        dv_str = f"#{dv}" if dv < 999 else "N/F"
        hy_str = f"#{hy}" if hy < 999 else "N/F"
        se_str = f"#{se}" if se < 999 else "N/F"
        kw_str = f"#{kw}" if kw < 999 else "N/F"
        
        print(f"{q:<25} {t:>10} {dv_str:>10} {hy_str:>10} {se_str:>10} {kw_str:>10}")
    
    # Calculate averages
    print("-"*75)
    
    modes = ['dual-vector', 'hybrid', 'semantic', 'keyword']
    for mode in modes:
        found_count = sum(1 for r in results_table if r.get(mode, 999) < 999)
        avg_rank = sum(r.get(mode, 0) for r in results_table if r.get(mode, 999) < 999)
        avg_rank = avg_rank / found_count if found_count > 0 else float('inf')
        print(f"{mode:16} - Found: {found_count}/{len(results_table)}, Avg Rank: {avg_rank:.1f}")


if __name__ == "__main__":
    compare_modes()
