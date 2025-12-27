"""
Query Enhancement Module

LLM kullanarak arama sorgularını iyileştirme.
Uses OpenRouter API with gpt-5-nano model for query expansion and rewriting.
"""
import os
import requests
from typing import List, Optional


class QueryEnhancer:
    """
    LLM ile sorgu iyileştirme.
    
    Özellikler:
    - Query Expansion: Eşanlamlı kelimeler ekleme
    - Query Rewriting: Daha iyi arama için sorguyu yeniden yazma
    - Multi-Query: Tek sorgudan birden fazla perspektif üretme
    
    Usage:
        enhancer = QueryEnhancer()
        
        # Expand query with synonyms
        expanded = enhancer.expand_query("sabır ve namaz")
        
        # Generate multiple query perspectives
        queries = enhancer.generate_multi_query("Allah'ın rahmeti", n=3)
    """
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"  # Fast and affordable
    
    def __init__(self, model: str = None, api_key: str = None):
        """
        Initialize QueryEnhancer.
        
        Args:
            model: OpenRouter model identifier (default: openai/gpt-5-nano)
            api_key: OpenRouter API key (default: from OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.model = model or self.DEFAULT_MODEL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM API call and return response text"""
        response = requests.post(
            self.OPENROUTER_URL,
            headers=self._headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    def expand_query(self, query: str) -> str:
        """
        Sorguyu eşanlamlı kelimelerle genişlet.
        
        Args:
            query: Orijinal arama sorgusu
            
        Returns:
            Genişletilmiş sorgu metni
        """
        prompt = f"""Verilen Türkçe sorguyu Kuran ve dini metinlerde arama için genişlet.
Eşanlamlı ve ilgili kelimeleri ekle. Sadece genişletilmiş sorguyu döndür, açıklama yapma.

Sorgu: {query}
Genişletilmiş sorgu:"""
        
        return self._call_llm(prompt)
    
    def generate_multi_query(self, query: str, n: int = 3) -> List[str]:
        """
        Tek sorgudan birden fazla perspektif üret.
        
        Args:
            query: Orijinal arama sorgusu
            n: Üretilecek sorgu sayısı
            
        Returns:
            Farklı perspektiflerde sorgular listesi
        """
        prompt = f"""Verilen Türkçe sorguyu {n} farklı perspektiften yeniden yaz.
Her satıra bir sorgu yaz. Sadece sorguları döndür, numaralama veya açıklama yapma.

Orijinal: {query}"""
        
        content = self._call_llm(prompt)
        queries = [line.strip() for line in content.strip().split("\n") if line.strip()]
        # Remove numbering if present
        cleaned = []
        for q in queries:
            # Remove patterns like "1.", "1)", "1-", etc.
            if q and q[0].isdigit():
                parts = q.split(".", 1) if "." in q[:3] else q.split(")", 1) if ")" in q[:3] else [q]
                q = parts[-1].strip() if len(parts) > 1 else q
            if q:
                cleaned.append(q)
        return cleaned[:n]
    
    def rewrite_for_search(self, query: str) -> str:
        """
        Sorguyu daha iyi arama sonuçları için yeniden yaz.
        
        Args:
            query: Orijinal arama sorgusu
            
        Returns:
            Arama için optimize edilmiş sorgu
        """
        prompt = f"""Verilen sorguyu kutsal metinlerde (Kuran, İncil) arama için optimize et.
Daha spesifik ve arama dostu hale getir. Sadece optimize edilmiş sorguyu döndür.

Sorgu: {query}
Optimize edilmiş:"""
        
        return self._call_llm(prompt)


if __name__ == "__main__":
    # Test QueryEnhancer
    enhancer = QueryEnhancer()
    
    test_query = "Allah'ın rahmeti"
    
    print(f"Original: {test_query}")
    print(f"\nExpanded: {enhancer.expand_query(test_query)}")
    print(f"\nMulti-query:")
    for i, q in enumerate(enhancer.generate_multi_query(test_query), 1):
        print(f"  {i}. {q}")
    print(f"\nRewritten: {enhancer.rewrite_for_search(test_query)}")
