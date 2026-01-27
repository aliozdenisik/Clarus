"""
Comparative Answer Generator Module

Generates comparative theological essays from multi-scripture search results.
Uses Gemini 2.5 Flash via OpenRouter for answer generation.

Features:
- Multi-scripture context (Quran + Bible)
- Essay-style comparative analysis
- Inline citations: [Bakara:45] for Quran, [John 3:16] for Bible
- Numbered reference list at end
- Priority ordering by relevance score
"""

import os
import re
import json
import logging
import requests
import time
import sentry_sdk
from typing import List, Optional, Dict, Any, Tuple
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
class ComparativeAnswer:
    """Comparative theological analysis result"""

    essay: str  # Full essay with inline citations
    quran_references: List[str]  # Used Quran verse references
    bible_references: List[str]  # Used Bible verse references
    all_references: List[str]  # Numbered list of all refs (in order of use)
    confidence: float  # 0.0 - 1.0 confidence score
    query: str  # Original query
    verses_provided: int  # Total verses given to LLM (80)


class ComparativeAnswerGenerator:
    """
    Generates comparative theological essays from multi-scripture search results.

    Takes 80 verses (20 per search type × 4 searches) sorted by relevance score.
    LLM generates essay with inline citations, prioritizing higher-scored verses.

    Output format:
    - Essay-style response with inline citations
    - [Bakara:45] for Quran, [John 3:16] for Bible
    - Numbered reference list at end
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "google/gemini-2.5-flash"  # Gemini 2.5 Flash normal

    SYSTEM_PROMPT = """You are an expert comparative theologian and scholar of Abrahamic religions.
Your task: Write a comprehensive, comparative theological essay that synthesizes content from both the Quran and the Bible to answer the user's question.

CRITICAL RULES:
1. Use ONLY the provided verses - never make things up!
2. PRIORITIZE verses that appear FIRST in the list (they have higher relevance scores)
3. Include content from BOTH the Quran AND the Bible
4. Cite EVERY claim with the exact reference format:
   - Quran: [Sure:Ayet] or [SurahName:Verse] (e.g., [Bakara:45])
   - Bible: [Book Chapter:Verse] (e.g., [John 3:16])
5. Write the essay in TURKISH
6. Be respectful, balanced, and theologically accurate
7. Present similarities AND differences between scriptures
8. Structure your response as a coherent essay, not bullet points

ESSAY STRUCTURE:
1. Introduction - brief overview of how both scriptures address the topic
2. Main body - comparative analysis with cited verses
3. Synthesis - common themes and unique perspectives
4. Conclusion - summary of key insights

OUTPUT FORMAT (JSON):
{
    "essay": "Karşılaştırmalı essay metni [Sure:Ayet] ve [Book Ch:V] şeklinde kaynaklarla...",
    "quran_citations": ["Bakara:45", "Fatiha:1"],
    "bible_citations": ["John 3:16", "Genesis 1:1"],
    "all_references_ordered": ["Bakara:45", "John 3:16", ...],
    "confidence": 0.85
}"""

    FEW_SHOT = [
        {
            "role": "user",
            "content": """SORU: Sabır hakkında kutsal metinler ne söylüyor?

KURAN AYETLERİ (skorla sıralı, en güvenilir ilk):
[Q1] Bakara:45 - Sabır ve namazla yardım dileyin. (skor: 0.95)
[Q2] Bakara:153 - Şüphesiz Allah sabredenlerle beraberdir. (skor: 0.92)

İNCİL AYETLERİ (skorla sıralı, en güvenilir ilk):
[B1] James 1:3 - The testing of your faith produces patience. (skor: 0.94)
[B2] Romans 5:3 - Tribulation worketh patience. (skor: 0.91)""",
        },
        {
            "role": "assistant",
            "content": json.dumps(
                {
                    "essay": """Sabır kavramı hem Kuran'da hem de İncil'de merkezi bir erdem olarak işlenir. Her iki kutsal metin de sabrın zorluklarla bağlantısını vurgular ve imanlılar için temel bir özellik olarak sunar.

Kuran'da sabır, Allah'a yaklaşmanın bir yolu olarak sunulur. "Sabır ve namazla yardım dileyin" [Bakara:45] ayeti, sabrı ibadetle birleştirerek ruhani bir disiplin olarak konumlandırır. Dahası, "Allah sabredenlerle beraberdir" [Bakara:153] vaadi, sabrın ilahi beraberliğe götüren bir yol olduğunu gösterir.

