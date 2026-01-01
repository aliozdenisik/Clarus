"""
Query Enhancement Module

Enhances search queries using LLM for better semantic search results.
Uses OpenRouter API for query expansion, translation, and rewriting.

Key feature: Automatically translates Turkish queries to English for KJVA Bible search.
"""
import os
import requests
from typing import List, Optional


class QueryEnhancer:
    """
    LLM-powered query enhancement for sacred text search.
    
    Features:
    - Query Expansion: Add synonyms and related biblical terms
    - Query Translation: Translate Turkish queries to English for KJVA
    - Query Rewriting: Optimize queries for search
    - Multi-Query: Generate multiple query perspectives
    
    Usage:
        enhancer = QueryEnhancer()
        
        # Expand query with synonyms (auto-translates Turkish to English)
        expanded = enhancer.expand_query("Tanrı'nın sevgisi")
        
        # Generate multiple query perspectives
        queries = enhancer.generate_multi_query("God's mercy", n=3)
    """
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"  # Fast and affordable
    
    # System prompt for Turkish-to-English translation and query enhancement
    SYSTEM_PROMPT = """You are a biblical search query optimizer. Your task is to help users find relevant passages in the King James Version Bible (KJVA).

IMPORTANT RULES:
1. If the input query is in Turkish, FIRST translate it to English
2. Then expand the English query with synonyms and related biblical terms
3. Use KJV-style language where appropriate (thee, thou, hath, etc.)
4. Keep the output concise - just the optimized query
5. Do not include explanations or numbering"""

    def __init__(self, model: str = None, api_key: str = None):
        """
        Initialize QueryEnhancer.
        
        Args:
            model: OpenRouter model identifier (default: google/gemini-2.5-flash-lite)
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
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make LLM API call and return response text"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            self.OPENROUTER_URL,
            headers=self._headers,
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": 200
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
    def expand_query(self, query: str) -> str:
        """
        Expand query with synonyms and related terms.
        Automatically translates Turkish queries to English.
        
        Args:
            query: Original search query (Turkish or English)
            
        Returns:
            Expanded English query optimized for KJVA Bible search
        """
        prompt = f"""Expand this query for searching the King James Bible.
If it's in Turkish, translate to English first. Add synonyms and biblical terms.
Only return the expanded query, no explanation.

Query: {query}
Expanded query:"""
        
        return self._call_llm(prompt, self.SYSTEM_PROMPT)
    
    def generate_multi_query(self, query: str, n: int = 3) -> List[str]:
        """
        Generate multiple query perspectives from a single query.
        Translates Turkish to English if needed.
        
        Args:
            query: Original search query
            n: Number of queries to generate
            
        Returns:
            List of query variations in English
        """
        prompt = f"""Generate {n} different search queries for the King James Bible based on this query.
If the original is in Turkish, translate ALL outputs to English.
Put each query on a new line. No numbering or explanations.

Original: {query}"""
        
        content = self._call_llm(prompt, self.SYSTEM_PROMPT)
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
        Rewrite query for better search results.
        Translates Turkish to English if needed.
        
        Args:
            query: Original search query
            
        Returns:
            Search-optimized English query
        """
        prompt = f"""Rewrite this query for searching the King James Bible (KJVA).
If it's in Turkish, translate to English first.
Make it specific and search-friendly. Only return the optimized query.

Query: {query}
Optimized:"""
        
        return self._call_llm(prompt, self.SYSTEM_PROMPT)
    
    def translate_to_english(self, query: str) -> str:
        """
        Translate a Turkish query to English.
        If already in English, returns as-is.
        
        Args:
            query: Query in any language
            
        Returns:
            English translation
        """
        prompt = f"""If this text is in Turkish, translate it to English.
If it's already in English, return it unchanged.
Only return the translation, no explanation.

Text: {query}
English:"""
        
        return self._call_llm(prompt)
    
    def translate_for_bible(self, query: str) -> str:
        """
        Türkçe sorguyu King James İncil (KJVA) araması için İngilizceye çevir.
        
        Args:
            query: Türkçe arama sorgusu
            
        Returns:
            İngilizce'ye çevrilmiş ve İncil terminolojisine uygun sorgu
        """
        prompt = f"""Translate the following Turkish query to English for searching in the King James Bible.
Use proper Biblical terminology and phrasing. Return ONLY the English translation, no explanations.

Turkish query: {query}
English translation:"""
        
        return self._call_llm(prompt)


if __name__ == "__main__":
    # Test QueryEnhancer
    enhancer = QueryEnhancer()
    
    # Test with Turkish query
    test_query_tr = "Tanrı'nın sevgisi ve merhameti"
    print(f"Turkish Query: {test_query_tr}")
    print(f"Expanded (English): {enhancer.expand_query(test_query_tr)}")
    
    # Test with English query
    test_query_en = "God's love and mercy"
    print(f"\nEnglish Query: {test_query_en}")
    print(f"Expanded: {enhancer.expand_query(test_query_en)}")
    
    print(f"\nMulti-query (from Turkish):")
    for i, q in enumerate(enhancer.generate_multi_query(test_query_tr), 1):
        print(f"  {i}. {q}")
