"""
Query Translation Module

Detects query language and translates between languages for cross-lingual
sacred text search. Uses a single LLM call to detect + translate via
OpenRouter (google/gemini-2.5-flash-lite).

Heuristic pre-filters skip the LLM entirely when language is obvious:
- Turkish characters + quran corpus → already Turkish, no translation needed
- Pure ASCII + bible corpus → already English, no translation needed

Also provides response translation for translating generated essays back
to the user's detected language while preserving citations and markdown.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, Set

import requests
import sentry_sdk
from pybreaker import CircuitBreakerError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.circuit_breaker import llm_with_breaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRANSLATION_MODEL = "google/gemini-2.5-flash-lite"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

TURKISH_CHARS: str = "ğüşıöçĞÜŞİÖÇ"

SUPPORTED_LANGUAGES: Set[str] = {"en", "tr", "es", "fr", "it", "pt", "ar", "de"}

CORPUS_LANGUAGES: dict[str, str] = {
    "quran": "tr",
    "quran_tr": "tr",  # Deprecated - keep for backward compatibility
    "quran_tr_diyanet": "tr",
    "quran_tr_yazir": "tr",
    "quran_tr_ates": "tr",
    "quran_tr_bulac": "tr",
    "quran_tr_ozturk": "tr",
    "quran_tr_vakfi": "tr",
    "quran_tr_yildirim": "tr",
    "quran_tr_yuksel": "tr",
    "bible": "en",
    "bible_ot": "en",
    "bible_nt": "en",
    "bible_apocrypha": "en",
    "bible_tr_ot": "tr",
    "bible_tr_nt": "tr",
}

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

QUERY_DETECT_AND_TRANSLATE_PROMPT = """You are a theological translation expert specializing in sacred text terminology across Islam and Christianity.

TASK: Detect the language of the user's search query, then translate it to {target_lang} for searching {corpus_context}.

STEP 1 — DETECT: Identify the ISO 639-1 language code of the input query.
Supported languages: en (English), tr (Turkish), es (Spanish), fr (French), it (Italian), pt (Portuguese), ar (Arabic), de (German).
If the query contains multiple languages, detect the DOMINANT language.

STEP 2 — TRANSLATE (or return unchanged):
- If the detected language is ALREADY {target_lang}, return the query UNCHANGED with "was_translated": false.
- If the detected language is DIFFERENT from {target_lang}, translate the query with these rules:
  1. PRESERVE proper nouns exactly as-is: Allah, Musa, Isa, Ibrahim, Quran, Bible, Torah, Gospel, Injil, Zebur
  2. PRESERVE book/surah names: Genesis, Exodus, Bakara, Al-Imran, Matta, Yuhanna
  3. PRESERVE citation references: [Bakara:153], [Genesis 1:1] — do NOT translate text inside brackets
  4. Use FORMAL theological register (not colloquial). Examples:
     - "sabır" → "patience" (not "waiting" or "endurance")
     - "şefaat" → "intercession" (not "recommendation")
     - "tövbe" → "repentance" (not "sorry" or "apology")
     - "rahmet" → "mercy/grace" (not "pity")
  5. Translate the MEANING, not word-by-word. Preserve the search intent.

OUTPUT: Return a JSON object with exactly these fields:
{{
  "detected_language": "<ISO 639-1 code>",
  "translated_query": "<translated text OR original text if unchanged>",
  "was_translated": <true if translated, false if returned unchanged>
}}

EXAMPLES:
Input: "¿Qué dice el Corán sobre la paciencia?" (target: tr)
Output: {{"detected_language": "es", "translated_query": "Kuran'da sabır hakkında ne söyleniyor?", "was_translated": true}}

Input: "sabır ve namaz" (target: tr)
Output: {{"detected_language": "tr", "translated_query": "sabır ve namaz", "was_translated": false}}

Input: "What is love according to the Bible?" (target: en)
Output: {{"detected_language": "en", "translated_query": "What is love according to the Bible?", "was_translated": false}}

Input: "Geduld im Islam" (target: tr)
Output: {{"detected_language": "de", "translated_query": "İslam'da sabır", "was_translated": true}}"""

RESPONSE_TRANSLATION_SYSTEM_PROMPT = """You are a theological essay translator specializing in comparative religious analysis.

TASK: Translate the following essay from its current language to {target_lang} while preserving all structural and reference elements.

