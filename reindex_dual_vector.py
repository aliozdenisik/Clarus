"""
Dual Vector Reindexer - BATCH OPTIMIZED VERSION

Preprocessed verileri kullanarak yeni collection oluşturur.
Toplu API çağrıları ile hızlı indeksleme yapar.

Kullanım:
    python reindex_dual_vector.py
"""
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from tqdm import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    Distance,
    PointStruct,
    SparseVector,
)

from src.embeddings import DenseEncoder, SparseEncoder

# Collection name
COLLECTION_NAME = "quran_tr_v2"


def create_dual_vector_collection(client: QdrantClient, dense_dim: int, recreate: bool = True):
    """Create collection with dual vector configuration"""
    
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if exists:
        if recreate:
            print(f"Deleting existing collection: {COLLECTION_NAME}")
            client.delete_collection(COLLECTION_NAME)
        else:
            print(f"Collection exists: {COLLECTION_NAME}")
            return False
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(size=dense_dim, distance=Distance.COSINE),
            "dense_normalized": VectorParams(size=dense_dim, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False)),
            "sparse_normalized": SparseVectorParams(index=SparseIndexParams(on_disk=False)),
        }
    )
    
    print(f"Created dual vector collection: {COLLECTION_NAME}")
    return True


def load_preprocessed_data():
    """Load preprocessed verses"""
    path = Path("data/quran_preprocessed.json")
    if not path.exists():
        print("ERROR: Preprocessed data not found. Run preprocess_verses.py first.")
        sys.exit(1)
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def index_with_batch_embeddings(
    client: QdrantClient,
    dense_encoder: DenseEncoder,
    sparse_encoder: SparseEncoder,
    verses: list,
    batch_size: int = 32
):
    """
    Index verses using BATCH API calls for efficiency.
    Much faster than per-text API calls.
    """
    
    total = len(verses)
    print(f"Indexing {total} verses with batch size {batch_size}...")
    
    # Prepare all texts
    print("Preparing texts...")
    orig_texts = [v["translation"] for v in verses]
    norm_texts = [v["translation_normalized"] for v in verses]
    
    # BATCH encode dense vectors - MUCH FASTER!
    print("\nEncoding original texts (batch)...")
    dense_orig_all = dense_encoder.encode_batch(orig_texts, batch_size=batch_size)
    
    print("\nEncoding normalized texts (batch)...")
    dense_norm_all = dense_encoder.encode_batch(norm_texts, batch_size=batch_size)
    
    # Encode sparse vectors
    print("\nEncoding sparse vectors...")
    sparse_orig_all = []
    sparse_norm_all = []
    
    for i in tqdm(range(total), desc="Sparse encoding"):
        sparse_orig_all.append(sparse_encoder.encode(orig_texts[i]))
        sparse_norm_all.append(sparse_encoder.encode(norm_texts[i]))
    
    # Now create and upsert points in batches
    print("\nUpserting to Qdrant...")
    indexed = 0
    
    for i in tqdm(range(0, total, batch_size), desc="Upserting"):
        batch_end = min(i + batch_size, total)
        points = []
        
        for j in range(i, batch_end):
            verse = verses[j]
            point_id = verse["surah_id"] * 1000 + verse["verse_id"]
            
            sparse_orig_idx, sparse_orig_val = sparse_orig_all[j]
            sparse_norm_idx, sparse_norm_val = sparse_norm_all[j]
            
            point = PointStruct(
                id=point_id,
                vector={
                    "dense": dense_orig_all[j],
                    "dense_normalized": dense_norm_all[j],
                    "sparse": SparseVector(indices=sparse_orig_idx, values=sparse_orig_val),
                    "sparse_normalized": SparseVector(indices=sparse_norm_idx, values=sparse_norm_val),
                },
                payload={
                    "id": verse["id"],
                    "surah_id": verse["surah_id"],
                    "surah_name": verse["surah_name"],
                    "surah_name_arabic": verse["surah_name_arabic"],
                    "surah_transliteration": verse["surah_transliteration"],
                    "surah_type": verse["surah_type"],
                    "verse_id": verse["verse_id"],
                    "arabic_text": verse["arabic_text"],
                    "translation": verse["translation"],
                    "translation_normalized": verse["translation_normalized"],
                    "translation_lemma": verse["translation_lemma"],
                }
            )
            points.append(point)
        
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        indexed += len(points)
    
    return indexed


def main():
    print("="*60)
    print("DUAL VECTOR REINDEXER - BATCH OPTIMIZED")
    print("="*60)
    
    # Load preprocessed data
    print("\nLoading preprocessed data...")
    verses = load_preprocessed_data()
    print(f"Loaded {len(verses)} verses")
    
    # Initialize encoders
    print("\nInitializing encoders...")
    dense_encoder = DenseEncoder()
    sparse_encoder = SparseEncoder()
    
    # Connect to Qdrant
    print("\nConnecting to Qdrant...")
    client = QdrantClient(url="http://localhost:6333")
    
    # Create collection
    print("\nCreating dual vector collection...")
    create_dual_vector_collection(
        client=client,
        dense_dim=dense_encoder.dimension,
        recreate=True
    )
    
    # Index with batch API
    print("\nIndexing with BATCH API calls...")
    indexed = index_with_batch_embeddings(
        client=client,
        dense_encoder=dense_encoder,
        sparse_encoder=sparse_encoder,
        verses=verses,
        batch_size=32
    )
    
    # Verify
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print(f"Indexed: {indexed} verses")
    print(f"Collection: {COLLECTION_NAME}")
    
    info = client.get_collection(COLLECTION_NAME)
    print(f"Points count: {info.points_count}")
    print(f"Vectors: dense, dense_normalized, sparse, sparse_normalized")


if __name__ == "__main__":
    main()
