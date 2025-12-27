"""
Reranker Module for RAG Pipeline

Qwen3-Reranker ile arama sonuçlarını yeniden sıralama.
Cross-encoder modeli query-document çiftlerini değerlendirerek
daha hassas relevance skorları üretir.
"""
from typing import List, Union, Optional
from dataclasses import dataclass
import torch


class Reranker:
    """
    Qwen3-Reranker tabanlı yeniden sıralama.
    
    İlk arama sonuçlarını daha derin analiz ile yeniden sıralar.
    Cross-encoder modeli her query-document çiftini birlikte değerlendirir.
    
    Usage:
        from src.reranker import Reranker
        
        reranker = Reranker()
        reranked = reranker.rerank(query, results, top_k=5)
    """
    
    # Qwen3-Reranker-0.6B - hafif ve etkili reranker
    # 100+ dil desteği, Türkçe için iyi performans
    # Gerekirse 8B versiyonuna yükseltilebilir
    DEFAULT_MODEL = "tomaarsen/Qwen3-Reranker-0.6B-seq-cls"
    
    def __init__(self, model_name: str = None):
        """
        Initialize Reranker.
        
        Args:
            model_name: HuggingFace model adı
                       (default: tomaarsen/Qwen3-Reranker-8B-seq-cls)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model = None
        
    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            from sentence_transformers import CrossEncoder
            
            # GPU varsa kullan
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading reranker: {self.model_name} on {device}")
            
            self._model = CrossEncoder(
                self.model_name,
                device=device,
                trust_remote_code=True
            )
        return self._model
    
    def rerank(
        self, 
        query: str, 
        results: List, 
        top_k: int = 5,
        text_field: str = None
    ) -> List:
        """
        Arama sonuçlarını yeniden sırala.
        
        Args:
            query: Arama sorgusu
            results: SearchResult veya BibleSearchResult listesi
            top_k: Döndürülecek sonuç sayısı
            text_field: Metin alanı adı (otomatik tespit edilir)
            
        Returns:
            Yeniden sıralanmış sonuçlar
        """
        if not results:
            return results
            
        # Metin alanını tespit et
        if text_field is None:
            first = results[0]
            if hasattr(first, 'translation'):
                text_field = 'translation'
            elif hasattr(first, 'text'):
                text_field = 'text'
            else:
                raise ValueError("Cannot determine text field from results")
        
        # Query-document çiftleri oluştur
        pairs = [(query, getattr(r, text_field)) for r in results]
        
        # Skorları hesapla
        scores = self.model.predict(pairs, show_progress_bar=False)
        
        # Sonuçları skorlara göre sırala
        ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
        
        # Top-k sonuç döndür
        return [r for r, s in ranked[:top_k]]
    
    def rerank_with_scores(
        self, 
        query: str, 
        results: List, 
        top_k: int = 5,
        text_field: str = None
    ) -> List[tuple]:
        """
        Skorlarla birlikte yeniden sırala.
        
        Returns:
            [(result, score), ...] listesi
        """
        if not results:
            return []
            
        # Metin alanını tespit et
        if text_field is None:
            first = results[0]
            if hasattr(first, 'translation'):
                text_field = 'translation'
            elif hasattr(first, 'text'):
                text_field = 'text'
            else:
                raise ValueError("Cannot determine text field from results")
        
        pairs = [(query, getattr(r, text_field)) for r in results]
        scores = self.model.predict(pairs, show_progress_bar=False)
        
        ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


if __name__ == "__main__":
    # Test reranker
    print("Testing Qwen3-Reranker...")
    
    reranker = Reranker()
    
    # Basit test
    query = "sabır ve namaz"
    
    @dataclass
    class TestResult:
        translation: str
        score: float = 0.0
    
    test_docs = [
        TestResult("Namazlarına riayet ederler"),
        TestResult("Sabır ve namazla Allah'a sığınıp yardım isteyin"),
        TestResult("Güneşin batıya yönelmesinden gecenin kararmasına kadar namaz kıl"),
    ]
    
    ranked = reranker.rerank(query, test_docs, top_k=3)
    
    print(f"\nQuery: {query}")
    print("\nReranked results:")
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r.translation}")
