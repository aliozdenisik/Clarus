"""
Query Enhancement Module

Enhances search queries using LLM for better semantic search results.
Uses OpenRouter API for query expansion and multi-query generation.
Supports strictly separated modes for Bible (English/KJV) and Quran (Turkish).
"""

import json
import os
import re
import time
import warnings
from typing import Any

import requests
import sentry_sdk
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.logging_config import get_logger
from src.circuit_breaker import CircuitBreakerError, llm_with_breaker
from src.prompts import PromptManager

logger = get_logger(__name__)


class KeywordSuggestion(BaseModel):
    """A suggested keyword extracted from a query.

    Attributes:
        text: The keyword text
        language: Language code ("tr" for Turkish, "en" for English, "ar" for Arabic)
        confidence: Confidence score 0.0-1.0 (1.0 = high confidence)
        selected: Whether keyword is selected by default in frontend
        source: Extraction method ("llm", "rule_based", "fallback")
    """

    text: str = Field(..., description="Keyword text")
    language: str = Field(default="tr", description="Language code: tr, en, ar")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    selected: bool = Field(default=True, description="Default selection state in UI")
    source: str = Field(default="llm", description="Extraction method: llm, rule_based, fallback")


class EnhanceResponse(BaseModel):
    """Complete query enhancement response with keywords and metadata.

    Attributes:
        original_query: User's original input query
        keywords: List of extracted/suggested keywords
        corpus: Target corpus ("quran" or "bible")
    """

    original_query: str = Field(..., description="Original user query")
    keywords: list[KeywordSuggestion] = Field(default_factory=list, description="Extracted keywords")
    corpus: str = Field(default="bible", description="Target corpus: quran or bible")


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
    # Switched from x-ai/grok-4.1-fast (reasoning model, 13s latency due to
    # internal thinking tokens) to Gemini 2.5 Flash (~1s for same task).
    # Query expansion is a simple JSON extraction — no reasoning needed.
    DEFAULT_MODEL = "google/gemini-2.5-flash"

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
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "original_language": "tr",
                    "translated_query": "patience",
                    "expanded_terms": ["longsuffering", "endurance", "waiting"],
                    "final_search_query": "patience longsuffering endurance",
                }
            ),
        },
        {
            "role": "user",
            "content": "Make this query search-ready. Query: 'Jesus miracles'",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "original_language": "en",
                    "translated_query": "Jesus miracles",
                    "expanded_terms": ["wonders", "signs", "healing", "mighty works"],
                    "final_search_query": "Jesus miracles wonders signs mighty works",
                }
            ),
        },
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
Adım 2: TÜRKÇE eşanlamlılar ve çeviri varyantları üret.
- Eşanlamlılar: Aynı anlama gelen farklı Türkçe kelimeler (sabır → sebat, tahammül)
- Çeviri varyantları: Arapça kökenli İslami terimlerin bu Kuran çevirisinde kullanılan Türkçe karşılıkları (tabut → sandık, salat → namaz)
NOT: Sadece kullanıcı sorgusunda bulunan terimleri genişlet. Yeni kavramlar ekleme.
Adım 3: JSON formatında ver.

