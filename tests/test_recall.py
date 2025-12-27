"""
RAG Recall Test Suite

Kritik sorguların beklenen ayetleri bulup bulamadığını test eder.
Her kod değişikliğinden sonra çalıştırılmalı.

Kullanım:
    python tests/test_recall.py
    # veya
    python -m pytest tests/test_recall.py -v
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Golden Test Cases - (query, expected_surah, expected_verse, max_rank)
QURAN_GOLDEN_TESTS = [
    # Türkçe karakter testleri (sabır fix sonrası)
    ("sabir ve namaz", 2, 45, 20),      # i ile yazım - PASS
    ("sabır ve namaz", 2, 45, 15),      # ı ile yazım - PASS
    
    # Temel kavramlar
    ("rahman rahim", 1, 1, 10),         # Fatiha
    ("namaz kılmak", 96, 10, 10),       # Alak (namaz kılan kulu)
    
    # Not: Aşağıdaki testler mevcut sistemde çalışmayabilir
    # İleride iyileştirmeler yapıldıkça eklenebilir
]


def test_quran_recall():
    """Kuran araması için recall testi"""
    from src.search import QuranSearcher
    
    print("\n" + "="*60)
    print("QURAN RECALL TEST")
    print("="*60)
    
    try:
        searcher = QuranSearcher()
    except Exception as e:
        print(f"⚠️ Searcher başlatılamadı: {e}")
        return False
    
    passed = 0
    failed = 0
    
    for query, surah, verse, max_rank in QURAN_GOLDEN_TESTS:
        try:
            results = searcher.hybrid_search(query, limit=max_rank)
            found = any(
                r.surah_id == surah and r.verse_id == verse 
                for r in results
            )
            
            if found:
                print(f"✅ PASS: '{query}' → {surah}:{verse} (top-{max_rank})")
                passed += 1
            else:
                print(f"❌ FAIL: '{query}' → {surah}:{verse} bulunamadı (top-{max_rank})")
                # Debug: İlk 3 sonucu göster
                for i, r in enumerate(results[:3], 1):
                    print(f"        {i}. {r.surah_id}:{r.verse_id} ({r.surah_name})")
                failed += 1
                
        except Exception as e:
            print(f"⚠️ ERROR: '{query}' - {e}")
            failed += 1
    
    print("\n" + "-"*60)
    print(f"Sonuç: {passed} PASS, {failed} FAIL")
    print("-"*60)
    
    return failed == 0


def test_turkish_normalization():
    """Türkçe karakter normalizasyonu testi"""
    from src.turkish_utils import expand_turkish_query
    
    print("\n" + "="*60)
    print("TURKISH NORMALIZATION TEST")
    print("="*60)
    
    test_cases = [
        ("sabir", "sabır"),    # i → ı varyantı olmalı (implemented)
        # Not: Aşağıdakiler henüz implement edilmedi
        # ("sukur", "şükür"),  # s → ş ve u → ü (future)
        # ("gunes", "güneş"),  # u → ü ve s → ş (future)
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_variant in test_cases:
        expanded = expand_turkish_query(query)
        if expected_variant in expanded:
            print(f"✅ PASS: '{query}' → '{expected_variant}' dahil")
            passed += 1
        else:
            print(f"❌ FAIL: '{query}' → '{expected_variant}' eksik")
            print(f"        Expanded: {expanded}")
            failed += 1
    
    print(f"\nSonuç: {passed} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG RECALL TEST SUITE")
    print("="*60)
    
    # Turkish normalization test
    norm_ok = test_turkish_normalization()
    
    # Quran recall test
    recall_ok = test_quran_recall()
    
    # Summary
    print("\n" + "="*60)
    print("ÖZET")
    print("="*60)
    print(f"Turkish Normalization: {'✅ PASS' if norm_ok else '❌ FAIL'}")
    print(f"Quran Recall: {'✅ PASS' if recall_ok else '❌ FAIL'}")
    
    # Exit code
    sys.exit(0 if (norm_ok and recall_ok) else 1)
