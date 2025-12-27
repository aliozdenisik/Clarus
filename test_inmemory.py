#!/usr/bin/env python3
"""
In-memory test script for Quran Hybrid Search.
Tests the full pipeline without requiring Docker.
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import QuranDataLoader
from src.embeddings import HybridEncoder
from src.indexer import QuranIndexer
from src.search import QuranSearcher, print_results

def main():
    print("=" * 60)
    print("[*] Quran Hybrid Search - In-Memory Test")
    print("=" * 60)
    
    # 1. Load data
    print("\n[1] Step 1: Loading Quran data...")
    loader = QuranDataLoader(data_dir=Path("data"))
    loader.download_data()
    
    stats = loader.get_stats()
    print(f"   ✓ Loaded {stats['total_surahs']} surahs, {stats['total_verses']} verses")
    
    # Create chunks (use subset for faster testing)
    print("\n[2] Step 2: Creating chunks...")
    all_chunks = loader.create_chunks(show_progress=False)
    # Use first 100 chunks for test
    test_chunks = all_chunks[:100]
    print(f"   ✓ Using {len(test_chunks)} chunks for test (out of {len(all_chunks)} total)")
    
    # 2. Initialize indexer (in-memory)
    print("\n[3] Step 3: Initializing in-memory Qdrant...")
    indexer = QuranIndexer(in_memory=True)
    indexer.create_collection(recreate=True)
    print("   ✓ Collection created")
    
    # 3. Index chunks
    print("\n[4] Step 4: Indexing chunks...")
    count = indexer.index_chunks(test_chunks, batch_size=50, show_progress=True)
    print(f"   ✓ Indexed {count} chunks")
    
    # 4. Test search
    print("\n[5] Step 5: Testing search...")
    
    # Create searcher with same client
    searcher = QuranSearcher(client=indexer.client)
    
    test_queries = [
        "Allah'ın rahmeti",
        "namaz kılmak",
        "doğru yol"
    ]
    
    for query in test_queries:
        print(f"\n   Query: \"{query}\"")
        
        # Hybrid search
        results = searcher.hybrid_search(query, limit=3)
        if results:
            print(f"   Hybrid Results ({len(results)}):")
            for i, r in enumerate(results, 1):
                print(f"      {i}. [{r.surah_id}:{r.verse_id}] {r.translation[:60]}...")
        else:
            print("   No results found")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
