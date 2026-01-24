"""
Query Enhancement Module

Enhances search queries using LLM for better semantic search results.
Uses OpenRouter API for query expansion and multi-query generation.
Supports strictly separated modes for Bible (English/KJV) and Quran (Turkish).
"""
import os
import json
import requests
from typing import List, Optional, Dict, Any


class QueryEnhancer:
    """
    LLM-powered query enhancement for sacred text search.
    
    Features:
    - distinct "corpus" modes: 'bible' (English KJV) and 'quran' (Turkish)
    - Query Expansion: Add synonyms and related terms appropriate for the corpus
    - Multi-Query: Generate multiple query perspectives
    - JSON Structured Output: Robust parsing for reliability
    
    Usage:
        enhancer = QueryEnhancer()
        
        # Bible Mode (Default) - Auto-translates to English
        expanded = enhancer.expand_query("Tanrı'nın sevgisi", corpus="bible")
        
        # Quran Mode - Keeps Turkish, finds Islamic synonyms
        expanded = enhancer.expand_query("sabır", corpus="quran")
    """
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "x-ai/grok-4.1-fast"
    
    # --- BIBLE PROMPTS (English / KJV) ---
    SYSTEM_PROMPT_BIBLE = """You are an expert Biblical Scholar and Linguist specializing in the King James Version (KJV).
Your goal is to convert user queries (which may be in Turkish or English) into precise search terms for a KJV database.

Step 1: Identify the language. If Turkish, translate accurately to English.
Step 2: Identify key biblical themes and archaic KJV synonyms (e.g., "you" -> "thee/thou", "love" -> "charity").
Step 3: Output the result strictly in the following JSON format:

{
    "original_language": "tr|en",
    "translated_query": "string (the English translation)",
    "expanded_terms": ["term1", "term2", "term3"],
    "final_search_query": "string (the optimized query string)"
}
"""
    FEW_SHOT_BIBLE = [
        {"role": "user", "content": "Make this query search-ready. Query: 'sabır'"},
        {"role": "assistant", "content": json.dumps({
            "original_language": "tr",
            "translated_query": "patience",
            "expanded_terms": ["longsuffering", "endurance", "waiting"],
            "final_search_query": "patience longsuffering endurance"
        })},
        {"role": "user", "content": "Make this query search-ready. Query: 'Jesus miracles'"},
        {"role": "assistant", "content": json.dumps({
            "original_language": "en",
            "translated_query": "Jesus miracles",
            "expanded_terms": ["wonders", "signs", "healing", "mighty works"],
            "final_search_query": "Jesus miracles wonders signs mighty works"
        })}
    ]

    # --- QURAN PROMPTS (Turkish) ---
    SYSTEM_PROMPT_QURAN = """Sen uzman bir İslam Alimi ve Dilbilimcususun.
Görevin Kuran aramaları için sorgu optimize etmektir.

KURALLAR:
1. Çıktıların TAMAMI %100 TÜRKÇE olmalıdır.
2. ASLA İngilizce kelime kullanma (örn: 'God', 'Judgment', 'Wrath' YASAK).
3. Eğer girdi İngilizce ise, önce Türkçeye çevir.
4. Sadece Türkçe ve İslami terminoloji kullan (örn: 'Judgment' -> 'Kıyamet', 'Hesap Günü').

Adım 1: Dili algıla. İngilizce ise Türkçeye çevir.
Adım 2: Sadece TÜRKÇE eşanlamlılar üret.
Adım 3: JSON formatında ver.

{
    "original_language": "tr|en",
    "translated_query": "string (Türkçe çevirisi)",
    "expanded_terms": ["terim1 (tr)", "terim2 (tr)"],
    "final_search_query": "string (Sadece Türkçe kelimeler)"
}
"""
    FEW_SHOT_QURAN = [
        {"role": "user", "content": "Bu sorguyu Kuran araması için hazırla. Sorgu: 'sabır'"},
        {"role": "assistant", "content": json.dumps({
            "original_language": "tr",
            "translated_query": "sabır",
            "expanded_terms": ["sebat", "direnç", "tahammül", "göğüs germek"],
            "final_search_query": "sabır sebat direnç tahammül"
        })},
        {"role": "user", "content": "Bu sorguyu Kuran araması için hazırla. Sorgu: 'God's mercy'"},
        {"role": "assistant", "content": json.dumps({
            "original_language": "en",
            "translated_query": "Allah'ın merhameti",
            "expanded_terms": ["rahmet", "rahman", "rahim", "bağışlama", "mağfiret"],
            "final_search_query": "Allah'ın merhameti rahmet rahman rahim mağfiret"
        })}
    ]

    def __init__(self, model: str = None, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required.")
        self.model = model or self.DEFAULT_MODEL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }
    
    def _call_llm_json(self, prompt: str, system_prompt: str, examples: List[Dict]) -> Dict[str, Any]:
        """Generic JSON LLM caller with dynamic context"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(examples)
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 500,
                    "temperature": 0.3
                },
                timeout=30
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return json.loads(content)
        except Exception as e:
            print(f"API Call failed: {e}")
            return {}

    def expand_query(self, query: str, corpus: str = "bible") -> str:
        """
        Expand query based on corpus context.
        corpus='bible': Translates to English, adds KJV terms.
        corpus='quran': Keeps/Translates to Turkish, adds Islamic terms.
        """
        if corpus == "quran":
            prompt = f"Bu sorguyu Kuran araması için hazırla. Sorgu: '{query}'"
            system_prompt = self.SYSTEM_PROMPT_QURAN
            examples = self.FEW_SHOT_QURAN
        else:
            prompt = f"Make this query search-ready. Query: '{query}'"
            system_prompt = self.SYSTEM_PROMPT_BIBLE
            examples = self.FEW_SHOT_BIBLE
            
        result = self._call_llm_json(prompt, system_prompt, examples)
        final_query = result.get("final_search_query", query)
        
        # Post-Processing: Safety Filter for Quran Mode
        if corpus == "quran":
            blacklist = {
                "god", "lord", "wrath", "tribulation", "judgment", "day", "bible", 
                "christ", "jesus", "spirit", "holy", "father", "son", "gospel",
                "eschaton", "last", "times", "of", "the", "and"
            }
            # Filter out blacklisted English terms (case-insensitive)
            terms = final_query.split()
            filtered_terms = [t for t in terms if t.lower() not in blacklist]
            final_query = " ".join(filtered_terms)
            
        return final_query
    
    def generate_multi_query(self, query: str, n: int = 3, corpus: str = "bible") -> List[str]:
        """Generate multiple query perspectives based on corpus."""
        if corpus == "quran":
            system_prompt = """Sen uzman bir İslam Alimisin.
            Görev: Kullanıcı sorgusunu temel alarak Türkçe Kuran araması için 3-5 farklı arama varyasyonu üret.
            
            KRİTİK KURAL: Çıktıların tümü TÜRKÇE olmalıdır. İngilizce sorgu gelirse Türkçeye çevir.
            
            Sadece geçerli JSON çıktısı ver:
            {"queries": ["sorgu 1", "sorgu 2 (eşanlamlılar)", "sorgu 3 (kavramsal)"]}"""
            prompt = f"Sorgu için {n} farklı Kuran arama perspektifi üret: '{query}'"
            examples = [] # Multi-query has specific prompt, examples less critical here
        else:
            system_prompt = """You are an expert Biblical Scholar.
            Task: Generate 3-5 different search queries for the King James Version (KJV) Bible.
            CRITICAL RULE: ALL OUTPUT MUST BE IN ENGLISH. If Turkish, translate first.
            
            Output valid JSON only:
            {"queries": ["query 1", "query 2", "query 3"]}"""
            prompt = f"Generate {n} KJV search perspectives for: '{query}'"
            examples = []

        result = self._call_llm_json(prompt, system_prompt, examples)
        return result.get("queries", [query])[:n]

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        enhancer = QueryEnhancer()
        
        print("--- BIBLE MODE TEST ---")
        q_bible = "Tanrı'nın sevgisi"
        print(f"TR Input: {q_bible}")
        print(f"Expanded: {enhancer.expand_query(q_bible, corpus='bible')}")
        
        print("\n--- QURAN MODE TEST ---")
        q_quran = "God's mercy" # Intentionally English to test translation back to TR
        print(f"EN Input: {q_quran}")
        print(f"Expanded: {enhancer.expand_query(q_quran, corpus='quran')}")
        
    except Exception as e:
        print(f"Test failed: {e}")
