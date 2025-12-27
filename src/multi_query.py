"""
Multi-Query RAG Module

RAG-Fusion implementasyonu: Tek sorguyu birden fazla varyasyona 
dönüştürür, her biri için ayrı arama yapar, sonuçları RRF ile birleştirir.
"""
from typing import List, Optional
from dataclasses import dataclass
from qdrant_client.models import Prefetch, SparseVector

from src.query_enhancer import QueryEnhancer


class MultiQueryGenerator:
    """
    LLM ile sorgu varyasyonları üretir.
    
    Usage:
        generator = MultiQueryGenerator()
        queries = generator.generate("sabır ve namaz", n=3)
        # ["sabır ve namaz", "sabır", "namaz kılmak", "tahammül ibadet"]
    """
    
    def __init__(self):
        self._enhancer = None
    
    @property
    def enhancer(self):
        """Lazy load QueryEnhancer"""
        if self._enhancer is None:
            self._enhancer = QueryEnhancer()
        return self._enhancer
    
    def generate(self, query: str, n: int = 3) -> List[str]:
        """
        Sorgu varyasyonları üret.
        
        Args:
            query: Orijinal sorgu
            n: Üretilecek varyasyon sayısı (3 optimal)
            
        Returns:
            Orijinal + varyasyonlar listesi
        """
        prompt = f"""Aşağıdaki arama sorgusunu {n} farklı şekilde yaz.
Her varyasyon farklı kelimeler ve perspektifler kullanmalı.
Sadece sorguları yaz, her biri ayrı satırda, numarasız ve açıklamasız.

Sorgu: {query}

Varyasyonlar:"""

        try:
            response = self.enhancer._call_llm(prompt)
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            # Orijinal sorguyu başa ekle
            variations = [query] + lines[:n]
            return variations
        except Exception as e:
            print(f"Warning: Could not generate variations: {e}")
            return [query]  # Sadece orijinal


class ParallelKeywordParser:
    """
    Sorguyu kelimelere ayırır ve stop words filtreler.
    
    Usage:
        parser = ParallelKeywordParser()
        keywords = parser.parse("sabır ve namaz ile dua")
        # ["sabır", "namaz", "dua"]
    """
    
    TURKISH_STOP_WORDS = {
        "ve", "ile", "için", "de", "da", "bir", "bu", "şu", 
        "o", "onu", "onun", "olan", "gibi", "kadar", "ne",
        "ki", "mi", "mı", "mu", "mü", "ya", "veya", "ama",
        "fakat", "ancak", "hem", "çünkü", "eğer", "ise"
    }
    
    def parse(self, query: str) -> List[str]:
        """
        Sorguyu kelimelere ayır, stop words filtrele.
        
        Args:
            query: Arama sorgusu
            
        Returns:
            Filtrelenmiş kelime listesi
        """
        words = query.lower().split()
        keywords = [w for w in words if w not in self.TURKISH_STOP_WORDS and len(w) > 1]
        return keywords if keywords else words  # En az orijinal kelimeleri döndür


def create_multi_query_prefetches(
    queries: List[str],
    sparse_encoder,
    dense_encoder,
    limit_per_query: int = 20
) -> List[Prefetch]:
    """
    Birden fazla sorgu için prefetch listesi oluştur.
    
    Args:
        queries: Sorgu listesi
        sparse_encoder: BM25 encoder
        dense_encoder: Semantic encoder
        limit_per_query: Her prefetch için limit
        
    Returns:
        Prefetch listesi (her query için sparse + dense)
    """
    prefetches = []
    
    for query in queries:
        # Sparse (BM25) prefetch
        sparse_indices, sparse_values = sparse_encoder.query_embed(query)
        prefetches.append(Prefetch(
            query=SparseVector(indices=sparse_indices, values=sparse_values),
            using="sparse",
            limit=limit_per_query
        ))
        
        # Dense (Semantic) prefetch
        dense_vector = dense_encoder.encode(query)
        prefetches.append(Prefetch(
            query=dense_vector,
            using="dense",
            limit=limit_per_query
        ))
    
    return prefetches


def create_parallel_keyword_prefetches(
    keywords: List[str],
    sparse_encoder,
    limit_per_keyword: int = 20
) -> List[Prefetch]:
    """
    Her keyword için ayrı sparse prefetch oluştur.
    
    Args:
        keywords: Keyword listesi
        sparse_encoder: BM25 encoder
        limit_per_keyword: Her prefetch için limit
        
    Returns:
        Sparse prefetch listesi
    """
    prefetches = []
    
    for keyword in keywords:
        sparse_indices, sparse_values = sparse_encoder.query_embed(keyword)
        prefetches.append(Prefetch(
            query=SparseVector(indices=sparse_indices, values=sparse_values),
            using="sparse",
            limit=limit_per_keyword
        ))
    
    return prefetches


if __name__ == "__main__":
    # Test
    print("Testing MultiQueryGenerator...")
    generator = MultiQueryGenerator()
    
    print("\nTesting ParallelKeywordParser...")
    parser = ParallelKeywordParser()
    keywords = parser.parse("sabır ve namaz ile dua etmek")
    print(f"Keywords: {keywords}")
