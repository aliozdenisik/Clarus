"""
Answer Generator Module

Generates LLM-powered answers with cited sources from search results.
Uses OpenRouter API (Gemini 2.5 Flash Lite) for answer generation.

Usage:
    from src.answer_generator import AnswerGenerator

    generator = AnswerGenerator()
    answer = generator.generate_answer(query, search_results, source="quran_tr")
    print(answer.text)  # Cevap metni [Bakara 45]...
    print(answer.citations)  # ['Bakara 45', 'Bakara 153']
"""

import os
import json
import logging
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.circuit_breaker import llm_with_breaker, CircuitBreakerError

logger = logging.getLogger(__name__)


@dataclass
class AnswerResult:
    """Structured answer result with citations"""

    text: str  # Full answer text with inline citations
    citations: List[str]  # List of cited references
    confidence: float  # 0.0 - 1.0 confidence score
    source: str  # quran_tr, bible_kjva, etc.
    query: str  # Original query
    context_used: int  # Number of verses used as context


class AnswerGenerator:
    """
    LLM-powered answer generation with cited sources.

    Takes search results from UltimateRAG and generates a comprehensive
    answer that references specific verses using [Reference] format.

    Features:
    - Citation-aware prompting for faithful answers
    - Separate prompts for Quran (Turkish) and Bible (English source)
    - Structured JSON output for reliable parsing
    - Confidence scoring
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "google/gemini-3-flash-preview"

    # --- QURAN PROMPT (Turkish in, Turkish out) ---
    SYSTEM_PROMPT_QURAN = """Sen uzman bir İslam Alimi ve Kuran tefsircisisin.
Görevin: Kullanıcının sorusunu, sana verilen Kuran ayetlerine dayanarak cevaplamak.

KRİTİK KURALLAR:
1. SADECE sana verilen ayetlerdeki bilgileri kullan - asla uydurma!
2. Her iddiayı mutlaka [Sure:Ayet] formatında kaynak göster. Örnek: [Bakara:45], [Fatiha:1-3]
3. Cevabın TAMAMI Türkçe olmalı
4. Verilen ayetler yeterli değilse, bunu açıkça belirt
5. Tefsir/yorum yaparken kaynağa bağlı kal

ÇIKTI FORMATI (JSON):
{
    "answer": "Cevap metni [Sure:Ayet] şeklinde kaynaklarla...",
    "cited_references": ["Bakara:45", "Nisa:11"],
    "confidence": 0.85
}"""

    FEW_SHOT_QURAN = [
        {
            "role": "user",
            "content": """SORU: Sabır neden önemlidir?

AYETLER:
[1] Bakara:45 - Sabır ve namazla yardım dileyin. Şüphesiz bu, kalbi Allah'a saygıyla dopdolu olanlardan başkasına ağır gelir.
[2] Bakara:153 - Ey iman edenler! Sabır ve namazla yardım dileyin. Şüphesiz Allah sabredenlerle beraberdir.""",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "answer": "Kuran'a göre sabır, müminin en önemli erdemlerinden biridir. Allah, müminlere zorluklar karşısında sabır ve namazla yardım dilemelerini emretmektedir [Bakara:45]. Sabrın önemi, Allah'ın sabredenlerle beraber olduğu müjdesiyle vurgulanır [Bakara:153]. Bu, sabrın sadece bir erdem değil, aynı zamanda Allah'ın yardımına ulaşmanın bir yolu olduğunu gösterir.",
                    "cited_references": ["Bakara:45", "Bakara:153"],
                    "confidence": 0.95,
                },
                ensure_ascii=False,
            ),
        },
    ]

    # --- BIBLE PROMPT (English source, Turkish answer) ---
    SYSTEM_PROMPT_BIBLE = """You are an expert Biblical Scholar and Theologian.
Your task: Answer the user's question based ONLY on the provided Bible verses.

