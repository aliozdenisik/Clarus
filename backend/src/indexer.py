"""
Qdrant Indexer Module

Handles collection creation and document indexing with hybrid vectors.

Optimizations:
- HNSW config (m=16, ef_construct=200) for better search quality
- Scalar Quantization (int8) for 75% RAM savings
- Payload indexes for fast filtered searches
"""

from typing import List, Optional, Dict
from pathlib import Path
from tqdm import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    Distance,
    PointStruct,
    HnswConfigDiff,
    ScalarQuantization,
    ScalarQuantizationConfig,
    PayloadSchemaType,
)

from .data_loader import QuranChunk
from .embeddings import DenseEncoder
from .tanzil_loader import TanzilLoader, VALID_TRANSLATORS


class QuranIndexer:
    """
    Indexes Quran verses into Qdrant with hybrid vectors per translator.

    Supports 8 Turkish translators: diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel.
    Creates separate collections per translator: quran_tr_{translator}

    Optimized with:
    - HNSW: m=16, ef_construct=200 for quality-speed balance
    - Scalar Quantization: int8 for 75% RAM reduction
    - Payload indexes: surah_number, verse_number, translator for filtered search
    """

    def __init__(
        self,
        translator: str = "diyanet",
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[DenseEncoder] = None,
    ):
        """
        Initialize QuranIndexer for a specific translator.

        Args:
            translator: Translator key (default: "diyanet")
                       Valid: diyanet, yazir, ates, bulac, ozturk, vakfi, yildirim, yuksel
            qdrant_url: Qdrant server URL
            in_memory: Use in-memory Qdrant
            encoder: Dense encoder instance

        Raises:
            ValueError: If translator is invalid
        """
        if translator not in VALID_TRANSLATORS:
            raise ValueError(
                f"Invalid translator: {translator}\n"
                f"Valid translators: {', '.join(sorted(VALID_TRANSLATORS))}"
            )

        self.translator = translator
        self.collection_name = f"quran_tr_{translator}"

        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or DenseEncoder()
        self._collection_exists = False

    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create collection with dense and sparse vector configuration.

        Includes HNSW optimization and Scalar Quantization for performance.

        Args:
            recreate: If True, delete existing collection and create new
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if exists:
            if recreate:
                print(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
            else:
                print(f"Collection already exists: {self.collection_name}")
                self._collection_exists = True
                return False

        # Get dense vector dimension
        dense_dim = self.encoder.dense_dimension
        print(
            f"Creating collection {self.collection_name} ({self.translator}) with dense dimension: {dense_dim}"
        )
        print("  HNSW config: m=16, ef_construct=200")
        print("  Quantization: Scalar int8 (75% RAM savings)")

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=200,
                    ),
                    quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type="int8", quantile=0.99, always_ram=True
                        )
                    ),
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
            },
        )

        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="surah_number",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="verse_number",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="translator",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        print(f"Created collection: {self.collection_name}")
        self._collection_exists = True
        return True

    def index_chunks(
        self,
        chunks: List[QuranChunk],
        batch_size: int = 100,
        show_progress: bool = True,
    ) -> int:
        """
        Index chunks with dense vectors only.

        Args:
            chunks: List of QuranChunk objects
            batch_size: Number of chunks to process at once
            show_progress: Show progress bar

        Returns:
            Number of indexed chunks
        """
        if not self._collection_exists:
            self.create_collection()

        # Extract texts for encoding
        texts = [chunk.translation for chunk in chunks]

        # Encode all texts (returns only dense vectors)
        print(f"Encoding {len(texts)} chunks...")
        dense_vectors = self.encoder.encode_batch(
            texts, batch_size=batch_size, show_progress=show_progress
        )

        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0

        for i in tqdm(range(0, len(chunks), batch_size), desc="Indexing"):
            batch_chunks = chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),  # Convert string ID to int
                    vector={
                        "dense": batch_dense[j],
                    },
                    payload=chunk.to_dict(),
                )
                points.append(point)

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_indexed += len(points)

        print(f"Indexed {total_indexed} chunks successfully!")
        return total_indexed

    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": getattr(info, "vectors_count", info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }

    async def index_chunks_async(
        self,
        chunks: List[QuranChunk],
        batch_size: int = 256,  # Optimized for OpenRouter API
        max_concurrent_embeddings: int = 10,  # OpenRouter has no rate limits with credits
        upsert_batch_size: int = 500,  # Qdrant upsert batch size (larger = faster)
        show_progress: bool = True,
    ) -> int:
        """
        Async index chunks with parallel embedding generation.

        Optimized for maximum speed:
        - batch_size=256: Larger batches reduce API overhead (8x increase)
        - max_concurrent=10: Parallel API calls (2x increase)
        - upsert_batch_size=500: Bulk Qdrant inserts

        Args:
            chunks: List of QuranChunk objects
            batch_size: Embedding batch size (default: 256)
            max_concurrent_embeddings: Max concurrent API calls (default: 10)
            upsert_batch_size: Points per Qdrant upsert (default: 500)
            show_progress: Show progress bar

        Returns:
            Number of indexed chunks
        """
        from .embeddings import AsyncDenseEncoder

        if not self._collection_exists:
            self.create_collection()

        # Use async encoder
        async_encoder = AsyncDenseEncoder()

        # Extract texts for encoding
        texts = [chunk.translation for chunk in chunks]

        # Encode all texts asynchronously (returns only dense vectors)
        print(f"Async encoding {len(texts)} chunks...")
        dense_vectors = await async_encoder.encode_batch_async(
            texts,
            batch_size=batch_size,
            max_concurrent=max_concurrent_embeddings,
            show_progress=show_progress,
        )

        # Create points in batches (use larger upsert batches for speed)
        print(f"Indexing to Qdrant (batch_size={upsert_batch_size})...")
        total_indexed = 0

        for i in tqdm(range(0, len(chunks), upsert_batch_size), desc="Indexing"):
            batch_chunks = chunks[i : i + upsert_batch_size]
            batch_dense = dense_vectors[i : i + upsert_batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_indexed += len(points)

        print(f"Async indexed {total_indexed} chunks successfully!")
        return total_indexed

    def index(self) -> int:
        """
        Index Quran translation using TanzilLoader.

        Returns:
            Number of indexed verses
        """

        loader = TanzilLoader()
        verses = loader.load_translation(self.translator)
        metadata = loader._load_surah_metadata()

        # Convert verses to QuranChunk-like structure
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
                arabic_text="",  # Not available in Tanzil Turkish translations
                translation=verse["text"],
                translation_normalized="",
                translation_lemma="",
            )
            chunks.append(chunk)

        # Create collection if needed
        if not self._collection_exists:
            self.create_collection()

        # Index chunks
        return self.index_chunks(chunks)

    @staticmethod
    def index_all_translators(
        qdrant_url: str = "http://localhost:6333",
        recreate: bool = False,
    ) -> None:
        """
        Index all 8 Turkish Quran translations.

        Args:
            qdrant_url: Qdrant server URL
            recreate: If True, recreate collections
        """
        for translator in sorted(VALID_TRANSLATORS):
            print(f"\n{'=' * 60}")
            print(f"Indexing {translator} translation...")
            print(f"{'=' * 60}")

            indexer = QuranIndexer(translator=translator, qdrant_url=qdrant_url)
            indexer.create_collection(recreate=recreate)
            count = indexer.index()

            print(f"✓ Indexed {count} verses for {translator}")


