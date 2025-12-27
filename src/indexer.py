"""
Qdrant Indexer Module

Handles collection creation and document indexing with hybrid vectors.
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
)

from .data_loader import QuranChunk
from .embeddings import HybridEncoder


class QuranIndexer:
    """
    Indexes Quran chunks into Qdrant with hybrid vectors.
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
        
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE
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
