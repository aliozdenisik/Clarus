#!/usr/bin/env python3
"""
Split Bible Collection by Testament

Migrates data from `bible_kjva` into 3 separate collections:
- bible_ot (Old Testament)
- bible_nt (New Testament)  
- bible_apocrypha (Apocrypha/Deuterocanonical)

No re-embedding needed - copies existing vectors.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    SparseVectorParams, SparseIndexParams,
    HnswConfigDiff, ScalarQuantization, ScalarQuantizationConfig,
    PayloadSchemaType, SparseVector
)
from tqdm import tqdm


QDRANT_URL = "http://localhost:6333"
SOURCE_COLLECTION = "bible_kjva"
TESTAMENT_COLLECTIONS = {
    "OT": "bible_ot",
    "NT": "bible_nt",
    "Apocrypha": "bible_apocrypha"
}


def get_collection_config(client: QdrantClient, collection_name: str):
    """Get vector configuration from existing collection."""
    info = client.get_collection(collection_name)
    return info.config


def create_testament_collection(client: QdrantClient, name: str, source_config):
    """Create a testament collection with same vector config as source."""
    # Check if exists
    collections = [c.name for c in client.get_collections().collections]
    if name in collections:
        print(f"  Deleting existing collection: {name}")
        client.delete_collection(name)
    
    # Get dense vector params from source
    dense_config = source_config.params.vectors.get("dense")
    
    print(f"  Creating collection: {name} (dim={dense_config.size})")
    
    client.create_collection(
        collection_name=name,
        vectors_config={
            "dense": VectorParams(
                size=dense_config.size,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
                quantization_config=ScalarQuantization(
                    scalar=ScalarQuantizationConfig(
                        type="int8",
                        quantile=0.99,
                        always_ram=True
                    )
                )
            )
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        }
    )
    
    # Create payload indexes
    for field, schema in [
        ("book_name", PayloadSchemaType.KEYWORD),
        ("chapter_number", PayloadSchemaType.INTEGER),
        ("verse_number", PayloadSchemaType.INTEGER),
    ]:
        client.create_payload_index(
            collection_name=name,
            field_name=field,
            field_schema=schema
        )
    
    return True


def migrate_points(client: QdrantClient, source: str, targets: dict):
    """Migrate points from source to testament-specific collections."""
    print(f"\nMigrating points from {source}...")
    
    # Scroll through all points
    offset = None
    batch_size = 100
    counts = {t: 0 for t in targets.values()}
    
    while True:
        results, offset = client.scroll(
            collection_name=source,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=True
        )
        
        if not results:
            break
        
        # Group by testament
        testament_points = {t: [] for t in targets.keys()}
        
        for point in results:
            testament = point.payload.get("testament", "OT")
            if testament not in testament_points:
                testament = "OT"  # Default
            
            # Get vectors
            dense_vector = point.vector.get("dense", [])
            sparse_data = point.vector.get("sparse")
            
            # Handle sparse vector - it's a SparseVector object, not a dict
            if sparse_data is not None:
                sparse_indices = sparse_data.indices if hasattr(sparse_data, 'indices') else sparse_data.get("indices", [])
                sparse_values = sparse_data.values if hasattr(sparse_data, 'values') else sparse_data.get("values", [])
            else:
                sparse_indices = []
                sparse_values = []
            
            new_point = PointStruct(
                id=point.id,
                vector={
                    "dense": dense_vector,
                    "sparse": SparseVector(
                        indices=sparse_indices,
                        values=sparse_values
                    )
                },
                payload=point.payload
            )
            testament_points[testament].append(new_point)
        
        # Upsert to each testament collection
        for testament, points in testament_points.items():
            if points:
                target_collection = targets[testament]
                client.upsert(
                    collection_name=target_collection,
                    points=points
                )
                counts[targets[testament]] += len(points)
        
        if offset is None:
            break
    
    return counts


def main():
    print("=" * 60)
    print("Bible Testament Collection Split")
    print("=" * 60)
    
    client = QdrantClient(url=QDRANT_URL)
    
    # Step 1: Get source config
    print("\n[1/4] Reading source collection config...")
    source_config = get_collection_config(client, SOURCE_COLLECTION)
    print(f"  Source: {SOURCE_COLLECTION}")
    
    # Step 2: Create testament collections
    print("\n[2/4] Creating testament collections...")
    for testament, collection_name in TESTAMENT_COLLECTIONS.items():
        create_testament_collection(client, collection_name, source_config)
    
    # Step 3: Migrate points
    print("\n[3/4] Migrating points...")
    counts = migrate_points(client, SOURCE_COLLECTION, TESTAMENT_COLLECTIONS)
    
    print("\nMigration complete:")
    for collection, count in counts.items():
        print(f"  {collection}: {count} verses")
    
    # Step 4: Delete source collection
    print(f"\n[4/4] Deleting source collection: {SOURCE_COLLECTION}...")
    client.delete_collection(SOURCE_COLLECTION)
    print("  Deleted.")
    
    # Verify
    print("\n" + "=" * 60)
    print("Verification:")
    print("=" * 60)
    
    collections = client.get_collections().collections
    for c in collections:
        if c.name.startswith("bible_"):
            info = client.get_collection(c.name)
            print(f"  {c.name}: {info.points_count} points")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
