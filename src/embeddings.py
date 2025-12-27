"""
Embedding Module for Dense and Sparse Vectors

Provides both semantic (dense) and BM25 (sparse) embeddings for hybrid search.
Uses OpenRouter API with Qwen3-Embedding-8B model for dense embeddings.
"""
from typing import List, Tuple, Optional, Any
import numpy as np
import os
import requests
from tqdm import tqdm


class DenseEncoder:
    """
    Dense vector encoder using OpenRouter API with Qwen3-Embedding-8B.
    Provides semantic understanding of text with 4096-dimension embeddings.
    """
    
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
    DEFAULT_MODEL = "qwen/qwen3-embedding-8b"
    EMBEDDING_DIMENSION = 4096
    
    def __init__(self, model_name: str = None, api_key: str = None):
        """
        Initialize the OpenRouter Dense Encoder.
        
        Args:
            model_name: Model identifier (default: qwen/qwen3-embedding-8b)
            api_key: OpenRouter API key (default: from OPENROUTER_API_KEY env var)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        print(f"Initialized OpenRouter dense encoder: {self.model_name}")
    
    def encode(self, text: str) -> List[float]:
        """Encode a single text to dense vector using OpenRouter API"""
        response = requests.post(
            self.OPENROUTER_API_URL,
            headers=self._headers,
            json={
                "model": self.model_name,
                "input": text
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
    
    def encode_batch(self, texts: List[str], batch_size: int = 32, show_progress: bool = True, max_retries: int = 3) -> List[List[float]]:
        """
        Encode multiple texts to dense vectors.
        Processes in batches to avoid API limits.
        Includes retry logic for handling timeouts.
        
        Args:
            texts: List of texts to encode
            batch_size: Number of texts per API call
            show_progress: Show progress bar
            max_retries: Maximum retry attempts per batch
        """
        import time
        
        all_embeddings = []
        
        iterator = range(0, len(texts), batch_size)
        if show_progress:
            iterator = tqdm(iterator, desc="Encoding dense vectors")
        
        for i in iterator:
            batch = texts[i:i + batch_size]
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.OPENROUTER_API_URL,
                        headers=self._headers,
                        json={
                            "model": self.model_name,
                            "input": batch
                        },
                        timeout=180  # Increased timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Sort by index to maintain order
                    sorted_data = sorted(data["data"], key=lambda x: x["index"])
                    batch_embeddings = [item["embedding"] for item in sorted_data]
                    all_embeddings.extend(batch_embeddings)
                    break  # Success, exit retry loop
                    
                except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt * 5  # 5s, 10s, 20s
                        print(f"\nTimeout error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print(f"\nFailed after {max_retries} attempts. Raising error.")
                        raise
                        
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt * 5
                        print(f"\nAPI error: {e}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        raise
        
        return all_embeddings
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension (4096 for Qwen3-Embedding-8B)"""
        return self.EMBEDDING_DIMENSION


class SparseEncoder:
    """
    Sparse vector encoder using BM25.
    Provides keyword-based matching capabilities.
    """
    
    def __init__(self, model_name: str = "Qdrant/bm25"):
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            from fastembed import SparseTextEmbedding
            print(f"Loading sparse encoder: {self.model_name}")
            self._model = SparseTextEmbedding(model_name=self.model_name)
        return self._model
    
    def encode(self, text: str) -> Tuple[List[int], List[float]]:
        """
        Encode a single text to sparse vector.
        Returns (indices, values) tuple for Qdrant SparseVector.
        """
        embeddings = list(self.model.embed([text]))
        if embeddings:
            sparse = embeddings[0]
            return sparse.indices.tolist(), sparse.values.tolist()
        return [], []
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[Tuple[List[int], List[float]]]:
        """Encode multiple texts to sparse vectors"""
        results = []
        embeddings = list(self.model.embed(texts, batch_size=batch_size))
        for sparse in embeddings:
            results.append((sparse.indices.tolist(), sparse.values.tolist()))
        return results
    
    def query_embed(self, text: str) -> Tuple[List[int], List[float]]:
        """
        Encode query text for sparse search.
        Uses query_embed which is optimized for queries.
        """
        embeddings = list(self.model.query_embed(text))
        if embeddings:
            sparse = embeddings[0]
            return sparse.indices.tolist(), sparse.values.tolist()
        return [], []


class HybridEncoder:
    """
    Combined encoder for both dense and sparse embeddings.
    Uses OpenRouter Qwen3-Embedding-8B for dense and BM25 for sparse.
    """
    
    def __init__(
        self, 
        dense_model: str = None,  # Uses OpenRouter qwen/qwen3-embedding-8b by default
        sparse_model: str = "Qdrant/bm25",
        api_key: str = None
    ):
        self.dense_encoder = DenseEncoder(model_name=dense_model, api_key=api_key)
        self.sparse_encoder = SparseEncoder(sparse_model)
    
    def encode(self, text: str) -> Tuple[List[float], Tuple[List[int], List[float]]]:
        """Encode text to both dense and sparse vectors"""
        dense = self.dense_encoder.encode(text)
        sparse = self.sparse_encoder.encode(text)
        return dense, sparse
    
    def encode_batch(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        show_progress: bool = True
    ) -> Tuple[List[List[float]], List[Tuple[List[int], List[float]]]]:
        """Encode multiple texts to both dense and sparse vectors"""
        print("Encoding dense vectors...")
        dense_vectors = self.dense_encoder.encode_batch(texts, batch_size, show_progress)
        
        print("Encoding sparse vectors...")
        sparse_vectors = self.sparse_encoder.encode_batch(texts, batch_size)
        
        return dense_vectors, sparse_vectors
    
    @property
    def dense_dimension(self) -> int:
        return self.dense_encoder.dimension


if __name__ == "__main__":
    # Test encoders
    test_text = "Rahman ve Rahim olan Allah'ın adıyla"
    
    print("Testing Dense Encoder...")
    dense = DenseEncoder()
    dense_vec = dense.encode(test_text)
    print(f"Dense vector dimension: {len(dense_vec)}")
    print(f"Dense vector sample: {dense_vec[:5]}...")
    
    print("\nTesting Sparse Encoder...")
    sparse = SparseEncoder()
    indices, values = sparse.encode(test_text)
    print(f"Sparse vector non-zero elements: {len(indices)}")
    print(f"Indices sample: {indices[:5]}...")
    print(f"Values sample: {values[:5]}...")
    
    print("\nTesting Hybrid Encoder...")
    hybrid = HybridEncoder()
    d, s = hybrid.encode(test_text)
    print(f"Hybrid encoding successful!")
    print(f"Dense dim: {len(d)}, Sparse non-zeros: {len(s[0])}")