İncil'de ise sabır, imanın sınanmasıyla elde edilen bir erdem olarak açıklanır. "İmanınızın sınanması sabır üretir" [James 1:3] ifadesi, zorlukların karakteri geliştirdiğini öğretir. Benzer şekilde, "sıkıntı sabır doğurur" [Romans 5:3] ayeti bu anlayışı pekiştirir.

Her iki gelenek de sabrı pasif bir bekleme değil, aktif bir manevi çaba olarak sunar. Kuran sabrı ibadet ve ilahi beraberlikle ilişkilendirirken, İncil onu iman sınaması ve karakter gelişimi çerçevesinde ele alır. Ortak nokta, zorlukların sabrı geliştirmesi ve bunun ilahi onay getirmesidir.""",
                    "quran_citations": ["Bakara:45", "Bakara:153"],
                    "bible_citations": ["James 1:3", "Romans 5:3"],
                    "all_references_ordered": [
                        "Bakara:45",
                        "Bakara:153",
                        "James 1:3",
                        "Romans 5:3",
                    ],
                    "confidence": 0.92,
                },
                ensure_ascii=False,
            ),
        },
    ]

    def __init__(self, model: str = None, api_key: str = None):
        """Initialize Comparative Answer Generator with OpenRouter API"""
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
        print(f"Initialized ComparativeAnswerGenerator with model: {self.model}")

    def _extract_reference(self, result, source: str) -> str:
        """Extract reference string from search result based on source"""
        if "quran" in source:
            surah = getattr(result, "surah_id", None)
            verse = getattr(result, "verse_id", None) or getattr(
                result, "verse_ids", None
            )
            surah_name = getattr(result, "surah_name", None)

            # Fallback to payload
            if surah is None and hasattr(result, "payload"):
                payload = result.payload or {}
                surah = payload.get("surah_id")
                verse = payload.get("verse_id") or payload.get("verse_ids")
                surah_name = payload.get("surah_name")

            if surah_name and verse:
                return f"{surah_name}:{verse}"
            if surah and verse:
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

        return "Unknown"

    def _extract_text(self, result, source: str) -> str:
        """Extract verse text from search result"""
        for attr in ["translation", "text", "content", "combined_translation"]:
            text = getattr(result, attr, None)
            if text:
                return text[:500]  # Limit length

        if hasattr(result, "payload"):
            payload = result.payload or {}
            for key in ["translation", "text", "content"]:
                if key in payload:
                    return str(payload[key])[:500]

        return ""

    def _extract_score(self, result) -> float:
        """Extract relevance score from result"""
        return getattr(result, "score", 0.0)

    def _format_verses_section(
        self, results: List, source: str, label: str, prefix: str
    ) -> str:
        """Format verses with scores for a single source"""
        lines = []
        for i, result in enumerate(results, 1):
            ref = self._extract_reference(result, source)
            text = self._extract_text(result, source)
            score = self._extract_score(result)

            if text:
                lines.append(f"[{prefix}{i}] {ref} - {text} (skor: {score:.2f})")

        return f"\n{label} (skorla sıralı, en güvenilir ilk):\n" + "\n".join(lines)

    def _format_context(
        self,
        quran_semantic: List,
        quran_chunks: List,
        bible_semantic: List,
        bible_chunks: List,
    ) -> str:
        """Format all 80 verses as context for LLM"""
        sections = []

        # Quran Semantic (20)
        if quran_semantic:
            sections.append(
                self._format_verses_section(
                    quran_semantic, "quran_tr", "KURAN - SEMANTİK ARAMA SONUÇLARI", "QS"
                )
            )

        # Quran Chunks (20)
        if quran_chunks:
            sections.append(
                self._format_verses_section(
                    quran_chunks, "quran_tr", "KURAN - SEMANTİK CHUNK SONUÇLARI", "QC"
                )
            )

        # Bible Semantic (20)
        if bible_semantic:
            sections.append(
                self._format_verses_section(
                    bible_semantic,
                    "bible_kjva",
                    "İNCİL - SEMANTİK ARAMA SONUÇLARI",
                    "BS",
                )
            )

        # Bible Chunks (20)
        if bible_chunks:
            sections.append(
                self._format_verses_section(
                    bible_chunks, "bible_kjva", "İNCİL - SEMANTİK CHUNK SONUÇLARI", "BC"
                )
            )

        return "\n".join(sections)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=lambda rs: logger.info(
            f"Retrying LLM call, attempt {rs.attempt_number}/5"
        ),
    )
    def _call_llm(self, query: str, context: str) -> dict:
        """Call OpenRouter API for comparative essay generation"""
        with sentry_sdk.start_span(
            op="llm.openrouter.comparative",
            description="Comparative essay generation LLM call",
        ) as span:
            start_time = time.time()
            span.set_data("model", self.model)

            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
            messages.extend(self.FEW_SHOT)
            messages.append({"role": "user", "content": f"SORU: {query}\n\n{context}"})

            try:
                response = llm_with_breaker(
                    lambda: requests.post(
                        self.OPENROUTER_URL,
                        headers=self._headers,
                        json={
                            "model": self.model,
                            "messages": messages,
                            "response_format": {"type": "json_object"},
                            "max_tokens": 4000,  # Longer for essay
                            "temperature": 0.4,
                        },
                        timeout=120,  # Longer timeout for complex generation
                    )
                )
                response.raise_for_status()
                response_json = response.json()

                # Defensive parsing for LLM response
                if "choices" not in response_json or not response_json["choices"]:
                    logger.error(
                        f"Invalid LLM response: missing 'choices'. Response: {response_json}"
                    )
                    raise ValueError("Invalid LLM response: missing 'choices' field")

                choice = response_json["choices"][0]
                if "message" not in choice or "content" not in choice.get(
                    "message", {}
                ):
                    logger.error(f"Invalid LLM response structure: {choice}")
                    raise ValueError("Invalid LLM response: missing message content")

                content = choice["message"]["content"].strip()
                result = json.loads(content)
                span.set_data("latency_ms", (time.time() - start_time) * 1000)
                return result
            except CircuitBreakerError:
                # Circuit breaker open - fail fast, do NOT retry
                logger.warning(
                    "Circuit breaker OPEN for LLM - comparative essay generation failed"
                )
                span.set_data("latency_ms", (time.time() - start_time) * 1000)
                return {
                    "essay": "Karşılaştırmalı analiz üretilemedi (servis geçici olarak kullanılamıyor).",
                    "quran_citations": [],
                    "bible_citations": [],
                    "all_references_ordered": [],
                    "confidence": 0.0,
                }
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                # Let these propagate to @retry decorator
                raise
            except requests.exceptions.RequestException as e:
                # Other HTTP errors - don't retry
                logger.error(f"API request failed: {e}")
                span.set_data("latency_ms", (time.time() - start_time) * 1000)
                return {
                    "essay": "Karşılaştırmalı analiz üretilemedi.",
                    "quran_citations": [],
                    "bible_citations": [],
                    "all_references_ordered": [],
                    "confidence": 0.0,
                }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Parse errors - don't retry
                logger.error(f"Response parsing failed: {e}")
                span.set_data("latency_ms", (time.time() - start_time) * 1000)
                return {
                    "essay": "Karşılaştırmalı analiz üretilemedi.",
                    "quran_citations": [],
                    "bible_citations": [],
                    "all_references_ordered": [],
                    "confidence": 0.0,
                }

    def generate_comparative_answer(
        self,
        query: str,
        quran_semantic: List,
        quran_chunks: List,
        bible_semantic: List,
        bible_chunks: List,
    ) -> ComparativeAnswer:
        """
        Generate a comparative theological essay from multi-scripture results.

        Args:
            query: User's original question
            quran_semantic: 20 results from Quran semantic search
            quran_chunks: 20 results from Quran chunk search
            bible_semantic: 20 results from Bible semantic search
            bible_chunks: 20 results from Bible chunk search

        Returns:
            ComparativeAnswer with essay, citations, and confidence
        """
        total_verses = (
            len(quran_semantic)
            + len(quran_chunks)
            + len(bible_semantic)
            + len(bible_chunks)
        )

        if total_verses == 0:
            return ComparativeAnswer(
                essay="Verilen kaynaklarda bu soruyla ilgili bilgi bulunamadı.",
                quran_references=[],
                bible_references=[],
                all_references=[],
                confidence=0.0,
                query=query,
                verses_provided=0,
            )

        # Format context from all 80 verses
        context = self._format_context(
            quran_semantic, quran_chunks, bible_semantic, bible_chunks
        )

        # Call LLM for comparative essay generation
        print(f"Generating comparative essay with {total_verses} verses...")
        llm_result = self._call_llm(query, context)

        return ComparativeAnswer(
            essay=llm_result.get("essay", "Analiz üretilemedi."),
            quran_references=llm_result.get("quran_citations", []),
            bible_references=llm_result.get("bible_citations", []),
            all_references=llm_result.get("all_references_ordered", []),
            confidence=llm_result.get("confidence", 0.0),
            query=query,
            verses_provided=total_verses,
        )


if __name__ == "__main__":
    # Quick test
    from dotenv import load_dotenv

    load_dotenv()

    generator = ComparativeAnswerGenerator()
    print("ComparativeAnswerGenerator ready!")
