"""
Reranker Module for RAG Pipeline

Uses SiliconFlow API (Qwen3-Reranker-8B) for re-ranking search results.
Fallback: If API fails or key is missing, returns original results.
"""
import os
import requests
import json
from typing import List, Union, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from rich.console import Console

console = Console()

class Reranker:
    """
    SiliconFlow API tabanlı yeniden sıralama (Qwen3-Reranker-8B).
    
    Usage:
        reranker = Reranker()
        reranked = reranker.rerank(query, results, top_k=5)
    """
    
    # Default model on SiliconFlow
    DEFAULT_MODEL = "Qwen/Qwen2.5-Reranker-8B"  # Updated to Qwen2.5 based on recommended ID, or Qwen/Qwen3-Reranker-8B
    # Note: Search results said Qwen3-Reranker-8B, but some docs might say Qwen2.5-Reranker. 
    # Validated: "Qwen/Qwen3-Reranker-8B" is the specific model ID for the 8B reranker on SiliconFlow.
    MODEL_ID = "Qwen/Qwen3-Reranker-8B"
    
    API_URL = "https://api.siliconflow.com/v1/rerank"
    
    def __init__(self, model_name: str = None):
        """
        Initialize Reranker.
        
        Args:
            model_name: Optional override for model ID
        """
        self.model_name = model_name or self.MODEL_ID
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        
        if not self.api_key:
            console.print("[yellow]Warning: SILICONFLOW_API_KEY not found. Reranking will be disabled (fallback mode).[/yellow]")
        else:
            console.print(f"[dim]Initialized Reranker with {self.model_name}[/dim]")
        
    def rerank(
        self, 
        query: str, 
        results: List, 
        top_k: int = 5,
        text_field: str = None
    ) -> List:
        """
        Arama sonuçlarını API üzerinden yeniden sırala.
        
        Args:
            query: Arama sorgusu
            results: SearchResult listesi
            top_k: Döndürülecek sonuç sayısı
            
        Returns:
            Yeniden sıralanmış sonuçlar
        """
        if not results:
            return results
            
        # Fallback if no key
        if not self.api_key:
            return results[:top_k]
            
        try:
            # Prepare documents for API
            documents = []
            for r in results:
                documents.append(self._get_text(r))
            
            # Call API
            payload = {
                "model": self.model_name,
                "query": query,
                "documents": documents,
                "top_n": top_k,
                "return_documents": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.API_URL, 
                json=payload, 
                headers=headers, 
                timeout=10  # 10s timeout
            )
            
            if response.status_code != 200:
                console.print(f"[red]Reranker API Error: {response.text}[/red]")
                return results[:top_k]
                
            data = response.json()
            
            # Process results
            # API returns: {"results": [{"index": 0, "relevance_score": 0.9}, ...]}
            api_results = data.get("results", [])
            
            reranked_results = []
            for item in api_results:
                original_index = item["index"]
                score = item["relevance_score"]
                
                original_result = results[original_index]
                original_result.score = score  # Update score
                reranked_results.append(original_result)
                
            return reranked_results
            
        except Exception as e:
            console.print(f"[yellow]Reranking failed (using fallback): {e}[/yellow]")
            return results[:top_k]
    
    def _get_text(self, result) -> str:
        """Helper to extract text from various result objects"""
        if hasattr(result, 'translation'):
            return result.translation
        elif hasattr(result, 'combined_translation'):
            return result.combined_translation
        elif hasattr(result, 'text'):
            return result.text
        else:
            return str(result)
            
    def rerank_with_scores(
        self, 
        query: str, 
        results: List, 
        top_k: int = 5,
        text_field: str = None
    ) -> List[tuple]:
        """
        Skorlarla birlikte yeniden sırala (Geriye dönük uyumluluk için).
        """
        reranked = self.rerank(query, results, top_k=top_k)
        return [(r, r.score) for r in reranked]


if __name__ == "__main__":
    # Test stub
    print("Testing SiliconFlow Reranker...")
    
    @dataclass
    class TestResult:
        translation: str
        score: float = 0.0
    
    test_docs = [
        TestResult("Namazlarına riayet ederler"),
        TestResult("Sabır ve namazla Allah'a sığınıp yardım isteyin"),
        TestResult("Güneşin batıya yönelmesinden gecenin kararmasına kadar namaz kıl"),
    ]
    
    # Needs valid key to work
    if os.getenv("SILICONFLOW_API_KEY"):
        reranker = Reranker()
        results = reranker.rerank("sabır ve namaz", test_docs, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"{i}. {r.translation} (Score: {r.score})")
    else:
        print("Skipping live test: SILICONFLOW_API_KEY not found")
