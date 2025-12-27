#!/usr/bin/env python3
"""
Comprehensive Test Suite for Quran Hybrid Search Application.
Tests all modules: data_loader, embeddings, indexer, and search.
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import QuranDataLoader, QuranChunk
from src.embeddings import DenseEncoder, SparseEncoder, HybridEncoder
from src.indexer import QuranIndexer
from src.search import QuranSearcher, print_results


def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} | {name}")
    if details:
        print(f"         └─ {details}")


def test_data_loader():
    """Test the QuranDataLoader module"""
    print_header("1. Testing Data Loader Module")
    
    all_passed = True
    loader = QuranDataLoader(data_dir=Path("data"))
    
    # Test 1: Download/cache data
    try:
        path = loader.download_data()
        passed = path.exists()
        print_test("Data download/cache", passed, f"Path: {path}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Data download/cache", False, str(e))
        all_passed = False
    
    # Test 2: Load data
    try:
        data = loader.load_data()
        passed = len(data) == 114
        print_test("Load Quran data", passed, f"Loaded {len(data)} surahs (expected 114)")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Load Quran data", False, str(e))
        all_passed = False
    
    # Test 3: Get stats
    try:
        stats = loader.get_stats()
        passed = (stats['total_surahs'] == 114 and 
                  stats['total_verses'] == 6236 and
                  stats['meccan_surahs'] + stats['medinan_surahs'] == 114)
        details = f"Surahs: {stats['total_surahs']}, Verses: {stats['total_verses']}, Meccan: {stats['meccan_surahs']}, Medinan: {stats['medinan_surahs']}"
        print_test("Get statistics", passed, details)
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Get statistics", False, str(e))
        all_passed = False
    
    # Test 4: Create chunks
    try:
        chunks = loader.create_chunks(show_progress=False)
        passed = len(chunks) == 6236
        print_test("Create chunks", passed, f"Created {len(chunks)} chunks (expected 6236)")
        all_passed = all_passed and passed
        
        # Check chunk structure
        if chunks:
            sample = chunks[0]
            has_all_fields = all([
                sample.id, sample.surah_name, sample.translation,
                sample.arabic_text, sample.surah_transliteration
            ])
            print_test("Chunk structure valid", has_all_fields, f"Sample: {sample.id} - {sample.surah_name}")
            all_passed = all_passed and has_all_fields
    except Exception as e:
        print_test("Create chunks", False, str(e))
        all_passed = False
    
    return all_passed, chunks[:50] if 'chunks' in dir() else []


def test_embeddings():
    """Test the embeddings module"""
    print_header("2. Testing Embeddings Module")
    
    all_passed = True
    test_text = "Rahman ve Rahim olan Allah'ın adıyla"
    test_texts = [
        "Rahman ve Rahim olan Allah'ın adıyla",
        "Hamd alemlerin Rabbi Allah'a mahsustur",
        "O, Rahman ve Rahim'dir"
    ]
    
    # Test 1: Dense encoder single
    try:
        dense = DenseEncoder()
        vec = dense.encode(test_text)
        passed = len(vec) == 4096
        print_test("Dense encoder (single)", passed, f"Dimension: {len(vec)} (expected 4096)")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Dense encoder (single)", False, str(e))
        all_passed = False
    
    # Test 2: Dense encoder batch
    try:
        vecs = dense.encode_batch(test_texts, show_progress=False)
        passed = len(vecs) == 3 and all(len(v) == 4096 for v in vecs)
        print_test("Dense encoder (batch)", passed, f"Encoded {len(vecs)} texts with dim 4096")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Dense encoder (batch)", False, str(e))
        all_passed = False
    
    # Test 3: Sparse encoder single
    try:
        sparse = SparseEncoder()
        indices, values = sparse.encode(test_text)
        passed = len(indices) > 0 and len(indices) == len(values)
        print_test("Sparse encoder (single)", passed, f"Non-zero elements: {len(indices)}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Sparse encoder (single)", False, str(e))
        all_passed = False
    
    # Test 4: Sparse encoder batch
    try:
        sparse_vecs = sparse.encode_batch(test_texts)
        passed = len(sparse_vecs) == 3
        print_test("Sparse encoder (batch)", passed, f"Encoded {len(sparse_vecs)} texts")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Sparse encoder (batch)", False, str(e))
        all_passed = False
    
    # Test 5: Sparse query embed
    try:
        q_indices, q_values = sparse.query_embed(test_text)
        passed = len(q_indices) > 0
        print_test("Sparse query embed", passed, f"Query non-zero elements: {len(q_indices)}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Sparse query embed", False, str(e))
        all_passed = False
    
    # Test 6: Hybrid encoder
    try:
        hybrid = HybridEncoder()
        d, s = hybrid.encode(test_text)
        passed = len(d) == 4096 and len(s[0]) > 0
        print_test("Hybrid encoder (single)", passed, f"Dense: 4096, Sparse non-zeros: {len(s[0])}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Hybrid encoder (single)", False, str(e))
        all_passed = False
    
    return all_passed


def test_indexer(chunks):
    """Test the indexer module"""
    print_header("3. Testing Indexer Module")
    
    all_passed = True
    
    # Test 1: Initialize in-memory indexer
    try:
        indexer = QuranIndexer(in_memory=True)
        passed = indexer.client is not None
        print_test("Initialize in-memory indexer", passed)
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Initialize in-memory indexer", False, str(e))
        return False, None
    
    # Test 2: Create collection
    try:
        created = indexer.create_collection(recreate=True)
        passed = created == True
        print_test("Create collection", passed, "Collection 'quran_tr' created")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Create collection", False, str(e))
        all_passed = False
    
    # Test 3: Index chunks
    try:
        count = indexer.index_chunks(chunks, batch_size=25, show_progress=False)
        passed = count == len(chunks)
        print_test("Index chunks", passed, f"Indexed {count}/{len(chunks)} chunks")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Index chunks", False, str(e))
        all_passed = False
    
    # Test 4: Get collection info
    try:
        info = indexer.get_collection_info()
        passed = info['points_count'] == len(chunks)
        print_test("Collection info", passed, f"Points: {info['points_count']}, Status: {info['status']}")
        all_passed = all_passed and passed
    except Exception as e:
        print_test("Collection info", False, str(e))
        all_passed = False
    
    return all_passed, indexer


def test_search(indexer):
    """Test the search module"""
    print_header("4. Testing Search Module")
    
    all_passed = True
    searcher = QuranSearcher(client=indexer.client)
    
    test_queries = [
        ("Allah'ın rahmeti", "Mercy/Rahman query"),
        ("namaz", "Prayer query"),
        ("doğru yol", "Right path query"),
    ]
    
    # Test 1: Semantic search
    print("\n  [Semantic Search Tests]")
    for query, desc in test_queries:
        try:
            results = searcher.semantic_search(query, limit=3)
            passed = len(results) > 0
            if passed:
                top = results[0]
                print_test(f"Semantic: {desc}", passed, f"Top: [{top.surah_id}:{top.verse_id}] score={top.score:.3f}")
            else:
                print_test(f"Semantic: {desc}", False, "No results")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"Semantic: {desc}", False, str(e))
            all_passed = False
    
    # Test 2: Keyword search
    print("\n  [Keyword/BM25 Search Tests]")
    for query, desc in test_queries:
        try:
            results = searcher.keyword_search(query, limit=3)
            passed = len(results) > 0
            if passed:
                top = results[0]
                print_test(f"Keyword: {desc}", passed, f"Top: [{top.surah_id}:{top.verse_id}] score={top.score:.3f}")
            else:
                print_test(f"Keyword: {desc}", False, "No results")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"Keyword: {desc}", False, str(e))
            all_passed = False
    
    # Test 3: Hybrid search
    print("\n  [Hybrid Search Tests]")
    for query, desc in test_queries:
        try:
            results = searcher.hybrid_search(query, limit=3)
            passed = len(results) > 0
            if passed:
                top = results[0]
                print_test(f"Hybrid: {desc}", passed, f"Top: [{top.surah_id}:{top.verse_id}] score={top.score:.3f}")
            else:
                print_test(f"Hybrid: {desc}", False, "No results")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"Hybrid: {desc}", False, str(e))
            all_passed = False
    
    # Test 4: Unified search interface
    print("\n  [Unified Search Interface Tests]")
    for mode in ["hybrid", "semantic", "keyword"]:
        try:
            results = searcher.search("Allah", mode=mode, limit=3)
            passed = len(results) > 0
            print_test(f"Unified search (mode={mode})", passed, f"Found {len(results)} results")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"Unified search (mode={mode})", False, str(e))
            all_passed = False
    
    return all_passed


def test_cli():
    """Test CLI help command"""
    print_header("5. Testing CLI Interface")
    
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        passed = result.returncode == 0 and "Quran Hybrid Search" in result.stdout
        print_test("CLI help command", passed, "CLI is accessible and shows help")
        return passed
    except Exception as e:
        print_test("CLI help command", False, str(e))
        return False


def main():
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE TEST SUITE - Quran Hybrid Search Application")
    print("=" * 70)
    
    results = {}
    
    # Run all tests
    data_passed, chunks = test_data_loader()
    results["Data Loader"] = data_passed
    
    embed_passed = test_embeddings()
    results["Embeddings"] = embed_passed
    
    if chunks:
        index_passed, indexer = test_indexer(chunks)
        results["Indexer"] = index_passed
        
        if indexer:
            search_passed = test_search(indexer)
            results["Search"] = search_passed
    
    cli_passed = test_cli()
    results["CLI"] = cli_passed
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for module, status in results.items():
        icon = "[PASS]" if status else "[FAIL]"
        print(f"  {icon} {module}")
    
    print(f"\n  Total: {passed}/{total} modules passed")
    
    if passed == total:
        print("\n  ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("\n  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