CRITICAL PRESERVATION RULES (DO NOT TRANSLATE):
1. Text within square brackets: [Bakara:153], [Genesis 1:1], [Matthew 5:3-5]
2. Book/surah names: Genesis, Exodus, Leviticus, Bakara, Al-Imran, Matta, Yuhanna, etc.
3. Source labels: Quran, Bible, Old Testament, New Testament, Apocrypha
4. Section headers in Turkish: ## Eski Ahit, ## Yeni Ahit, ## Apokrifa, ## Kuran-ı Kerim, ## Karşılaştırmalı Değerlendirme
   → Keep these headers as-is (they are proper names of the analysis sections)
5. ALL markdown formatting: ## headers, **bold**, *italic*, - bullet points, 1. numbered lists
6. Horizontal rules: ---

TRANSLATION RULES:
1. Maintain FORMAL academic register throughout (scholarly theological essay style)
2. Preserve theological nuance in translation
3. Keep paragraph structure intact (same number of paragraphs)
4. Translate the CONTENT of each paragraph, not the structural elements

OUTPUT: Return ONLY the translated essay text. No JSON, no explanation, no wrapping.

EXAMPLE:
Input (Turkish → Spanish):
## Kuran-ı Kerim

Sabır kavramı Kuran'da merkezi bir öneme sahiptir. [Bakara:153] ayetinde Allah, müminlere sabır ve namazla yardım dilemelerini emreder.

Output:
## Kuran-ı Kerim

