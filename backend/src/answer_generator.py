"""
Answer Generator Module

Generates LLM-powered answers with cited sources from search results.
Uses OpenRouter API (Gemini 2.5 Flash Lite) for answer generation.

Usage:
    from src.answer_generator import AnswerGenerator

    generator = AnswerGenerator()
    answer = generator.generate_answer(query, search_results, source="quran_tr_diyanet")
    print(answer.text)  # Cevap metni [Bakara 45]...
    print(answer.citations)  # ['Bakara 45', 'Bakara 153']
"""

import json
import os
import time
from dataclasses import dataclass

import requests
import sentry_sdk
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.logging_config import get_logger, log_performance
from src.circuit_breaker import CircuitBreakerError, llm_with_breaker
from src.confidence_scorer import ConfidenceScorer

logger = get_logger(__name__)


@dataclass
class AnswerResult:
    """Structured answer result with citations"""

    text: str  # Full answer text with inline citations
    citations: list[str]  # List of cited references
    confidence: float  # 0.0 - 1.0 confidence score
    source: str  # quran_tr, bible_kjva, etc.
    query: str  # Original query
    context_used: int  # Number of verses used as context
    confidence_breakdown: dict | None = None  # Detailed confidence signals


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

Not: "confidence" alanı sistem tarafından hesaplanacaktır. 0.0 olarak bırakın.

ÇIKTI FORMATI (JSON):
{
    "answer": "Cevap metni [Sure:Ayet] şeklinde kaynaklarla...",
    "cited_references": ["Bakara:45", "Nisa:11"],
    "confidence": 0.0
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
                    "confidence": 0.0,
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

Note: The "confidence" field will be computed by the system. Leave it as 0.0.

OUTPUT FORMAT (JSON):
{
    "answer": "Cevap Türkçe olarak [John 3:16] şeklinde kaynaklarla...",
    "cited_references": ["John 3:16", "Romans 5:8"],
    "confidence": 0.0
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
                    "confidence": 0.0,
                },
                ensure_ascii=False,
            ),
        },
    ]

    def __init__(self, model: str | None = None, api_key: str | None = None):
        """Initialize Answer Generator with OpenRouter API"""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY environment variable.")
        self.model = model or self.MODEL
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }
        self.confidence_scorer = ConfidenceScorer()

    def _extract_reference(self, result, source: str) -> str:
        """Extract reference string from search result based on source"""
        # Try to get from object attributes first
        if "quran" in source:
            surah = getattr(result, "surah_id", None)
            verse = getattr(result, "verse_id", None) or getattr(result, "verse_ids", None)

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
            chapter = getattr(result, "chapter_number", None) or getattr(result, "chapter", None)
            verse = getattr(result, "verse_number", None) or getattr(result, "verse", None)

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

    def _format_context(self, results: list, source: str, max_results: int = 15) -> str:
        """Format search results as numbered, cited context for LLM"""
        context_parts = []

        for i, result in enumerate(results[:max_results], 1):
            ref = self._extract_reference(result, source)
            text = self._extract_text(result, source)

            if text:
                context_parts.append(f"[{i}] {ref} - {text}")

        return "\n".join(context_parts)

    @staticmethod
    def _is_retryable_error(exception):
        """Check if exception is retryable (timeout, connection, or rate limit)"""
        if isinstance(
            exception,
            requests.exceptions.Timeout | requests.exceptions.ConnectionError,
        ):
            return True
        if isinstance(exception, requests.exceptions.HTTPError):
            return exception.response is not None and exception.response.status_code == 429
        return False

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=lambda rs: logger.info(
            "Retrying LLM call", extra={"attempt": rs.attempt_number, "max_attempts": 5}
        ),
    )
    def _call_llm(self, query: str, context: str, source: str) -> dict:
        """Call OpenRouter API for answer generation"""
        with sentry_sdk.start_span(op="llm.openrouter.answer", description="Answer generation LLM call") as span:
            start_time = time.perf_counter()
            span.set_data("model", self.model)
            span.set_data("source", source)

            logger.info(
                "LLM call started",
                extra={
                    "operation": "answer_generation",
                    "model": self.model,
                    "source": source,
                },
            )

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
                result = json.loads(content)

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

                latency_ms = (time.perf_counter() - start_time) * 1000
                span.set_data("latency_ms", latency_ms)
                log_performance(
                    logger,
                    "llm_answer_generation",
                    latency_ms,
                    model=self.model,
                    source=source,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
                return result
            except CircuitBreakerError:
                # Circuit breaker open - fail fast, do NOT retry
                logger.warning(
                    "Circuit breaker OPEN for LLM - answer generation failed",
                    extra={"model": self.model, "source": source},
                )
                span.set_data("latency_ms", (time.perf_counter() - start_time) * 1000)
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
                logger.error("API request failed", extra={"error": str(e), "model": self.model})
                span.set_data("latency_ms", (time.perf_counter() - start_time) * 1000)
                return {
                    "answer": "Cevap üretilemedi.",
                    "cited_references": [],
                    "confidence": 0.0,
                }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Parse errors - don't retry
                logger.error(
                    "Response parsing failed",
                    extra={"error": str(e), "model": self.model},
                )
                span.set_data("latency_ms", (time.perf_counter() - start_time) * 1000)
                return {
                    "answer": "Cevap üretilemedi.",
                    "cited_references": [],
                    "confidence": 0.0,
                }

    def generate_answer(
        self,
        query: str,
        search_results: list,
        source: str = "quran_tr_diyanet",
        max_context_results: int = 15,
        score_stats: dict[str, float] | None = None,
    ) -> AnswerResult:
        """
        Generate a cited answer from search results.

        Args:
            query: User's original question
            search_results: List of search results from UltimateRAG
            source: Data source - "quran_tr_diyanet", "bible_ot", etc.
            max_context_results: Maximum number of results to include as context

        Returns:
            AnswerResult with text, citations, and confidence
        """
        logger.info(
            "Answer generation started",
            extra={
                "source": source,
                "context_count": len(search_results),
                "query": query[:50],
            },
        )

        if not search_results:
            logger.warning("No search results for answer generation", extra={"source": source})
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

        citations = llm_result.get("cited_references", [])
        logger.info(
            "Citation extraction completed",
            extra={
                "source": source,
                "citation_count": len(citations),
                "citations": citations[:5],
            },
        )

        # Compute objective confidence (two-phase sigmoid-calibrated)
        rrf_scores = [r.score for r in search_results]
        rrf_scores.sort(reverse=True)
        num_queries = int(score_stats.get("num_queries", 1)) if score_stats else 1

        answer_text = llm_result.get("answer", "")
        breakdown = self.confidence_scorer.compute(
            scores=rrf_scores,
            num_queries=num_queries,
            cited_count=len(citations),
            num_paragraphs=self.confidence_scorer.count_paragraphs(answer_text),
            total_results=len(search_results),
            expected_results=10,  # final_top_k default
            collections_with_results=1,  # single source
            total_collections=1,  # single source
            answer_length_words=self.confidence_scorer.count_words(answer_text),
            query_type="ask",
        )

        return AnswerResult(
            text=llm_result.get("answer", "Cevap üretilemedi."),
            citations=citations,
            confidence=breakdown.final_score,
            source=source,
            query=query,
            context_used=min(len(search_results), max_context_results),
            confidence_breakdown=breakdown.to_dict(),
        )


if __name__ == "__main__":
    # Quick test
    from dotenv import load_dotenv

    load_dotenv()

    generator = AnswerGenerator()
    print(f"AnswerGenerator initialized with model: {generator.model}")
    print("Ready for answer generation!")
