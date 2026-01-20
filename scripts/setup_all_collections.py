#!/usr/bin/env python3
"""
Unified Collection Setup Script

Creates all Qdrant collections from scratch in a single run:
- quran_tr (~6236 verses)
- bible_ot, bible_nt, bible_apocrypha (~31,102 verses total)

Usage:
    ./venv/bin/python scripts/setup_all_collections.py
    ./venv/bin/python scripts/setup_all_collections.py --skip-quran  # Bible only
    ./venv/bin/python scripts/setup_all_collections.py --skip-bible  # Quran only
"""
import sys
import asyncio
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    SparseVectorParams, SparseIndexParams,
    HnswConfigDiff, ScalarQuantization, ScalarQuantizationConfig,
    PayloadSchemaType, SparseVector
)

from src.data_loader import QuranDataLoader
from src.bible_loader import BibleDataLoader, get_testament
from src.embeddings import AsyncHybridEncoder, HybridEncoder

console = Console()
QDRANT_URL = "http://localhost:6333"

# Collections to manage
COLLECTIONS_TO_DELETE = [
    "quran_tr",
    "quran_semantic_chunks",
    "bible_kjva",  # Legacy
    "bible_kjva_semantic_chunks",
    "bible_ot",
    "bible_nt", 
    "bible_apocrypha",
]

TESTAMENT_COLLECTIONS = {
    "OT": "bible_ot",
    "NT": "bible_nt",
    "Apocrypha": "bible_apocrypha",
}


def delete_all_collections(client: QdrantClient) -> int:
    """Delete all managed collections."""
    existing = [c.name for c in client.get_collections().collections]
    deleted = 0
    
    for name in COLLECTIONS_TO_DELETE:
        if name in existing:
            console.print(f"  Deleting [red]{name}[/red]...")
            client.delete_collection(name)
            deleted += 1
    
    return deleted