class SemanticChunkIndexer:
    """
    Indexes semantic chunks (grouped verses) into Qdrant.

    Creates a parallel collection that stores semantically grouped verses
    for context-aware search alongside the single-verse collection.

    Optimized with:
    - HNSW: m=16, ef_construct=200 for quality-speed balance
    - Scalar Quantization: int8 for 75% RAM reduction
    - Payload indexes: surah_id, verse_count for filtered search
    """

    COLLECTION_NAME = "quran_semantic_chunks"

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[DenseEncoder] = None,
    ):
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or DenseEncoder()
        self._collection_exists = False

    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create collection for semantic chunks.

        Args:
            recreate: If True, delete existing collection and create new
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)

        if exists:
            if recreate:
                print(f"Deleting existing collection: {self.COLLECTION_NAME}")
                self.client.delete_collection(self.COLLECTION_NAME)
            else:
                print(f"Collection already exists: {self.COLLECTION_NAME}")
                self._collection_exists = True
                return False

        # Get dense vector dimension
        dense_dim = self.encoder.dense_dimension
        print(f"Creating semantic chunks collection with dense dimension: {dense_dim}")
        print("  HNSW config: m=16, ef_construct=200")
        print("  Quantization: Scalar int8 (75% RAM savings)")

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=200,
                    ),
                    quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type="int8", quantile=0.99, always_ram=True
                        )
                    ),
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
            },
        )

        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_id",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_type",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="verse_count",
            field_schema=PayloadSchemaType.INTEGER,
        )

        print(f"Created collection: {self.COLLECTION_NAME}")
        self._collection_exists = True
        return True

    def index_chunks(
        self,
        chunks,  # List[SemanticChunk]
        batch_size: int = 50,
        show_progress: bool = True,
    ) -> int:
        """
        Index semantic chunks with dense vectors only.

        Args:
            chunks: List of SemanticChunk objects
            batch_size: Number of chunks to process at once
            show_progress: Show progress bar

        Returns:
            Number of indexed chunks
        """
        if not self._collection_exists:
            self.create_collection()

        # Extract texts for encoding (combined translations)
        texts = [chunk.combined_translation for chunk in chunks]

        # Encode all texts (returns only dense vectors)
        print(f"Encoding {len(texts)} semantic chunks...")
        dense_vectors = self.encoder.encode_batch(
            texts, batch_size=batch_size, show_progress=show_progress
        )

        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0

        for i in tqdm(
            range(0, len(chunks), batch_size), desc="Indexing semantic chunks"
        ):
            batch_chunks = chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),  # Convert string ID to int
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)
            total_indexed += len(points)

        print(f"Indexed {total_indexed} semantic chunks successfully!")
        return total_indexed

    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "name": self.COLLECTION_NAME,
            "vectors_count": getattr(info, "vectors_count", info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }


class BibleSemanticChunkIndexer:
    """
    Indexes semantic chunks (grouped verses) of Bible into Qdrant.

    Creates a parallel collection that stores semantically grouped verses
    for context-aware search alongside the single-verse collection.
    """

    def __init__(
        self,
        translation: str = "kjva",
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[DenseEncoder] = None,
    ):
        self.translation = translation
        self.collection_name = f"bible_{translation}_semantic_chunks"

        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or DenseEncoder()
        self._collection_exists = False

    def create_collection(self, recreate: bool = False) -> bool:
        """Create collection for semantic chunks."""
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if exists:
            if recreate:
                print(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
            else:
                print(f"Collection already exists: {self.collection_name}")
                self._collection_exists = True
                return False

        # Get dense vector dimension
        dense_dim = self.encoder.dense_dimension
        print(f"Creating semantic chunks collection ({self.translation}): {dense_dim}")

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(m=16, ef_construct=200),
                    quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type="int8", quantile=0.99, always_ram=True
                        )
                    ),
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
            },
        )

        # Create payload indexes
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="book_name",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="testament",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="verse_count",
            field_schema=PayloadSchemaType.INTEGER,
        )

        print(f"Created collection: {self.collection_name}")
        self._collection_exists = True
        return True

    def index_chunks(
        self,
        chunks,  # List[BibleSemanticChunk]
        batch_size: int = 100,  # Increased from 50
        show_progress: bool = True,
    ) -> int:
        """Index semantic chunks with dense vectors only."""
        if not self._collection_exists:
            self.create_collection()

        # Extract texts for encoding
        texts = [chunk.text for chunk in chunks]

        # Encode all texts (returns only dense vectors)
        print(f"Encoding {len(texts)} semantic chunks...")
        dense_vectors = self.encoder.encode_batch(
            texts, batch_size=batch_size, show_progress=show_progress
        )

        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0

        for i in tqdm(
            range(0, len(chunks), batch_size), desc="Indexing semantic chunks"
        ):
            batch_chunks = chunks[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_indexed += len(points)

        print(f"Indexed {total_indexed} Bible semantic chunks successfully!")
        return total_indexed

    async def index_chunks_async(
        self,
        chunks,  # List[BibleSemanticChunk]
        batch_size: int = 256,  # 5x larger for speed
        max_concurrent: int = 10,  # Parallel API calls
        upsert_batch_size: int = 500,  # Larger Qdrant batches
        show_progress: bool = True,
    ) -> int:
        """
        Async index semantic chunks with parallel embedding generation.

        Optimized for maximum speed:
        - batch_size=256: Larger batches reduce API overhead
        - max_concurrent=10: Parallel API calls for 2-3x speedup
        - upsert_batch_size=500: Bulk Qdrant inserts
        """
        from .embeddings import AsyncDenseEncoder

        if not self._collection_exists:
            self.create_collection()

        # Use async encoder
        async_encoder = AsyncDenseEncoder()

        # Extract texts for encoding
        texts = [chunk.text for chunk in chunks]

        # Encode all texts asynchronously (returns only dense vectors)
        print(f"Async encoding {len(texts)} Bible semantic chunks...")
        dense_vectors = await async_encoder.encode_batch_async(
            texts,
            batch_size=batch_size,
            max_concurrent=max_concurrent,
            show_progress=show_progress,
        )

        # Create points in batches (use larger upsert batches for speed)
        print(f"Indexing to Qdrant (batch_size={upsert_batch_size})...")
        total_indexed = 0

        for i in tqdm(range(0, len(chunks), upsert_batch_size), desc="Indexing"):
            batch_chunks = chunks[i : i + upsert_batch_size]
            batch_dense = dense_vectors[i : i + upsert_batch_size]

            points = []
            for j, chunk in enumerate(batch_chunks):
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload=chunk.to_dict(),
                )
                points.append(point)

            self.client.upsert(collection_name=self.collection_name, points=points)
            total_indexed += len(points)

        print(f"Async indexed {total_indexed} Bible semantic chunks!")
        return total_indexed

    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": getattr(info, "vectors_count", info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }


