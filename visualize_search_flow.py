# -*- coding: utf-8 -*-
"""
Search Pipeline Visualizer
Her adimi ekrana yazdirarak arama akisini gorsellstirir.
"""
import time
import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def print_header(text):
    """Print a styled header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_step(step_num, title, emoji=""):
    """Print a step header"""
    print(f"\n[ADIM {step_num}] {emoji} {title}")
    print(f"{'-'*50}")

def print_info(label, value, indent=2):
    """Print key-value info"""
    spaces = " " * indent
    print(f"{spaces}{label}: {value}")

def print_vector(name, vector, max_show=8):
    """Print vector with truncation"""
    if isinstance(vector, (list, tuple)) and len(vector) > max_show:
        shown = [f"{v:.4f}" for v in vector[:max_show]]
        print(f"  {name}: [{', '.join(shown)}, ... ] (toplam {len(vector)} boyut)")
    else:
        print(f"  {name}: {vector}")

def visualize_search(query: str, mode: str = "hybrid", limit: int = 5):
    """
    Gercek arama yapip her adimi ekrana yazdirir.
    """
    
    print_header("[ARAMA PIPELINE GORSELLESTIRME]")
    print(f"Sorgu: '{query}'")
    print(f"Mod: {mode}")
    print(f"Limit: {limit}")
    
    total_start = time.time()
    
    # ============================================================
    # ADIM 1: Turkish Normalization
    # ============================================================
    print_step(1, "TURKISH NORMALIZASYON", "[TR]")
    
    from src.turkish_utils import normalize_turkish, expand_turkish_query, generate_i_variants
    
    step_start = time.time()
    
    # Normalize
    normalized = normalize_turkish(query)
    print_info("Orijinal sorgu", query)
    print_info("Normalize edilmis", normalized)
    
    # Expand with variants
    expanded = expand_turkish_query(query)
    print_info("Genisletilmis sorgu", expanded)
    
    # Show word-by-word variants
    print(f"\n  Kelime bazli varyantlar:")
    for word in query.split():
        variants = generate_i_variants(word.lower())
        print(f"    '{word}' -> {variants}")
    
    step_time = time.time() - step_start
    print(f"\n  Sure: {step_time*1000:.2f}ms")
    
    # ============================================================
    # ADIM 2: Dense Encoding (Semantic)
    # ============================================================
    print_step(2, "DENSE ENCODING (SEMANTIC)", "[AI]")
    
    from src.embeddings import DenseEncoder
    
    step_start = time.time()
    
    dense_encoder = DenseEncoder()
    print_info("Model", dense_encoder.model_name)
    print_info("API", "OpenRouter")
    
    print(f"\n  Encoding basliyor...")
    dense_vector = dense_encoder.encode(query)
    
    print_vector("Dense Vector", dense_vector)
    print_info("Boyut", f"{len(dense_vector)} dim")
    print_info("Min deger", f"{min(dense_vector):.4f}")
    print_info("Max deger", f"{max(dense_vector):.4f}")
    print_info("Ortalama", f"{sum(dense_vector)/len(dense_vector):.4f}")
    
    step_time = time.time() - step_start
    print(f"\n  Sure: {step_time*1000:.2f}ms")
    
    # ============================================================
    # ADIM 3: Sparse Encoding (BM25)
    # ============================================================
    print_step(3, "SPARSE ENCODING (BM25)", "[TXT]")
    
    from src.embeddings import SparseEncoder
    
    step_start = time.time()
    
    sparse_encoder = SparseEncoder()
    print_info("Model", sparse_encoder.model_name)
    
    # Use expanded query for better keyword matching
    print(f"\n  Expanded query icin encoding:")
    sparse_indices, sparse_values = sparse_encoder.query_embed(expanded)
    
    print_info("Indices (token IDs)", list(sparse_indices[:15]) if len(sparse_indices) > 15 else list(sparse_indices))
    print_info("Values (TF-IDF weights)", [f"{v:.3f}" for v in list(sparse_values)[:15]])
    print_info("Non-zero token sayisi", len(sparse_indices))
    
    if len(sparse_values) > 0:
        print_info("Max weight", f"{max(sparse_values):.4f}")
        print_info("Min weight", f"{min(sparse_values):.4f}")
    
    step_time = time.time() - step_start
    print(f"\n  Sure: {step_time*1000:.2f}ms")
    
    # ============================================================
    # ADIM 4: Qdrant Query (Parallel Prefetch)
    # ============================================================
    print_step(4, "QDRANT PARALLEL PREFETCH", "[DB]")
    
    from qdrant_client import QdrantClient
    from qdrant_client.models import Prefetch, SparseVector, RrfQuery, Rrf
    
    step_start = time.time()
    
    client = QdrantClient(url="http://localhost:6333")
    collection_name = "quran_tr"
    
    print_info("Collection", collection_name)
    print_info("Qdrant URL", "http://localhost:6333")
    
    # Show prefetch config
    print(f"\n  Prefetch Konfigurasyonu:")
    print(f"    +-- Sparse Prefetch (BM25): limit=100, using='sparse'")
    print(f"    +-- Dense Prefetch (Semantic): limit=100, using='dense'")
    
    print(f"\n  RRF Fusion:")
    print(f"    +-- k=60 (normalization constant)")
    
    # Execute the query
    print(f"\n  >> Qdrant sorgusu calistiriliyor...")
    
    results = client.query_points(
        collection_name=collection_name,
        prefetch=[
            Prefetch(
                query=SparseVector(indices=list(sparse_indices), values=list(sparse_values)),
                using="sparse",
                limit=100
            ),
            Prefetch(
                query=dense_vector,
                using="dense",
                limit=100
            )
        ],
        query=RrfQuery(rrf=Rrf(k=60)),
        limit=limit,
        with_payload=True
    )
    
    step_time = time.time() - step_start
    print(f"\n  Sure: {step_time*1000:.2f}ms")
    
    # ============================================================
    # ADIM 5: RRF Fusion Sonuclari
    # ============================================================
    print_step(5, "RRF FUSION SONUCLARI", "[MERGE]")
    
    print(f"  RRF Formula: score = Sum 1/(k + rank)")
    print(f"  k degeri: 60")
    print(f"  Birlestirilen kaynaklar: Dense + Sparse")
    
    print(f"\n  Toplam sonuc: {len(results.points)}")
    
    # ============================================================
    # ADIM 6: Sonuclarin Parse Edilmesi
    # ============================================================
    print_step(6, "SONUCLAR", "[OUT]")
    
    for i, point in enumerate(results.points, 1):
        payload = point.payload
        print(f"\n  --- Sonuc #{i} ---")
        print(f"  ID: {payload.get('id', 'N/A')}")
        print(f"  Score (RRF): {point.score:.4f}")
        print(f"  Sure: {payload.get('surah_name', '')} ({payload.get('surah_id', '')}:{payload.get('verse_id', '')})")
        
        translation = payload.get('translation', '')
        if len(translation) > 120:
            translation = translation[:120] + "..."
        print(f"  Ceviri: {translation}")
    
    # ============================================================
    # OZET
    # ============================================================
    total_time = time.time() - total_start
    
    print_header("[OZET]")
    print(f"  * Toplam sure: {total_time*1000:.2f}ms")
    print(f"  * Bulunan sonuc: {len(results.points)}")
    print(f"  * Dense boyut: {len(dense_vector)}")
    print(f"  * Sparse token: {len(sparse_indices)}")
    print(f"  * Turkish varyant: {len(expanded.split())} kelime")


def main():
    """Ana calistirma fonksiyonu"""
    # Write to file
    import io
    output_file = "search_output.txt"
    
    # Store original stdout
    original_stdout = sys.stdout
    
    # Create file with utf-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        sys.stdout = f
        
        print(f"\n=== QDRANT HYBRID SEARCH VISUALIZER ===\n")
        
        # Test sorgulari
        test_queries = [
            "sabir ve namaz",
        ]
        
        for query in test_queries:
            try:
                visualize_search(query, mode="hybrid", limit=5)
            except Exception as e:
                print(f"Hata: {e}")
                import traceback
                traceback.print_exc()
            
            print("\n" + "="*70 + "\n")
    
    # Restore stdout
    sys.stdout = original_stdout
    print(f"Output written to {output_file}")
    
    # Also print to console
    with open(output_file, 'r', encoding='utf-8') as f:
        print(f.read())


if __name__ == "__main__":
    main()