CRITICAL RULES:
1. Use ONLY information from the provided verses - never make things up!
2. Cite every claim with [Book Chapter:Verse] format. Example: [John 3:16], [Romans 5:8]
3. Answer in TURKISH but keep verse references in English format
4. If the verses are insufficient, clearly state this
5. Be faithful to the source text

OUTPUT FORMAT (JSON):
{
    "answer": "Cevap Türkçe olarak [John 3:16] şeklinde kaynaklarla...",
    "cited_references": ["John 3:16", "Romans 5:8"],
    "confidence": 0.85
}"""

    FEW_SHOT_BIBLE = [
        {
            "role": "user",
            "content": """QUESTION: What does the Bible say about God's love?

VERSES:
[1] John 3:16 - For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.
[2] Romans 5:8 - But God commendeth his love toward us, in that, while we were yet sinners, Christ died for us.""",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "answer": "İncil'e göre Tanrı'nın sevgisi benzersiz ve koşulsuzdur. Tanrı dünyayı o kadar çok sevdi ki, biricik Oğlu'nu verdi - bu, O'na iman edenlerin mahvolmaması, sonsuz yaşama kavuşması içindir [John 3:16]. Daha da dikkat çekici olan, Tanrı'nın bu sevgiyi biz henüz günahkârken göstermesidir; Mesih bizim için öldü [Romans 5:8]. Bu, ilahi sevginin insan liyakatine değil, Tanrı'nın merhametine dayandığını gösterir.",
                    "cited_references": ["John 3:16", "Romans 5:8"],
                    "confidence": 0.95,
                },
                ensure_ascii=False,
            ),
        },
    ]

    def __init__(self, model: str = None, api_key: str = None):
        """Initialize Answer Generator with OpenRouter API"""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable."
            )
        self.model = model or self.MODEL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }

    def _extract_reference(self, result, source: str) -> str:
        """Extract reference string from search result based on source"""
        # Try to get from object attributes first
        if "quran" in source:
            surah = getattr(result, "surah_id", None)
            verse = getattr(result, "verse_id", None) or getattr(
                result, "verse_ids", None
            )

            # Fallback to payload
            if surah is None and hasattr(result, "payload"):
                payload = result.payload or {}
                surah = payload.get("surah_id")
                verse = payload.get("verse_id") or payload.get("verse_ids")

            if surah and verse:
                # Get surah name if available
                surah_name = getattr(result, "surah_name", None)
                if surah_name is None and hasattr(result, "payload"):
                    surah_name = result.payload.get("surah_name")

                if surah_name:
                    return f"{surah_name}:{verse}"
                return f"Sure {surah}:{verse}"
        else:
            # Bible format
            book = getattr(result, "book_name", None)
            chapter = getattr(result, "chapter_number", None) or getattr(
                result, "chapter", None
            )
            verse = getattr(result, "verse_number", None) or getattr(
                result, "verse", None
            )

            # Fallback to payload
            if book is None and hasattr(result, "payload"):
                payload = result.payload or {}
                book = payload.get("book_name", "Unknown")
                chapter = payload.get("chapter_number") or payload.get("chapter")
                verse = payload.get("verse_number") or payload.get("verse")

            if book and chapter and verse:
                return f"{book} {chapter}:{verse}"

        # Last resort - check for reference attribute
        ref = getattr(result, "reference", None)
        if ref:
            return ref
        if hasattr(result, "payload") and "reference" in result.payload:
            return result.payload["reference"]

        return "Unknown"

    def _extract_text(self, result, source: str) -> str:
        """Extract verse text from search result"""
        # Try common attribute names
        for attr in ["translation", "text", "content", "verse_text"]:
            text = getattr(result, attr, None)
            if text:
                return text

        # Fallback to payload
        if hasattr(result, "payload"):
            payload = result.payload or {}
            for key in ["translation", "text", "content", "verse_text"]:
                if key in payload:
                    return payload[key]

        return ""

    def _format_context(self, results: List, source: str, max_results: int = 15) -> str:
        """Format search results as numbered, cited context for LLM"""
        context_parts = []

        for i, result in enumerate(results[:max_results], 1):
            ref = self._extract_reference(result, source)
            text = self._extract_text(result, source)

            if text:
                context_parts.append(f"[{i}] {ref} - {text}")

        return "\n".join(context_parts)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.exceptions.Timeout, requests.exceptions.ConnectionError)
        ),
        before_sleep=lambda rs: logger.info(
            f"Retrying LLM call, attempt {rs.attempt_number}/3"
        ),
    )
    def _call_llm(self, query: str, context: str, source: str) -> dict:
        """Call OpenRouter API for answer generation"""
        # Select appropriate prompt based on source
        if "quran" in source:
            system_prompt = self.SYSTEM_PROMPT_QURAN
            examples = self.FEW_SHOT_QURAN
            user_content = f"SORU: {query}\n\nAYETLER:\n{context}"
        else:
            system_prompt = self.SYSTEM_PROMPT_BIBLE
            examples = self.FEW_SHOT_BIBLE
            user_content = f"QUESTION: {query}\n\nVERSES:\n{context}"

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(examples)
        messages.append({"role": "user", "content": user_content})

        try:
            response = llm_with_breaker(
                lambda: requests.post(
                    self.OPENROUTER_URL,
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "response_format": {"type": "json_object"},
                        "max_tokens": 1500,
                        "temperature": 0.3,
                    },
                    timeout=60,
                )
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return json.loads(content)
        except CircuitBreakerError:
            # Circuit breaker open - fail fast, do NOT retry
            logger.warning("Circuit breaker OPEN for LLM - answer generation failed")
            return {
                "answer": "Cevap üretilemedi (servis geçici olarak kullanılamıyor).",
                "cited_references": [],
                "confidence": 0.0,
            }
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            # Let these propagate to @retry decorator
            raise
        except requests.exceptions.RequestException as e:
            # Other HTTP errors - don't retry
            logger.error(f"API request failed: {e}")
            return {
                "answer": "Cevap üretilemedi.",
                "cited_references": [],
                "confidence": 0.0,
            }
        except (json.JSONDecodeError, KeyError) as e:
            # Parse errors - don't retry
            logger.error(f"Response parsing failed: {e}")
            return {
                "answer": "Cevap üretilemedi.",
                "cited_references": [],
                "confidence": 0.0,
            }
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {
                "answer": "Cevap üretilemedi.",
                "cited_references": [],
                "confidence": 0.0,
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Response parsing failed: {e}")
            return {
                "answer": "Cevap üretilemedi.",
                "cited_references": [],
                "confidence": 0.0,
            }

    def generate_answer(
        self,
        query: str,
        search_results: List,
        source: str = "quran_tr",
        max_context_results: int = 15,
    ) -> AnswerResult:
        """
        Generate a cited answer from search results.

        Args:
            query: User's original question
            search_results: List of search results from UltimateRAG
            source: Data source - "quran_tr", "bible_kjva", etc.
            max_context_results: Maximum number of results to include as context

        Returns:
            AnswerResult with text, citations, and confidence
        """
        if not search_results:
            return AnswerResult(
                text="Verilen kaynaklarda bu soruyla ilgili bilgi bulunamadı.",
                citations=[],
                confidence=0.0,
                source=source,
                query=query,
                context_used=0,
            )

        # Format context from search results
        context = self._format_context(search_results, source, max_context_results)

        # Call LLM for answer generation
        llm_result = self._call_llm(query, context, source)

        return AnswerResult(
            text=llm_result.get("answer", "Cevap üretilemedi."),
            citations=llm_result.get("cited_references", []),
            confidence=llm_result.get("confidence", 0.0),
            source=source,
            query=query,
            context_used=min(len(search_results), max_context_results),
        )


if __name__ == "__main__":
    # Quick test
    from dotenv import load_dotenv

    load_dotenv()

    generator = AnswerGenerator()
    print(f"AnswerGenerator initialized with model: {generator.model}")
    print("Ready for answer generation!")