class TurkishBibleIndexer:
    """
    Indexes Turkish Bible verses into Qdrant with hybrid vectors.

    Creates two collections:
    - bible_tr_ot: Old Testament (39 books, ~22,724 verses)
    - bible_tr_nt: New Testament (27 books, ~7,458 verses)

    Optimized with:
    - HNSW: m=16, ef_construct=200
    - Scalar Quantization: int8 for 75% RAM reduction
    - Payload indexes: book, chapter, testament
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[DenseEncoder] = None,
        osis_file_path: Optional[str] = None,
    ):
        """
        Initialize Turkish Bible indexer.

        Args:
            qdrant_url: Qdrant server URL
            in_memory: Use in-memory Qdrant
            encoder: Dense encoder instance
            osis_file_path: Path to Turkish OSIS XML file
        """
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or DenseEncoder()

        # Default OSIS file path
        if osis_file_path is None:
            current = Path(__file__).parent
            if current.name == "src":
                data_dir = current.parent / "data"
            else:
                data_dir = current / "data"
            osis_file_path = str(data_dir / "turkish_bible" / "tur-turkish.osis.xml")

        self.osis_file_path = osis_file_path
        self._ot_collection_exists = False
        self._nt_collection_exists = False

    def _create_collection(self, collection_name: str, recreate: bool = False) -> bool:
        """
        Create collection with dense and sparse vector configuration.

        Args:
            collection_name: Name of collection to create
            recreate: If True, delete existing collection and create new

        Returns:
            True if collection was created, False if already exists
        """
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)

        if exists:
            if recreate:
                print(f"Deleting existing collection: {collection_name}")
                self.client.delete_collection(collection_name)
            else:
                print(f"Collection already exists: {collection_name}")
                return False

        # Get dense vector dimension
        dense_dim = self.encoder.dense_dimension
        print(
            f"Creating collection {collection_name} with dense dimension: {dense_dim}"
        )
        print("  HNSW config: m=16, ef_construct=200")
        print("  Quantization: Scalar int8 (75% RAM savings)")

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=16,
                        ef_construct=200,
                    ),
                    quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type="int8", quantile=0.99, always_ram=True
                        )
                    ),
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
            },
        )

        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="book",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="chapter",
            field_schema=PayloadSchemaType.INTEGER,
        )
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="testament",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="language",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        print(f"Created collection: {collection_name}")
        return True

    def _index_verses(
        self,
        collection_name: str,
        verses: List[Dict],
        batch_size: int = 100,
        show_progress: bool = True,
    ) -> int:
        """
        Index verses into a collection.

        Args:
            collection_name: Target collection name
            verses: List of verse dicts with keys: book, chapter, verse, text, testament
            batch_size: Batch size for encoding and indexing
            show_progress: Show progress bar

        Returns:
            Number of indexed verses
        """
        # Extract texts for encoding
        texts = [v["text"] for v in verses]

        # Encode all texts (returns only dense vectors)
        print(f"Encoding {len(texts)} verses...")
        dense_vectors = self.encoder.encode_batch(
            texts, batch_size=batch_size, show_progress=show_progress
        )

        # Create points in batches
        print(f"Indexing to Qdrant (collection: {collection_name})...")
        total_indexed = 0

        for i in tqdm(range(0, len(verses), batch_size), desc="Indexing"):
            batch_verses = verses[i : i + batch_size]
            batch_dense = dense_vectors[i : i + batch_size]

            points = []
            for j, verse in enumerate(batch_verses):
                # Create unique ID from book, chapter, verse
                verse_id = f"{verse['book']}:{verse['chapter']}:{verse['verse']}"

                point = PointStruct(
                    id=hash(verse_id) % (2**63),
                    vector={"dense": batch_dense[j]},
                    payload={
                        "book": verse["book"],
                        "chapter": verse["chapter"],
                        "verse": verse["verse"],
                        "text": verse["text"],
                        "testament": verse["testament"],
                        "language": "tr",
                    },
                )
                points.append(point)

            self.client.upsert(collection_name=collection_name, points=points)
            total_indexed += len(points)

        print(f"Indexed {total_indexed} verses successfully!")
        return total_indexed

    def index_ot(self, recreate: bool = False) -> int:
        """
        Index Old Testament verses from OSIS file.

        Args:
            recreate: If True, recreate collection

        Returns:
            Number of indexed verses
        """
        from .osis_loader import OsisLoader

        collection_name = "bible_tr_ot"

        # Create collection
        self._create_collection(collection_name, recreate=recreate)
        self._ot_collection_exists = True

        # Load verses
        loader = OsisLoader(self.osis_file_path)
        ot_verses, _ = loader.load()

        # Index verses
        return self._index_verses(collection_name, ot_verses)

    def index_nt(self, recreate: bool = False) -> int:
        """
        Index New Testament verses from OSIS file.

        Args:
            recreate: If True, recreate collection

        Returns:
            Number of indexed verses
        """
        from .osis_loader import OsisLoader

        collection_name = "bible_tr_nt"

        # Create collection
        self._create_collection(collection_name, recreate=recreate)
        self._nt_collection_exists = True

        # Load verses
        loader = OsisLoader(self.osis_file_path)
        _, nt_verses = loader.load()

        # Index verses
        return self._index_verses(collection_name, nt_verses)

    def index_all(self, recreate: bool = False) -> Dict[str, int]:
        """
        Index both Old and New Testament.

        Args:
            recreate: If True, recreate collections

        Returns:
            Dict with counts: {"ot": <count>, "nt": <count>}
        """
        print("\n" + "=" * 60)
        print("Indexing Turkish Bible - Old Testament")
        print("=" * 60)
        ot_count = self.index_ot(recreate=recreate)

        print("\n" + "=" * 60)
        print("Indexing Turkish Bible - New Testament")
        print("=" * 60)
        nt_count = self.index_nt(recreate=recreate)

        return {"ot": ot_count, "nt": nt_count}


if __name__ == "__main__":
    from .data_loader import QuranDataLoader

    # Test indexing
    print("Loading data...")
    loader = QuranDataLoader()
    chunks = loader.create_chunks()

    print(f"\nCreated {len(chunks)} chunks")

    print("\nInitializing indexer...")
    indexer = QuranIndexer()

    print("\nCreating collection...")
    indexer.create_collection(recreate=True)

    print("\nIndexing chunks...")
    indexer.index_chunks(chunks[:10])  # Test with first 10

    print("\nCollection info:")
    info = indexer.get_collection_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
