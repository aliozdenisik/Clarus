"""
Test Dual Vector Search

quran_tr_v2 collection üzerinde hibrit arama testi yapar.
"""
import sys
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Prefetch, SparseVector, Query

from src.embeddings import DenseEncoder, SparseEncoder
from src.turkish_utils import normalize_turkish

# Init
client = QdrantClient(url="http://localhost:6333")
dense_encoder = DenseEncoder()
sparse_encoder = SparseEncoder()

COLLECTION = "quran_tr_v2"


def dual_vector_search(query: str, limit: int = 10):
    """
    Search using all 4 vector types with RRF fusion.
    """
    # Normalize query
    query_norm = normalize_turkish(query.lower())
    
    # Encode query
    dense_orig = dense_encoder.encode(query)
    dense_norm = dense_encoder.encode(query_norm)
    sparse_orig_idx, sparse_orig_val = sparse_encoder.encode(query)
    sparse_norm_idx, sparse_norm_val = sparse_encoder.encode(query_norm)
    
    # 4 prefetches
    prefetches = [
        Prefetch(query=dense_orig, using="dense", limit=50),
        Prefetch(query=dense_norm, using="dense_normalized", limit=50),
        Prefetch(
            query=SparseVector(indices=sparse_orig_idx, values=sparse_orig_val),
            using="sparse",
            limit=50
        ),
        Prefetch(
            query=SparseVector(indices=sparse_norm_idx, values=sparse_norm_val),
            using="sparse_normalized",
            limit=50
        ),
    ]
    
    # RRF fusion
    from qdrant_client.models import FusionQuery, Fusion
    
    results = client.query_points(
        collection_name=COLLECTION,
        prefetch=prefetches,
        query=FusionQuery(fusion=Fusion.RRF),
        limit=limit,
        with_payload=True
    )
    
    return results.points


def test_search():
    """Run test queries"""
    
    test_queries = [
        "sabir ve namaz",
        "sabır ve namaz",
        "rahman rahim",
        "Allah yardım",
    ]
    
    print("="*70)
    print("DUAL VECTOR SEARCH TEST")
    print("="*70)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-"*50)
        
        results = dual_vector_search(query, limit=5)
        
        for i, r in enumerate(results, 1):
            p = r.payload
            score = r.score
            print(f"  {i}. [{p['surah_id']}:{p['verse_id']}] {p['surah_name']}")
            print(f"     Score: {score:.4f}")
            print(f"     {p['translation'][:60]}...")
        
        # Check for Bakara 2:45
        if "sabir" in query.lower() or "sabır" in query.lower():
            found_245 = any(
                r.payload['surah_id'] == 2 and r.payload['verse_id'] == 45 
                for r in results
            )
            status = "✅ FOUND" if found_245 else "❌ NOT FOUND"
            print(f"  --> Bakara 2:45: {status}")


if __name__ == "__main__":
    test_search()
