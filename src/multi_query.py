"""
Multi-Query RAG Module

RAG-Fusion implementasyonu: Tek sorguyu birden fazla varyasyona 
dönüştürür, her biri için ayrı arama yapar, sonuçları RRF ile birleştirir.

Yeni: Adaptif sorgu sayısı - sorgu karmaşıklığına göre varyasyon sayısı belirlenir.
"""
from typing import List, Optional, Tuple
from dataclasses import dataclass
from qdrant_client.models import Prefetch, SparseVector

from src.query_enhancer import QueryEnhancer


# Türkçe stop words
TURKISH_STOP_WORDS = {
    "ve", "ile", "için", "de", "da", "bir", "bu", "şu", 
    "o", "onu", "onun", "olan", "gibi", "kadar", "ne",
    "ki", "mi", "mı", "mu", "mü", "ya", "veya", "ama",
    "fakat", "ancak", "hem", "çünkü", "eğer", "ise",
    "nasıl", "neden", "hangi", "kim", "ne", "nerede"
}


def calculate_query_complexity(query: str) -> Tuple[int, str]:
    """
    Sorgu karmaşıklığını analiz et ve uygun varyasyon sayısını belirle.
    
    Complexity factors:
    - Kelime sayısı
    - Stop word oranı  
    - Soru işareti/soru kelimeleri
    - Kavram çeşitliliği
    
    Returns:
        (n_queries, complexity_level): Önerilen sorgu sayısı ve seviye
    """
    words = query.lower().split()
    word_count = len(words)
    
    # Stop word oranı
    stop_count = sum(1 for w in words if w in TURKISH_STOP_WORDS)
    stop_ratio = stop_count / max(word_count, 1)
    
    # Soru mu?
    is_question = "?" in query or any(w in query.lower() for w in ["nasıl", "neden", "hangi", "kim", "nerede"])
    
    # Dini/özel terimler var mı?
    special_terms = {"allah", "kuran", "incil", "isa", "muhammed", "peygamber", "cennet", "cehennem", "namaz", "oruç"}
    has_special = any(w in query.lower() for w in special_terms)
    
    # Karmaşıklık skoru hesapla (0-10)
    complexity_score = 0
    
    # Kelime sayısı etkisi
    if word_count <= 2:
        complexity_score += 1  # Basit, tek kelime
    elif word_count <= 4:
        complexity_score += 3  # Orta
    else:
        complexity_score += 5  # Karmaşık, çok kelimeli
    
    # Stop word oranı yüksekse belirsiz sorgu
    if stop_ratio > 0.5:
        complexity_score += 2
    
    # Soru ise daha fazla perspektif gerekebilir
    if is_question:
        complexity_score += 2
    
    # Özel terimler varsa daha az varyasyon yeterli
    if has_special:
        complexity_score -= 1
    
    # Skor -> varyasyon sayısı
    if complexity_score <= 2:
        return (1, "simple")      # Basit sorgu, varyasyon gereksiz
    elif complexity_score <= 4:
        return (2, "moderate")    # Orta, 2 varyasyon
    elif complexity_score <= 6:
        return (3, "complex")     # Karmaşık, 3 varyasyon (default)
    else:
        return (5, "very_complex") # Çok karmaşık, 5 varyasyon


class MultiQueryGenerator:
    """
    LLM ile sorgu varyasyonları üretir.
    
    Yeni: Adaptif mod - sorgu karmaşıklığına göre otomatik varyasyon sayısı.
    
    Usage:
        generator = MultiQueryGenerator()
        
        # Manuel mod (eski davranış)
        queries = generator.generate("sabır ve namaz", n=3)
        
        # Adaptif mod (yeni)
        queries, info = generator.generate_adaptive("sabır ve namaz")
        # info = {"complexity": "moderate", "n_queries": 2}
    """
    
    def __init__(self):
        self._enhancer = None
    
    @property
    def enhancer(self):
        """Lazy load QueryEnhancer"""
        if self._enhancer is None:
            self._enhancer = QueryEnhancer()
        return self._enhancer
    
    def generate_adaptive(self, query: str) -> Tuple[List[str], dict]:
        """
        Adaptif sorgu varyasyonu üret.
        
        Sorgu karmaşıklığını analiz eder ve uygun sayıda varyasyon üretir.
        Basit sorgularda LLM çağrısından kaçınarak maliyet tasarrufu sağlar.
        
        Args:
            query: Orijinal sorgu
            
        Returns:
            (queries, info): Sorgu listesi ve analiz bilgisi
        """
        n_queries, complexity = calculate_query_complexity(query)
        
        info = {
            "complexity": complexity,
            "n_queries": n_queries,
            "original_query": query
        }
        
        # Basit sorgularda LLM çağrısı yapma
        if n_queries == 1:
            return [query], info
        
        # Karmaşık sorgularda varyasyon üret
        queries = self.generate(query, n=n_queries)
        return queries, info
    
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