El concepto de paciencia tiene una importancia central en el Corán. En el versículo [Bakara:153], Allah ordena a los creyentes buscar ayuda a través de la paciencia y la oración."""


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class TranslationError(Exception):
    """Raised when query or response translation fails irrecoverably."""

    def __init__(
        self,
        message: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        original_text: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.original_text = original_text


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class TranslationResult:
    """Result of a language detection / translation operation.

    Attributes:
        detected_language: ISO 639-1 code of the detected source language.
        translated_query: The (possibly translated) query text.
        was_translated: ``True`` if the query was actually translated by the LLM.
    """

    detected_language: str
    translated_query: str
    was_translated: bool


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class QueryTranslator:
    """Detects query language and translates for cross-lingual sacred text search.

    Uses a single LLM call (google/gemini-2.5-flash-lite via OpenRouter) to
    detect the source language **and** translate in one request.  Heuristic
    pre-filters bypass the LLM when the answer is obvious (Turkish chars for
    Quran corpus, pure ASCII for Bible corpus).

    Args:
        api_key: OpenRouter API key.  Falls back to ``OPENROUTER_API_KEY`` env var.

    Raises:
        ValueError: If no API key is available.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key: str = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment "
                "variable or pass api_key parameter."
            )
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def translate_query(
        self,
        query: str,
        corpus: Optional[str] = None,
    ) -> TranslationResult:
        """Detect the language of *query* and optionally translate it.

        When *corpus* is provided the query is translated into the corpus's
        native language (Turkish for Quran, English for Bible).  When *corpus*
        is ``None`` only language detection is performed — the query text is
        returned unchanged.

        Args:
            query: The user's search query.
            corpus: Target corpus name (e.g. ``"quran_tr"``, ``"bible_ot"``).
                    ``None`` means detect-only mode.

        Returns:
            A :class:`TranslationResult` with detection and translation info.

        Raises:
            ValueError: If *query* is empty or *corpus* is not recognised.
            TranslationError: On irrecoverable LLM / network failures.
        """
        # --- Validation ---------------------------------------------------
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")
        query = query.strip()

        if corpus is not None and corpus not in CORPUS_LANGUAGES:
            raise ValueError(
                f"Invalid corpus '{corpus}'. "
                f"Supported: {sorted(CORPUS_LANGUAGES.keys())}"
            )

        target_lang: Optional[str] = (
            CORPUS_LANGUAGES[corpus] if corpus is not None else None
        )

        # --- Heuristic pre-filters (skip LLM) ----------------------------
        if corpus is not None:
            heuristic = self._heuristic_detect(query, corpus)
            if heuristic is not None:
                return heuristic

        # --- LLM detection (+translation) ---------------------------------
        return self._llm_detect_and_translate(query, target_lang, corpus)

    def translate_response(
        self,
        text: str,
        target_lang: str,
        preserve_citations: bool = True,
    ) -> str:
        """Translate a generated essay/response into *target_lang*.

        Uses a plain-text LLM call (no JSON mode) so the output is the
        translated essay directly.  Citations, markdown, and section headers
        are preserved via the system prompt.

        Args:
            text: The essay text to translate.
            target_lang: ISO 639-1 target language code.
            preserve_citations: Hint included in the system prompt (default ``True``).

        Returns:
            The translated essay as a plain string.

        Raises:
            TranslationError: On irrecoverable LLM / network failures.
        """
        if not text or not text.strip():
            return text

        system_prompt = RESPONSE_TRANSLATION_SYSTEM_PROMPT.format(
            target_lang=target_lang,
        )

        # Extra reminder when citations must be preserved
        if preserve_citations:
            system_prompt += (
                "\n\nREMINDER: Preserve ALL citation references in square "
                "brackets exactly as they appear."
            )

        return self._call_llm_text(
            prompt=text,
            system_prompt=system_prompt,
            max_tokens=4000,
        )

    # ------------------------------------------------------------------
    # Heuristic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _heuristic_detect(
        query: str,
        corpus: str,
    ) -> Optional[TranslationResult]:
        """Return a ``TranslationResult`` without calling the LLM when the
        language is obvious, or ``None`` if the LLM is needed.
        """
        target_lang = CORPUS_LANGUAGES[corpus]

        # Turkish chars + quran corpus → already Turkish
        if target_lang == "tr" and any(ch in query for ch in TURKISH_CHARS):
            logger.debug(
                "Heuristic: Turkish characters detected for Quran corpus — skipping LLM."
            )
            return TranslationResult(
                detected_language="tr",
                translated_query=query,
                was_translated=False,
            )

        # Pure ASCII + bible corpus → already English
        if target_lang == "en" and query.isascii():
            logger.debug(
                "Heuristic: Pure ASCII detected for Bible corpus — skipping LLM."
            )
            return TranslationResult(
                detected_language="en",
                translated_query=query,
                was_translated=False,
            )

        return None

    # ------------------------------------------------------------------
    # LLM call helpers
    # ------------------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=lambda rs: logger.info(
            "Retrying translation LLM call, attempt %d/3", rs.attempt_number
        ),
    )
    def _call_llm_json(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int = 300,
    ) -> dict:
        """Call OpenRouter with JSON response format.

        Args:
            prompt: User message content.
            system_prompt: System message content.
            max_tokens: Maximum tokens in the response.

        Returns:
            Parsed JSON dict from the LLM response.

        Raises:
            TranslationError: On empty response or circuit breaker open.
            requests.exceptions.RequestException: On transient HTTP errors
                (handled by tenacity retry).
        """
        with sentry_sdk.start_span(
            op="llm.openrouter.query_translator",
            description="Query translation LLM call",
        ) as span:
            start_time = time.time()
            span.set_data("model", TRANSLATION_MODEL)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            try:
                response = llm_with_breaker(
                    lambda: requests.post(
                        OPENROUTER_URL,
                        headers=self._headers,
                        json={
                            "model": TRANSLATION_MODEL,
                            "messages": messages,
                            "response_format": {"type": "json_object"},
                            "max_tokens": max_tokens,
                            "temperature": 0.3,
                        },
                        timeout=30,
                    )
                )
                response.raise_for_status()
                response_json = response.json()

                if "choices" not in response_json or not response_json["choices"]:
                    raise TranslationError(
                        "Invalid LLM response: missing 'choices'.",
                        original_text=prompt,
                    )

                content: str = (
                    response_json["choices"][0].get("message", {}).get("content", "")
                )
                if not content:
                    raise TranslationError(
                        "Empty content in LLM response.",
                        original_text=prompt,
                    )

                elapsed = time.time() - start_time
                span.set_data("duration_s", round(elapsed, 2))
                logger.debug("Translation LLM call completed in %.2fs", elapsed)

                return json.loads(content)

            except CircuitBreakerError:
                raise TranslationError(
                    "Circuit breaker OPEN for translation LLM.",
                    original_text=prompt,
                )
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Failed to parse LLM JSON response: %s",
                    exc,
                )
                raise  # will be caught by caller for fallback

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=lambda rs: logger.info(
            "Retrying response translation LLM call, attempt %d/3",
            rs.attempt_number,
        ),
    )
    def _call_llm_text(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int = 4000,
    ) -> str:
        """Call OpenRouter and return plain text (no JSON mode).

        Args:
            prompt: User message content (the essay to translate).
            system_prompt: System message content.
            max_tokens: Maximum tokens in the response.

        Returns:
            Plain text string from the LLM.

        Raises:
            TranslationError: On empty response or circuit breaker open.
        """
        with sentry_sdk.start_span(
            op="llm.openrouter.response_translator",
            description="Response translation LLM call",
        ) as span:
            start_time = time.time()
            span.set_data("model", TRANSLATION_MODEL)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            try:
                response = llm_with_breaker(
                    lambda: requests.post(
                        OPENROUTER_URL,
                        headers=self._headers,
                        json={
                            "model": TRANSLATION_MODEL,
                            "messages": messages,
                            "max_tokens": max_tokens,
                            "temperature": 0.3,
                        },
                        timeout=60,
                    )
                )
                response.raise_for_status()
                response_json = response.json()

                if "choices" not in response_json or not response_json["choices"]:
                    raise TranslationError(
                        "Invalid LLM response: missing 'choices'.",
                        original_text=prompt[:200],
                    )

                content: str = (
                    response_json["choices"][0].get("message", {}).get("content", "")
                )
                if not content:
                    raise TranslationError(
                        "Empty content in response translation.",
                        original_text=prompt[:200],
                    )

                elapsed = time.time() - start_time
                span.set_data("duration_s", round(elapsed, 2))
                logger.debug("Response translation completed in %.2fs", elapsed)

                return content.strip()

            except CircuitBreakerError:
                raise TranslationError(
                    "Circuit breaker OPEN for response translation.",
                    original_text=prompt[:200],
                )

    # ------------------------------------------------------------------
    # Core translation logic
    # ------------------------------------------------------------------

    def _llm_detect_and_translate(
        self,
        query: str,
        target_lang: Optional[str],
        corpus: Optional[str],
    ) -> TranslationResult:
        """Use the LLM to detect language and optionally translate.

        If *target_lang* is ``None`` (detect-only mode), the prompt still asks
        for detection but instructs the LLM to return the query unchanged.

        On JSON parse failure the method falls back to assuming the corpus
        language and returning the original query.
        """
        if target_lang is not None:
            corpus_context = f"the {corpus} corpus"
            effective_target = target_lang
        else:
            # Detect-only: ask LLM to detect but not translate
            corpus_context = "language detection only (no translation needed)"
            effective_target = "the original language"

        system_prompt = QUERY_DETECT_AND_TRANSLATE_PROMPT.format(
            target_lang=effective_target,
            corpus_context=corpus_context,
        )

        try:
            result = self._call_llm_json(
                prompt=query,
                system_prompt=system_prompt,
                max_tokens=300,
            )

            detected = result.get("detected_language", "")
            translated = result.get("translated_query", query)
            was_translated = bool(result.get("was_translated", False))

            # Sanity: if detected language is empty, fall back
            if not detected:
                logger.warning("LLM returned empty detected_language — falling back.")
                return self._fallback_result(query, target_lang)

            return TranslationResult(
                detected_language=detected,
                translated_query=translated or query,
                was_translated=was_translated,
            )

        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning(
                "Failed to parse translation LLM response (%s) — "
                "falling back to corpus language.",
                exc,
            )
            return self._fallback_result(query, target_lang)

        except TranslationError:
            # Already a TranslationError — re-raise as-is
            raise

        except Exception as exc:
            logger.error("Unexpected error during translation: %s", exc, exc_info=True)
            raise TranslationError(
                f"Translation failed: {exc}",
                original_text=query,
                target_lang=target_lang,
            ) from exc

    @staticmethod
    def _fallback_result(
        query: str,
        target_lang: Optional[str],
    ) -> TranslationResult:
        """Return a safe fallback when LLM parsing fails.

        Assumes the query is already in the target language and returns it
        unchanged.
        """
        fallback_lang = target_lang if target_lang else "en"
        logger.info(
            "Fallback: assuming query is '%s', returning unchanged.", fallback_lang
        )
        return TranslationResult(
            detected_language=fallback_lang,
            translated_query=query,
            was_translated=False,
        )
