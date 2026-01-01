"""
Qdrant Indexer Module

Handles collection creation and document indexing with hybrid vectors.

Optimizations:
- HNSW config (m=16, ef_construct=200) for better search quality
- Scalar Quantization (int8) for 75% RAM savings
- Payload indexes for fast filtered searches
"""
from typing import List, Optional
from tqdm import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    Distance,
    PointStruct,
    SparseVector,
    HnswConfigDiff,
    ScalarQuantization,
    ScalarQuantizationConfig,
    PayloadSchemaType,
)

from .data_loader import QuranChunk
from .embeddings import HybridEncoder


class QuranIndexer:
    """
    Indexes Quran chunks into Qdrant with hybrid vectors.
    
    Optimized with:
    - HNSW: m=16, ef_construct=200 for quality-speed balance
    - Scalar Quantization: int8 for 75% RAM reduction
    - Payload indexes: surah_id, surah_type for filtered search
    """
    
    COLLECTION_NAME = "quran_tr"
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[HybridEncoder] = None
    ):
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or HybridEncoder()
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
        print(f"Creating collection with dense dimension: {dense_dim}")
        print(f"  HNSW config: m=16, ef_construct=200")
        print(f"  Quantization: Scalar int8 (75% RAM savings)")
        
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
                            type="int8",
                            quantile=0.99,
                            always_ram=True
                        )
                    )
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(
                        on_disk=False
                    )
                )
            }
        )
        
        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_id",
            field_schema=PayloadSchemaType.INTEGER
        )
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_type",
            field_schema=PayloadSchemaType.KEYWORD
        )
        
        print(f"Created collection: {self.COLLECTION_NAME}")
        self._collection_exists = True
        return True
    
    def index_chunks(
        self,
        chunks: List[QuranChunk],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> int:
        """
        Index chunks with both dense and sparse vectors.
        
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
        
        # Encode all texts
        print(f"Encoding {len(texts)} chunks...")
        dense_vectors, sparse_vectors = self.encoder.encode_batch(
            texts, 
            batch_size=batch_size,
            show_progress=show_progress
        )
        
        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Indexing"):
            batch_chunks = chunks[i:i + batch_size]
            batch_dense = dense_vectors[i:i + batch_size]
            batch_sparse = sparse_vectors[i:i + batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),  # Convert string ID to int
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            total_indexed += len(points)
        
        print(f"Indexed {total_indexed} chunks successfully!")
        return total_indexed
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "name": self.COLLECTION_NAME,
            "vectors_count": getattr(info, 'vectors_count', info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }
    
    async def index_chunks_async(
        self,
        chunks: List[QuranChunk],
        batch_size: int = 256,  # Optimized for OpenRouter API
        max_concurrent_embeddings: int = 10,  # OpenRouter has no rate limits with credits
        upsert_batch_size: int = 500,  # Qdrant upsert batch size (larger = faster)
        show_progress: bool = True
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
        import asyncio
        from .embeddings import AsyncHybridEncoder
        
        if not self._collection_exists:
            self.create_collection()
        
        # Use async encoder
        async_encoder = AsyncHybridEncoder()
        
        # Extract texts for encoding
        texts = [chunk.translation for chunk in chunks]
        
        # Encode all texts asynchronously
        print(f"Async encoding {len(texts)} chunks...")
        dense_vectors, sparse_vectors = await async_encoder.encode_batch_async(
            texts, 
            batch_size=batch_size,
            max_concurrent=max_concurrent_embeddings,
            show_progress=show_progress
        )
        
        # Create points in batches (use larger upsert batches for speed)
        print(f"Indexing to Qdrant (batch_size={upsert_batch_size})...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(chunks), upsert_batch_size), desc="Indexing"):
            batch_chunks = chunks[i:i + upsert_batch_size]
            batch_dense = dense_vectors[i:i + upsert_batch_size]
            batch_sparse = sparse_vectors[i:i + upsert_batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            total_indexed += len(points)
        
        print(f"Async indexed {total_indexed} chunks successfully!")
        return total_indexed


class BibleIndexer:
    """
    Indexes Bible chunks into Qdrant with hybrid vectors.
    Supports English translations (kjva, kjv).
    """
    
    def __init__(
        self,
        translation: str = "kjva",
        qdrant_url: str = "http://localhost:6333",
        in_memory: bool = False,
        encoder: Optional[HybridEncoder] = None
    ):
        self.translation = translation
        self.collection_name = f"bible_{translation}"
        
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or HybridEncoder()
        self._collection_exists = False
    
    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create collection with dense and sparse vector configuration.
        
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
        print(f"Creating collection with dense dimension: {dense_dim}")
        print(f"  HNSW config: m=16, ef_construct=200")
        print(f"  Quantization: Scalar int8 (75% RAM savings)")
        
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
                            type="int8",
                            quantile=0.99,
                            always_ram=True
                        )
                    )
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(
                        on_disk=False
                    )
                )
            }
        )
        
        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="book_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="testament",
            field_schema=PayloadSchemaType.KEYWORD
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="chapter",
            field_schema=PayloadSchemaType.INTEGER
        )
        
        print(f"Created collection: {self.collection_name}")
        self._collection_exists = True
        return True
    
    async def index_chunks(
        self,
        chunks,  # List[BibleChunk]
        batch_size: int = 100,
        max_concurrent: int = 20,  # High concurrency for paid tier
        upload_batch_size: int = 500,
        show_progress: bool = True
    ) -> int:
        """
        Index chunks with both dense and sparse vectors using async processing.
        
        Args:
            chunks: List of BibleChunk objects
            batch_size: Number of texts per API call (default: 100)
            max_concurrent: Maximum concurrent API calls (default: 8)
            upload_batch_size: Number of points per Qdrant upload (default: 500)
            show_progress: Show progress bar
            
        Returns:
            Number of indexed chunks
        """
        from .embeddings import AsyncHybridEncoder
        
        if not self._collection_exists:
            self.create_collection()
        
        # Use async encoder
        async_encoder = AsyncHybridEncoder()
        
        # Extract texts for encoding
        texts = [chunk.text for chunk in chunks]
        
        # Encode all texts asynchronously
        print(f"Encoding {len(texts)} chunks...")
        dense_vectors, sparse_vectors = await async_encoder.encode_batch_async(
            texts, 
            batch_size=batch_size,
            max_concurrent=max_concurrent,
            show_progress=show_progress
        )
        
        # Create all points
        print("Preparing points for upload...")
        points = []
        for i, chunk in enumerate(chunks):
            sparse_indices, sparse_values = sparse_vectors[i]
            point = PointStruct(
                id=hash(chunk.id) % (2**63),
                vector={
                    "dense": dense_vectors[i],
                    "sparse": SparseVector(
                        indices=sparse_indices,
                        values=sparse_values
                    )
                },
                payload=chunk.to_dict()
            )
            points.append(point)
        
        # Upload in larger batches
        print(f"Uploading {len(points)} points to Qdrant (batch={upload_batch_size})...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(points), upload_batch_size), desc="Uploading"):
            batch_points = points[i:i + upload_batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch_points,
                wait=True
            )
            total_indexed += len(batch_points)
        
        print(f"Indexed {total_indexed} chunks successfully!")
        return total_indexed
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "translation": self.translation,
            "vectors_count": getattr(info, 'vectors_count', info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }
    
    async def index_chunks_async(
        self,
        chunks,  # List[BibleChunk]
        batch_size: int = 256,  # Optimized for OpenRouter API
        max_concurrent_embeddings: int = 10,  # OpenRouter has no rate limits with credits
        upsert_batch_size: int = 500,  # Qdrant upsert batch size (larger = faster)
        show_progress: bool = True
    ) -> int:
        """
        Async index chunks with parallel embedding generation.
        
        Optimized for maximum speed:
        - batch_size=256: Larger batches reduce API overhead (8x increase)
        - max_concurrent=10: Parallel API calls (2x increase)
        - upsert_batch_size=500: Bulk Qdrant inserts
        
        Args:
            chunks: List of BibleChunk objects
            batch_size: Embedding batch size (default: 256)
            max_concurrent_embeddings: Max concurrent API calls (default: 10)
            upsert_batch_size: Points per Qdrant upsert (default: 500)
            show_progress: Show progress bar
            
        Returns:
            Number of indexed chunks
        """
        import asyncio
        from .embeddings import AsyncHybridEncoder
        
        if not self._collection_exists:
            self.create_collection()
        
        # Use async encoder
        async_encoder = AsyncHybridEncoder()
        
        # Extract texts for encoding
        texts = [chunk.text for chunk in chunks]
        
        # Encode all texts asynchronously
        print(f"Async encoding {len(texts)} Bible chunks...")
        dense_vectors, sparse_vectors = await async_encoder.encode_batch_async(
            texts, 
            batch_size=batch_size,
            max_concurrent=max_concurrent_embeddings,
            show_progress=show_progress
        )
        
        # Create points in batches (use larger upsert batches for speed)
        print(f"Indexing to Qdrant (batch_size={upsert_batch_size})...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(chunks), upsert_batch_size), desc="Indexing"):
            batch_chunks = chunks[i:i + upsert_batch_size]
            batch_dense = dense_vectors[i:i + upsert_batch_size]
            batch_sparse = sparse_vectors[i:i + upsert_batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                
                point = PointStruct(
                    id=hash(chunk.id) % (2**63),
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            total_indexed += len(points)
        
        print(f"Async indexed {total_indexed} Bible chunks successfully!")
        return total_indexed


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
        encoder: Optional[HybridEncoder] = None
    ):
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or HybridEncoder()
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
        print(f"  HNSW config: m=16, ef_construct=200")
        print(f"  Quantization: Scalar int8 (75% RAM savings)")
        
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
                            type="int8",
                            quantile=0.99,
                            always_ram=True
                        )
                    )
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(
                        on_disk=False
                    )
                )
            }
        )
        
        # Create payload indexes for fast filtered search
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_id",
            field_schema=PayloadSchemaType.INTEGER
        )
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="surah_type",
            field_schema=PayloadSchemaType.KEYWORD
        )
        self.client.create_payload_index(
            collection_name=self.COLLECTION_NAME,
            field_name="verse_count",
            field_schema=PayloadSchemaType.INTEGER
        )
        
        print(f"Created collection: {self.COLLECTION_NAME}")
        self._collection_exists = True
        return True
    
    def index_chunks(
        self,
        chunks,  # List[SemanticChunk]
        batch_size: int = 50,
        show_progress: bool = True
    ) -> int:
        """
        Index semantic chunks with both dense and sparse vectors.
        
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
        
        # Encode all texts
        print(f"Encoding {len(texts)} semantic chunks...")
        dense_vectors, sparse_vectors = self.encoder.encode_batch(
            texts, 
            batch_size=batch_size,
            show_progress=show_progress
        )
        
        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Indexing semantic chunks"):
            batch_chunks = chunks[i:i + batch_size]
            batch_dense = dense_vectors[i:i + batch_size]
            batch_sparse = sparse_vectors[i:i + batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),  # Convert string ID to int
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            total_indexed += len(points)
        
        print(f"Indexed {total_indexed} semantic chunks successfully!")
        return total_indexed
    
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "name": self.COLLECTION_NAME,
            "vectors_count": getattr(info, 'vectors_count', info.points_count),
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
        encoder: Optional[HybridEncoder] = None
    ):
        self.translation = translation
        self.collection_name = f"bible_{translation}_semantic_chunks"
        
        if in_memory:
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.encoder = encoder or HybridEncoder()
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
        print("Creating payload indexes...")
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="book_name",
            field_schema=PayloadSchemaType.KEYWORD
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="testament",
            field_schema=PayloadSchemaType.KEYWORD
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="verse_count",
            field_schema=PayloadSchemaType.INTEGER
        )
        
        print(f"Created collection: {self.collection_name}")
        self._collection_exists = True
        return True
    
    def index_chunks(
        self,
        chunks,  # List[BibleSemanticChunk]
        batch_size: int = 50,
        show_progress: bool = True
    ) -> int:
        """Index semantic chunks with both dense and sparse vectors."""
        if not self._collection_exists:
            self.create_collection()
        
        # Extract texts for encoding
        texts = [chunk.text for chunk in chunks]
        
        # Encode all texts
        print(f"Encoding {len(texts)} semantic chunks...")
        dense_vectors, sparse_vectors = self.encoder.encode_batch(
            texts, 
            batch_size=batch_size,
            show_progress=show_progress
        )
        
        # Create points in batches
        print("Indexing to Qdrant...")
        total_indexed = 0
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Indexing semantic chunks"):
            batch_chunks = chunks[i:i + batch_size]
            batch_dense = dense_vectors[i:i + batch_size]
            batch_sparse = sparse_vectors[i:i + batch_size]
            
            points = []
            for j, chunk in enumerate(batch_chunks):
                sparse_indices, sparse_values = batch_sparse[j]
                
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),
                    vector={
                        "dense": batch_dense[j],
                        "sparse": SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload=chunk.to_dict()
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            total_indexed += len(points)
        
        print(f"Indexed {total_indexed} Bible semantic chunks successfully!")
        return total_indexed
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": getattr(info, 'vectors_count', info.points_count),
            "points_count": info.points_count,
            "status": info.status,
        }


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