def create_collection(client: QdrantClient, name: str, dense_dim: int, payload_indexes: list[tuple[str, PayloadSchemaType]]):
    """Create a collection with standard config."""
    client.create_collection(
        collection_name=name,
        vectors_config={
            "dense": VectorParams(
                size=dense_dim,
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
    for field, schema in payload_indexes:
        client.create_payload_index(
            collection_name=name,
            field_name=field,
            field_schema=schema
        )


async def index_quran(client: QdrantClient, encoder: AsyncHybridEncoder) -> int:
    """Index Quran verses."""
    console.print("\n[bold blue]📖 Indexing Quran[/bold blue]")
    
    # Load data
    loader = QuranDataLoader()
    loader.download_data()
    chunks = loader.create_chunks(show_progress=True)
    console.print(f"  Loaded [green]{len(chunks)}[/green] verses")
    
    # Create collection
    dense_dim = 3072  # text-embedding-3-large
    create_collection(client, "quran_tr", dense_dim, [
        ("surah_id", PayloadSchemaType.INTEGER),
        ("surah_type", PayloadSchemaType.KEYWORD),
        ("verse_id", PayloadSchemaType.INTEGER),
    ])
    console.print("  Created collection: [cyan]quran_tr[/cyan]")
    
    # Encode and index
    texts = [chunk.translation for chunk in chunks]
    console.print("  Encoding verses...")
    dense_vectors, sparse_vectors = await encoder.encode_batch_async(
        texts, batch_size=256, max_concurrent=10, show_progress=True
    )
    
    # Upload to Qdrant
    console.print("  Uploading to Qdrant...")
    batch_size = 500
    total = 0
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_dense = dense_vectors[i:i + batch_size]
        batch_sparse = sparse_vectors[i:i + batch_size]
        
        points = []
        for j, chunk in enumerate(batch_chunks):
            sparse_indices, sparse_values = batch_sparse[j]
            point = PointStruct(
                id=hash(chunk.id) % (2**63),
                vector={
                    "dense": batch_dense[j],
                    "sparse": SparseVector(indices=sparse_indices, values=sparse_values)
                },
                payload=chunk.to_dict()
            )
            points.append(point)
        
        client.upsert(collection_name="quran_tr", points=points)
        total += len(points)
    
    console.print(f"  [green]✓[/green] Indexed [bold]{total}[/bold] verses to quran_tr")
    return total


async def index_bible(client: QdrantClient, encoder: AsyncHybridEncoder) -> dict[str, int]:
    """Index Bible verses into testament-specific collections."""
    console.print("\n[bold yellow]📜 Indexing Bible[/bold yellow]")
    
    # Load data
    loader = BibleDataLoader("kjva")
    loader.download_data()
    chunks = loader.create_chunks(show_progress=True)
    console.print(f"  Loaded [green]{len(chunks)}[/green] verses")
    
    # Group by testament
    testament_chunks: dict[str, list] = {"OT": [], "NT": [], "Apocrypha": []}
    for chunk in chunks:
        testament_chunks[chunk.testament].append(chunk)
    
    for t, c in testament_chunks.items():
        console.print(f"    {t}: {len(c)} verses")
    
    # Create collections
    dense_dim = 3072
    for collection_name in TESTAMENT_COLLECTIONS.values():
        create_collection(client, collection_name, dense_dim, [
            ("book_name", PayloadSchemaType.KEYWORD),
            ("chapter_number", PayloadSchemaType.INTEGER),
            ("verse_number", PayloadSchemaType.INTEGER),
        ])
        console.print(f"  Created collection: [cyan]{collection_name}[/cyan]")
    
    # Index each testament
    counts = {}
    for testament, collection_name in TESTAMENT_COLLECTIONS.items():
        t_chunks = testament_chunks[testament]
        if not t_chunks:
            counts[collection_name] = 0
            continue
        
        console.print(f"\n  [bold]Encoding {testament}...[/bold]")
        texts = [chunk.text for chunk in t_chunks]
        dense_vectors, sparse_vectors = await encoder.encode_batch_async(
            texts, batch_size=256, max_concurrent=10, show_progress=True
        )
        
        # Upload
        batch_size = 500
        total = 0
        
        for i in range(0, len(t_chunks), batch_size):
            batch_chunks = t_chunks[i:i + batch_size]
            batch_dense = dense_vectors[i:i + batch_size]
            batch_sparse = sparse_vectors[i:i + batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(indices=sparse_indices, values=sparse_values)
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            client.upsert(collection_name=collection_name, points=points)
            total += len(points)
        
        counts[collection_name] = total
        console.print(f"  [green]✓[/green] Indexed [bold]{total}[/bold] verses to {collection_name}")
    
    return counts


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup all Qdrant collections")
    parser.add_argument("--skip-quran", action="store_true", help="Skip Quran indexing")
    parser.add_argument("--skip-bible", action="store_true", help="Skip Bible indexing")
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold green]Unified Collection Setup[/bold green]\n"
        "Creates all Qdrant collections from scratch",
        border_style="green"
    ))
    
    start_time = time.time()
    client = QdrantClient(url=QDRANT_URL)
    encoder = AsyncHybridEncoder()
    
    # Step 1: Clean existing collections
    console.print("\n[bold red]🗑️  Cleaning Existing Collections[/bold red]")
    deleted = delete_all_collections(client)
    console.print(f"  Deleted {deleted} collections")
    
    results = {}
    
    # Step 2: Index Quran
    if not args.skip_quran:
        quran_count = await index_quran(client, encoder)
        results["quran_tr"] = quran_count
    
    # Step 3: Index Bible
    if not args.skip_bible:
        bible_counts = await index_bible(client, encoder)
        results.update(bible_counts)
    
    # Summary
    elapsed = time.time() - start_time
    console.print("\n" + "=" * 50)
    console.print(Panel.fit(
        "[bold green]✨ Setup Complete![/bold green]\n\n" +
        "\n".join([f"  {name}: [bold]{count:,}[/bold] points" for name, count in results.items()]) +
        f"\n\n  Total time: [cyan]{elapsed:.1f}s[/cyan]",
        border_style="green"
    ))
    
    # Verify
    console.print("\n[dim]Verification:[/dim]")
    for c in client.get_collections().collections:
        info = client.get_collection(c.name)
        console.print(f"  {c.name}: {info.points_count} points ({info.status})")


if __name__ == "__main__":
    asyncio.run(main())
