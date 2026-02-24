#!/usr/bin/env python3
# ruff: noqa: E402
# This setup script adjusts sys.path before importing project modules.
"""
Unified Collection Setup Script (Multi-Translator)

Creates all Qdrant collections from scratch in a single run:
- quran_tr_{translator} × 8 translators (~6,236 verses each = 49,888 total)
- quran_en_{translator} × 1 English translator (~6,236 verses each)
- bible_tr_ot, bible_tr_nt (Turkish Bible, ~30,182 verses total)
- bible_ot, bible_nt, bible_apocrypha (English KJVA, ~36,819 verses total)

Usage:
    ./venv/bin/python scripts/setup_all_collections.py
    ./venv/bin/python scripts/setup_all_collections.py --skip-quran
    ./venv/bin/python scripts/setup_all_collections.py --translator diyanet  # Single translator
    ./venv/bin/python scripts/setup_all_collections.py --skip-english-bible
    ./venv/bin/python scripts/setup_all_collections.py --skip-english-quran
    ./venv/bin/python scripts/setup_all_collections.py --no-flush  # Skip Redis cache flush
    ./venv/bin/python scripts/setup_all_collections.py --yes  # Skip confirmation prompts
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    PayloadSchemaType,
    PointStruct,
    ScalarQuantization,
    ScalarQuantizationConfig,
    ScalarType,
    SparseIndexParams,
    SparseVectorParams,
    VectorParams,
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.bible_loader import BibleDataLoader
from src.embeddings import AsyncDenseEncoder
from src.indexer import TurkishBibleIndexer
from src.tanzil_loader import VALID_EN_TRANSLATORS, VALID_TRANSLATORS, TanzilLoader

console = Console()
QDRANT_URL = "http://localhost:6333"

# Collections to delete
OLD_COLLECTIONS = [
    "quran_tr",  # Old single-translator collection
    "quran_semantic_chunks",
    "bible_kjva",  # Legacy
    "bible_kjva_semantic_chunks",
]

TESTAMENT_COLLECTIONS = {
    "OT": "bible_ot",
    "NT": "bible_nt",
    "Apocrypha": "bible_apocrypha",
}


def delete_old_collections(client: QdrantClient, skip_confirmation: bool = False) -> int:
    """Delete old single-translator collections with confirmation."""
    existing = [c.name for c in client.get_collections().collections]
    to_delete = [name for name in OLD_COLLECTIONS if name in existing]

    if not to_delete:
        return 0

    console.print("\n[yellow]Found old collections to delete:[/yellow]")
    for name in to_delete:
        console.print(f"  - {name}")

    if not skip_confirmation:
        response = input("\nDelete these collections? [yes/N]: ")
        if response.lower() != "yes":
            console.print("[yellow]Skipping deletion.[/yellow]")
            return 0

    deleted = 0
    for name in to_delete:
        console.print(f"  Deleting [red]{name}[/red]...")
        client.delete_collection(name)
        deleted += 1

    return deleted


def create_collection(
    client: QdrantClient,
    name: str,
    dense_dim: int,
    payload_indexes: list[tuple[str, PayloadSchemaType]],
):
    """Create a collection with standard config."""
    client.create_collection(
        collection_name=name,
        vectors_config={
            "dense": VectorParams(
                size=dense_dim,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
                quantization_config=ScalarQuantization(
                    scalar=ScalarQuantizationConfig(type=ScalarType.INT8, quantile=0.99, always_ram=True)
                ),
            )
        },
        sparse_vectors_config={"sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))},
    )

    # Create payload indexes
    for field, schema in payload_indexes:
        client.create_payload_index(collection_name=name, field_name=field, field_schema=schema)


async def index_quran_translators(
    client: QdrantClient, encoder: AsyncDenseEncoder, translators: list[str]
) -> dict[str, int]:
    """Index all specified Quran translators."""
    console.print(f"\n[bold blue]📖 Indexing Quran ({len(translators)} translators)[/bold blue]")

    loader = TanzilLoader()
    counts = {}

    for translator in sorted(translators):
        console.print(f"\n  [cyan]Translator: {translator}[/cyan]")

        # Load translation
        verses = loader.load_translation(translator)
        metadata = loader._load_surah_metadata()
        console.print(f"    Loaded [green]{len(verses)}[/green] verses")

        # Convert to chunks
        from src.data_loader import QuranChunk
        from src.surah_names import get_turkish_surah_name

        chunks = []
        for verse in verses:
            surah_num = verse["surah_number"]
            surah_meta = metadata.get(surah_num, {})

            # Use Turkish name from mapping instead of Tanzil transliteration
            turkish_name = get_turkish_surah_name(surah_num)
            surah_name = turkish_name or verse["surah_name"]

            chunk = QuranChunk(
                id=f"{surah_num}:{verse['verse_number']}",
                surah_id=surah_num,
                surah_name=surah_name,
                surah_name_arabic=surah_meta.get("name", ""),
                surah_transliteration=verse["surah_name"],
                surah_type=surah_meta.get("type", ""),
                verse_id=verse["verse_number"],
                arabic_text="",
                translation=verse["text"],
                translation_normalized="",
                translation_lemma="",
            )
            chunks.append(chunk)

        # Create collection
        collection_name = f"quran_tr_{translator}"
        dense_dim = 3072
        create_collection(
            client,
            collection_name,
            dense_dim,
            [
                ("surah_number", PayloadSchemaType.INTEGER),
                ("verse_number", PayloadSchemaType.INTEGER),
                ("translator", PayloadSchemaType.KEYWORD),
            ],
        )
        console.print(f"    Created collection: [cyan]{collection_name}[/cyan]")

        # Encode and index
        texts = [chunk.translation for chunk in chunks]
        console.print("    Encoding verses...")
        dense_vectors = await encoder.encode_batch_async(texts, batch_size=256, max_concurrent=10, show_progress=True)

        # Upload to Qdrant
        console.print("    Uploading to Qdrant...")
        batch_size = 500
        total = 0

        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            client.upsert(collection_name=collection_name, points=points)
            total += len(points)

        counts[collection_name] = total
        console.print(f"    [green]✓[/green] Indexed [bold]{total}[/bold] verses")

    return counts


async def index_english_quran_translators(
    client: QdrantClient, encoder: AsyncDenseEncoder, translators: list[str]
) -> dict[str, int]:
    """Index all specified English Quran translators."""
    console.print(f"\n[bold green]📖 Indexing English Quran ({len(translators)} translators)[/bold green]")

    loader = TanzilLoader()
    counts = {}

    for translator in sorted(translators):
        console.print(f"\n  [cyan]Translator: en_{translator}[/cyan]")

        verses = loader.load_english_translation(translator)
        metadata = loader._load_surah_metadata()
        console.print(f"    Loaded [green]{len(verses)}[/green] verses")

        from src.data_loader import QuranChunk

        chunks = []
        for verse in verses:
            surah_num = verse["surah_number"]
            surah_meta = metadata.get(surah_num, {})

            chunk = QuranChunk(
                id=f"{surah_num}:{verse['verse_number']}",
                surah_id=surah_num,
                surah_name=verse["surah_name"],
                surah_name_arabic=surah_meta.get("name", ""),
                surah_transliteration=verse["surah_name"],
                surah_type=surah_meta.get("type", ""),
                verse_id=verse["verse_number"],
                arabic_text="",
                translation=verse["text"],
                translation_normalized="",
                translation_lemma="",
            )
            chunks.append(chunk)

        collection_name = f"quran_en_{translator}"
        dense_dim = 3072
        create_collection(
            client,
            collection_name,
            dense_dim,
            [
                ("surah_number", PayloadSchemaType.INTEGER),
                ("verse_number", PayloadSchemaType.INTEGER),
                ("translator", PayloadSchemaType.KEYWORD),
            ],
        )
        console.print(f"    Created collection: [cyan]{collection_name}[/cyan]")

        texts = [chunk.translation for chunk in chunks]
        console.print("    Encoding verses...")
        dense_vectors = await encoder.encode_batch_async(texts, batch_size=256, max_concurrent=10, show_progress=True)

        console.print("    Uploading to Qdrant...")
        batch_size = 500
        total = 0

        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            client.upsert(collection_name=collection_name, points=points)
            total += len(points)

        counts[collection_name] = total
        console.print(f"    [green]✓[/green] Indexed [bold]{total}[/bold] verses")

    return counts


async def index_turkish_bible(client: QdrantClient) -> dict[str, int]:
    """Index Turkish Bible using TurkishBibleIndexer."""
    console.print("\n[bold cyan]📜 Indexing Turkish Bible[/bold cyan]")

    indexer = TurkishBibleIndexer(qdrant_url=QDRANT_URL)
    result = indexer.index_all(recreate=True)

    counts = {
        "bible_tr_ot": result["ot"],
        "bible_tr_nt": result["nt"],
    }

    console.print("  [green]✓[/green] Indexed Turkish Bible:")
    console.print(f"    OT: {result['ot']} verses")
    console.print(f"    NT: {result['nt']} verses")

    return counts


async def index_english_bible(client: QdrantClient, encoder: AsyncDenseEncoder) -> dict[str, int]:
    """Index English Bible verses into testament-specific collections."""
    console.print("\n[bold yellow]📜 Indexing English Bible (KJVA)[/bold yellow]")

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
        create_collection(
            client,
            collection_name,
            dense_dim,
            [
                ("book_name", PayloadSchemaType.KEYWORD),
                ("chapter_number", PayloadSchemaType.INTEGER),
                ("verse_number", PayloadSchemaType.INTEGER),
            ],
        )
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
        dense_vectors = await encoder.encode_batch_async(texts, batch_size=256, max_concurrent=10, show_progress=True)

        # Upload
        batch_size = 500
        total = 0

        for i in range(0, len(t_chunks), batch_size):
            batch_chunks = t_chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
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
    parser.add_argument("--skip-english-quran", action="store_true", help="Skip English Quran indexing")
    parser.add_argument("--skip-bible", action="store_true", help="Skip all Bible indexing")
    parser.add_argument(
        "--skip-english-bible",
        action="store_true",
        help="Skip English Bible (keep Turkish)",
    )
    parser.add_argument("--skip-turkish-bible", action="store_true", help="Skip Turkish Bible")
    parser.add_argument(
        "--translator",
        type=str,
        default=None,
        choices=list(VALID_TRANSLATORS),
        help="Index only one specific Quran translator",
    )
    parser.add_argument("--no-flush", action="store_true", help="Skip Redis cache flush")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold green]Unified Collection Setup (Multi-Translator)[/bold green]\n"
            "Creates all Qdrant collections from scratch",
            border_style="green",
        )
    )

    start_time = time.time()
    client = QdrantClient(url=QDRANT_URL)
    encoder = AsyncDenseEncoder()
    await encoder.init_cache()  # Initialize async Redis cache

    # Step 1: Clean existing old collections
    console.print("\n[bold red]🗑️  Cleaning Old Collections[/bold red]")
    deleted = delete_old_collections(client, skip_confirmation=args.yes)
    if deleted > 0:
        console.print(f"  Deleted {deleted} old collections")
    else:
        console.print("  No old collections to delete")

    results = {}

    # Step 2: Index Quran (all translators or specific one)
    if not args.skip_quran:
        if args.translator:
            translators = [args.translator]
        else:
            translators = sorted(VALID_TRANSLATORS)

        quran_counts = await index_quran_translators(client, encoder, translators)
        results.update(quran_counts)

    # Step 2b: Index English Quran
    if not args.skip_quran and not args.skip_english_quran:
        en_quran_counts = await index_english_quran_translators(client, encoder, sorted(VALID_EN_TRANSLATORS))
        results.update(en_quran_counts)

    # Step 3: Index Turkish Bible
    if not args.skip_bible and not args.skip_turkish_bible:
        turkish_bible_counts = await index_turkish_bible(client)
        results.update(turkish_bible_counts)

    # Step 4: Index English Bible
    if not args.skip_bible and not args.skip_english_bible:
        english_bible_counts = await index_english_bible(client, encoder)
        results.update(english_bible_counts)

    # Step 5: Flush Redis cache
    if not args.no_flush:
        try:
            import redis

            console.print("\n[bold magenta]🔄 Flushing Redis Cache[/bold magenta]")
            r = redis.Redis(host="localhost", port=6379)
            r.flushall()
            console.print("  [green]✓[/green] Redis cache flushed")
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Redis flush failed (non-critical): {e}")

    # Summary
    elapsed = time.time() - start_time

    # Create summary table
    table = Table(title="Collection Summary", show_lines=True)
    table.add_column("Collection", style="cyan", width=25)
    table.add_column("Verses", style="green", justify="right", width=10)
    table.add_column("Type", style="magenta", width=15)

    # Sort results by type
    quran_tr_collections = {k: v for k, v in results.items() if k.startswith("quran_tr_")}
    quran_en_collections = {k: v for k, v in results.items() if k.startswith("quran_en_")}
    turkish_bible_collections = {k: v for k, v in results.items() if k.startswith("bible_tr_")}
    english_bible_collections = {k: v for k, v in results.items() if k in TESTAMENT_COLLECTIONS.values()}

    # Add Turkish Quran collections
    for name, count in sorted(quran_tr_collections.items()):
        translator = name[len("quran_tr_") :]
        table.add_row(name, f"{count:,}", f"Quran TR ({translator})")

    # Add English Quran collections
    for name, count in sorted(quran_en_collections.items()):
        translator = name[len("quran_en_") :]
        table.add_row(name, f"{count:,}", f"Quran EN ({translator})")

    # Add Turkish Bible collections
    for name, count in sorted(turkish_bible_collections.items()):
        testament = name.replace("bible_tr_", "").upper()
        table.add_row(name, f"{count:,}", f"Bible TR ({testament})")

    # Add English Bible collections
    for name, count in sorted(english_bible_collections.items()):
        testament = name.replace("bible_", "").upper()
        table.add_row(name, f"{count:,}", f"Bible EN ({testament})")

    # Add totals
    total_verses = sum(results.values())
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_verses:,}[/bold]",
        "[bold]All Collections[/bold]",
    )

    console.print("\n" + "=" * 70)
    console.print(
        Panel.fit(
            f"[bold green]✨ Setup Complete![/bold green]\n\n"
            f"  Collections created: [bold]{len(results)}[/bold]\n"
            f"  Total verses indexed: [bold]{total_verses:,}[/bold]\n"
            f"  Total time: [cyan]{elapsed:.1f}s[/cyan]",
            border_style="green",
        )
    )

    console.print(table)

    # Verify
    console.print("\n[dim]Verification:[/dim]")
    for c in client.get_collections().collections:
        if c.name in results:
            info = client.get_collection(c.name)
            console.print(f"  {c.name}: {info.points_count} points ({info.status})")


if __name__ == "__main__":
    asyncio.run(main())