{
    "original_language": "tr|en",
    "translated_query": "string (Türkçe çevirisi)",
    "expanded_terms": ["terim1 (tr)", "terim2 (tr)"],
    "final_search_query": "string (Sadece Türkçe kelimeler)"
}
"""
    FEW_SHOT_QURAN = [
        {
            "role": "user",
            "content": "Bu sorguyu Kuran araması için hazırla. Sorgu: 'sabır'",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "original_language": "tr",
                    "translated_query": "sabır",
                    "expanded_terms": ["sebat", "direnç", "tahammül", "göğüs germek"],
                    "final_search_query": "sabır sebat direnç tahammül",
                }
            ),
        },
        {
            "role": "user",
            "content": "Bu sorguyu Kuran araması için hazırla. Sorgu: 'God's mercy'",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "original_language": "en",
                    "translated_query": "Allah'ın merhameti",
                    "expanded_terms": [
                        "rahmet",
                        "rahman",
                        "rahim",
                        "bağışlama",
                        "mağfiret",
                    ],
                    "final_search_query": "Allah'ın merhameti rahmet rahman rahim mağfiret",
                }
            ),
        },
        {
            "role": "user",
            "content": "Bu sorguyu Kuran araması için hazırla. Sorgu: 'tabut'",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "original_language": "tr",
                    "translated_query": "tabut",
                    "expanded_terms": ["sandık", "ahit sandığı", "kutsal sandık"],
                    "final_search_query": "tabut sandık ahit sandığı",
                }
            ),
        },
    ]

    def __init__(self, model: str | None = None, api_key: str | None = None, locale: str = "tr"):
        """
        Initialize Query Enhancer with OpenRouter API.

        Args:
            model: LLM model identifier (default: Grok 4.1 Fast)
            api_key: OpenRouter API key (default: from OPENROUTER_API_KEY env var)
            locale: Language code for prompts ("tr" or "en", default: "tr")
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required.")
        self.model = model or self.DEFAULT_MODEL
        self.locale = locale
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }
        self._prompt_manager = PromptManager()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=lambda rs: logger.info(f"Retrying LLM call, attempt {rs.attempt_number}/5"),
    )
    def _call_llm_json(self, prompt: str, system_prompt: str, examples: list[dict]) -> dict[str, Any]:
        """Generic JSON LLM caller with dynamic context"""
        with sentry_sdk.start_span(
            op="llm.openrouter.query_enhancer", description="Query enhancement LLM call"
        ) as span:
            start_time = time.time()
            span.set_data("model", self.model)

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(examples)
            messages.append({"role": "user", "content": prompt})

            try:
                response = llm_with_breaker(
                    lambda: requests.post(
                        self.OPENROUTER_URL,
                        headers=self._headers,
                        json={
                            "model": self.model,
                            "messages": messages,
                            "response_format": {"type": "json_object"},
                            "max_tokens": 500,
                            "temperature": 0.3,
                        },
                        timeout=30,
                    )
                )
                response.raise_for_status()
                response_json = response.json()

                # Defensive parsing for LLM response
                if "choices" not in response_json or not response_json["choices"]:
                    logger.error(f"Invalid LLM response: missing 'choices'. Response: {response_json}")
                    raise ValueError("Invalid LLM response: missing 'choices' field")

                choice = response_json["choices"][0]
                if "message" not in choice or "content" not in choice.get("message", {}):
                    logger.error(f"Invalid LLM response structure: {choice}")
                    raise ValueError("Invalid LLM response: missing message content")

                content = choice["message"]["content"].strip()

                # Token tracking
                usage = response_json.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)

                sentry_sdk.set_measurement("llm.tokens.input", input_tokens, "none")
                sentry_sdk.set_measurement("llm.tokens.output", output_tokens, "none")

                # Simple cost estimate (OpenRouter typical pricing)
                estimated_cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
                sentry_sdk.set_measurement("llm.cost.estimated", estimated_cost, "none")

                span.set_data("input_tokens", input_tokens)
                span.set_data("output_tokens", output_tokens)

                # Set latency before return
                latency_ms = (time.time() - start_time) * 1000
                span.set_data("latency_ms", latency_ms)

                return json.loads(content)
            except CircuitBreakerError:
                # Circuit breaker open - fail fast, do NOT retry
                logger.warning("Circuit breaker OPEN for LLM - query enhancement failed")
                return {}
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                # Let these propagate to @retry decorator
                raise
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Parse errors - don't retry
                logger.error(f"Response parsing failed: {e}")
                return {}
            except Exception as e:
                # Other errors (HTTP errors, etc.) - don't retry
                logger.error(f"API Call failed: {e}")
                return {}

    def expand_query(self, query: str, corpus: str = "bible") -> str:
        """
        Expand query based on corpus context.
        corpus='bible': Translates to English, adds KJV terms.
        corpus='quran': Keeps/Translates to Turkish, adds Islamic terms.
        """
        logger.info(
            "Query expansion started",
            extra={"corpus": corpus, "original_query": query[:50]},
        )

        if corpus == "quran":
            prompt = (
                f"Bu sorguyu Kuran araması için hazırla. Sorgu: '{query}'"
                if self.locale == "tr"
                else f"Prepare this query for Quran search. Query: '{query}'"
            )
            system_prompt = self._prompt_manager.get_prompt("query_enhancer", "quran_system", self.locale)
            examples = self._prompt_manager.get_prompt("query_enhancer", "quran_few_shot")
        else:
            prompt = (
                f"Make this query search-ready. Query: '{query}'"
                if self.locale == "en"
                else f"Bu sorguyu arama için hazırla. Sorgu: '{query}'"
            )
            system_prompt = self._prompt_manager.get_prompt("query_enhancer", "bible_system", self.locale)
            examples = self._prompt_manager.get_prompt("query_enhancer", "bible_few_shot")

        result = self._call_llm_json(prompt, system_prompt, examples)
        final_query = result.get("final_search_query", query)

        # Post-Processing: Safety Filter for Quran Mode
        if corpus == "quran":
            blacklist = {
                "god",
                "lord",
                "wrath",
                "tribulation",
                "judgment",
                "day",
                "bible",
                "christ",
                "jesus",
                "spirit",
                "holy",
                "father",
                "son",
                "gospel",
                "eschaton",
                "last",
                "times",
                "of",
                "the",
                "and",
            }
            # Filter out blacklisted English terms (case-insensitive)
            terms = final_query.split()
            filtered_terms = [t for t in terms if t.lower() not in blacklist]
            final_query = " ".join(filtered_terms)

        logger.info(
            "Query expansion completed",
            extra={"corpus": corpus, "expanded_query": final_query[:80]},
        )
        return final_query

    def extract_keywords(self, query: str, corpus: str = "bible") -> list[KeywordSuggestion]:
        """
        Extract structured keywords from query using hybrid rule-based + LLM approach.

        This is the FOUNDATION method for multi-keyword search enhancement. It extracts
        and suggests relevant keywords that can be individually toggled in the frontend.

        Algorithm:
        1. Rule-based layer: Split on conjunctions (ve, veya, ile, and, or, with, commas)
        2. LLM layer: For complex/single-word queries, reuse expand_query() LLM results
        3. Deduplication: Turkish-aware normalization (ı→i, İ→I, ö→o, ü→u, ş→s, ç→c, ğ→g)
        4. Blacklist filter: Remove Quran English terms when corpus="quran"
        5. Selection: First 7 keywords marked selected=True, rest selected=False

        Args:
            query: User's search query (Turkish or English)
            corpus: Target corpus ("quran" or "bible")

        Returns:
            List of KeywordSuggestion objects with metadata
        """
        logger.info(
            "Keyword extraction started",
            extra={
                "corpus": corpus,
                "query_length": len(query),
                "original_query": query[:50],
            },
        )

        if not query or not query.strip():
            logger.warning("Empty query provided to extract_keywords")
            return []

        query = query.strip()
        keywords = []
        extraction_method = "unknown"

        # Step 1: Rule-based splitting on conjunctions
        # Turkish: ve, veya, ile | English: and, or, with | Universal: comma
        conjunction_pattern = r"\s+ve\s+|\s+veya\s+|\s+ile\s+|\s+and\s+|\s+or\s+|\s+with\s+|,\s*"
        parts = [p.strip() for p in re.split(conjunction_pattern, query, flags=re.IGNORECASE) if p.strip()]

        if len(parts) >= 2:
            # Multiple parts found - use rule-based extraction
            extraction_method = "rule_based"
            for part in parts:
                if part:  # Non-empty after strip
                    keywords.append(
                        KeywordSuggestion(
                            text=part,
                            language="tr" if corpus == "quran" else "en",
                            confidence=1.0,
                            selected=True,
                            source="rule_based",
                        )
                    )
            logger.info(
                "Rule-based extraction succeeded",
                extra={"method": extraction_method, "parts_found": len(parts)},
            )
        else:
            # Step 2: LLM-based extraction for single-word or complex queries
            # Reuse expand_query()'s LLM call and extract keywords from expanded_terms
            extraction_method = "llm"
            try:
                # Select prompts based on corpus (same logic as expand_query)
                if corpus == "quran":
                    prompt = (
                        f"Bu sorguyu Kuran araması için hazırla. Sorgu: '{query}'"
                        if self.locale == "tr"
                        else f"Prepare this query for Quran search. Query: '{query}'"
                    )
                    system_prompt = self._prompt_manager.get_prompt("query_enhancer", "quran_system", self.locale)
                    examples = self._prompt_manager.get_prompt("query_enhancer", "quran_few_shot")
                else:
                    prompt = (
                        f"Make this query search-ready. Query: '{query}'"
                        if self.locale == "en"
                        else f"Bu sorguyu arama için hazırla. Sorgu: '{query}'"
                    )
                    system_prompt = self._prompt_manager.get_prompt("query_enhancer", "bible_system", self.locale)
                    examples = self._prompt_manager.get_prompt("query_enhancer", "bible_few_shot")

                # Call LLM with existing infrastructure (retries, circuit breaker, etc.)
                result = self._call_llm_json(prompt, system_prompt, examples)

                if result:
                    # Extract keywords from LLM response
                    expanded_terms = result.get("expanded_terms", [])
                    translated_query = result.get("translated_query", query)

                    # Add expanded terms as keywords
                    for term in expanded_terms:
                        if term:
                            keywords.append(
                                KeywordSuggestion(
                                    text=term,
                                    language="tr" if corpus == "quran" else "en",
                                    confidence=0.9,
                                    selected=True,
                                    source="llm",
                                )
                            )

                    # Add translated query if different from original
                    if translated_query and translated_query.lower() != query.lower():
                        keywords.append(
                            KeywordSuggestion(
                                text=translated_query,
                                language="tr" if corpus == "quran" else "en",
                                confidence=0.95,
                                selected=True,
                                source="llm",
                            )
                        )

                    # Add original query terms as fallback
                    original_parts = query.split()
                    for part in original_parts:
                        if part and len(part) > 1:  # Skip single characters
                            keywords.append(
                                KeywordSuggestion(
                                    text=part,
                                    language="tr" if corpus == "quran" else "en",
                                    confidence=1.0,
                                    selected=True,
                                    source="llm",
                                )
                            )

                    logger.info(
                        "LLM extraction succeeded",
                        extra={
                            "method": extraction_method,
                            "keywords_extracted": len(keywords),
                        },
                    )
                else:
                    # LLM returned empty - fallback to simple split
                    extraction_method = "fallback"
                    raise ValueError("LLM returned empty result")

            except Exception as e:
                # Step 3: Fallback - simple word splitting
                extraction_method = "fallback"
                logger.warning(
                    f"LLM extraction failed, using fallback: {e}",
                    extra={"error": str(e), "query": query[:50]},
                )
                words = query.split()
                for word in words:
                    if word and len(word) > 1:  # Skip single characters
                        keywords.append(
                            KeywordSuggestion(
                                text=word,
                                language="tr" if corpus == "quran" else "en",
                                confidence=0.8,
                                selected=True,
                                source="fallback",
                            )
                        )

        # Step 4: Deduplication with Turkish character normalization
        def normalize_turkish(text: str) -> str:
            """Normalize Turkish characters for case-insensitive comparison."""
            text = text.lower()
            # Turkish-specific mappings
            tr_map = str.maketrans(
                {
                    "ı": "i",
                    "İ": "i",
                    "ö": "o",
                    "Ö": "o",
                    "ü": "u",
                    "Ü": "u",
                    "ş": "s",
                    "Ş": "s",
                    "ç": "c",
                    "Ç": "c",
                    "ğ": "g",
                    "Ğ": "g",
                }
            )
            return text.translate(tr_map)

        seen = set()
        deduplicated = []
        for kw in keywords:
            normalized = normalize_turkish(kw.text)
            if normalized not in seen and normalized:  # Skip empty after normalization
                seen.add(normalized)
                deduplicated.append(kw)

        keywords = deduplicated

        # Step 5: Blacklist filter for Quran mode (same as expand_query)
        if corpus == "quran":
            blacklist = {
                "god",
                "lord",
                "wrath",
                "tribulation",
                "judgment",
                "day",
                "bible",
                "christ",
                "jesus",
                "spirit",
                "holy",
                "father",
                "son",
                "gospel",
                "eschaton",
                "last",
                "times",
                "of",
                "the",
                "and",
            }
            keywords = [kw for kw in keywords if normalize_turkish(kw.text) not in blacklist]
            logger.info(
                "Quran blacklist filter applied",
                extra={"keywords_after_filter": len(keywords)},
            )

        # Step 6: Selection limit - first 7 selected, rest unselected
        for i, kw in enumerate(keywords):
            if i >= 7:
                kw.selected = False

        logger.info(
            "Keyword extraction completed",
            extra={
                "method": extraction_method,
                "count": len(keywords),
                "selected_count": sum(1 for kw in keywords if kw.selected),
                "corpus": corpus,
            },
        )

        return keywords

    def generate_multi_query(self, query: str, n: int = 3, corpus: str = "bible") -> list[str]:
        """Generate multiple query perspectives based on corpus."""
        logger.info(
            "Multi-query generation started",
            extra={"corpus": corpus, "n": n, "original_query": query[:50]},
        )

        if corpus == "quran":
            system_prompt = """Sen uzman bir İslam Alimisin.
            Görev: Kullanıcı sorgusunu temel alarak Türkçe Kuran araması için 3-5 farklı arama varyasyonu üret.

            KRİTİK KURAL: Çıktıların tümü TÜRKÇE olmalıdır. İngilizce sorgu gelirse Türkçeye çevir.

            Sadece geçerli JSON çıktısı ver:
            {"queries": ["sorgu 1", "sorgu 2 (eşanlamlılar)", "sorgu 3 (kavramsal)"]}"""
            prompt = f"Sorgu için {n} farklı Kuran arama perspektifi üret: '{query}'"
            examples = []  # Multi-query has specific prompt, examples less critical here
        else:
            system_prompt = """You are an expert Biblical Scholar.
            Task: Generate 3-5 different search queries for the King James Version (KJV) Bible.
            CRITICAL RULE: ALL OUTPUT MUST BE IN ENGLISH. If Turkish, translate first.

            Output valid JSON only:
            {"queries": ["query 1", "query 2", "query 3"]}"""
            prompt = f"Generate {n} KJV search perspectives for: '{query}'"
            examples = []

        result = self._call_llm_json(prompt, system_prompt, examples)
        queries = result.get("queries", [query])[:n]

        logger.info(
            "Multi-query generation completed",
            extra={
                "corpus": corpus,
                "query_count": len(queries),
                "queries": queries[:3],
            },
        )
        return queries

    def translate_for_bible(self, query: str) -> str:
        """
        Translate Turkish query to English for Bible (KJV) search.

        Bible (KJV) is in English, so Turkish queries must be translated
        to get accurate search results.

        .. deprecated::
            Use :class:`QueryTranslator.translate_query()` instead.
        """
        warnings.warn(
            "translate_for_bible() is deprecated. Use QueryTranslator.translate_query() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        system_prompt = """You are a translation expert specializing in Biblical terminology.
Your task: Translate the Turkish query into English for searching the King James Version (KJV) Bible.

RULES:
1. Translate accurately, preserving religious/theological meaning
2. Use KJV-appropriate English vocabulary where possible (e.g., "thee", "thou" for archaic terms)
3. If the query is already in English, return it as-is

Output valid JSON only:
{"english_query": "the translated query in English"}"""

        prompt = f"Translate this Turkish query to English for KJV Bible search: '{query}'"

        result = self._call_llm_json(prompt, system_prompt, [])
        translated = result.get("english_query", query)

        # If translation failed, return original query
        if not translated or translated == query:
            logger.warning(f"Translation may have failed for: {query}")

        return translated


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
        q_quran = "God's mercy"  # Intentionally English to test translation back to TR
        print(f"EN Input: {q_quran}")
        print(f"Expanded: {enhancer.expand_query(q_quran, corpus='quran')}")

    except Exception as e:
        print(f"Test failed: {e}")
