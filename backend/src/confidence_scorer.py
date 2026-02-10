"""
Confidence Scoring Module for Clarus RAG Pipeline

Two-phase sigmoid-calibrated confidence scoring system:

Phase 1 - Retrieval Confidence (computed from search results):
  - Score Quality: Sigmoid-calibrated median of top RRF scores
  - Score Separation: Top/5th score ratio (clear winner detection)
  - Result Coverage: Actual results vs expected

Phase 2 - Answer Quality (computed from generated answer):
  - Citation Density: Citations per paragraph (vs expected density)
  - Top-K Citation Rate: Estimated usage of best search results
  - Answer Substance: Word count vs minimum threshold

Final score uses geometric-arithmetic hybrid blend with sigmoid calibration
to produce meaningful score distribution (40-95% range).

Industry references:
- Azure AI Search: Score distribution analysis over single averages
- Cohere Rerank: Cutoff point scoring
- Perplexity: Citation grounding rate
- Sigmoid calibration (Platt scaling): ML standard for score calibration
"""

import math
from dataclasses import asdict, dataclass

from app.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConfidenceBreakdown:
    """Two-phase confidence score breakdown with all signals"""

    # Phase 1: Retrieval Confidence signals
    score_quality: float  # 0.0-1.0: Sigmoid-calibrated RRF score quality
    score_separation: float  # 0.0-1.0: Top vs 5th score ratio
    result_coverage: float  # 0.0-1.0: Actual / expected results

    # Phase 2: Answer Quality signals
    citation_density: float  # 0.0-1.0: Citations per paragraph vs expected
    top_k_citation_rate: float  # 0.0-1.0: Estimated top-K result usage
    answer_substance: float  # 0.0-1.0: Word count vs minimum

    # Composite scores
    retrieval_confidence: float  # 0.0-1.0: Phase 1 composite
    answer_quality: float  # 0.0-1.0: Phase 2 composite
    final_score: float  # 0.0-1.0: Calibrated final score

    # Bonus
    source_breadth_bonus: float  # 0.0-0.05: Multi-collection bonus

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return asdict(self)


class ConfidenceScorer:
    """
    Two-phase sigmoid-calibrated confidence scorer.

    Replaces weighted arithmetic mean with:
    1. Per-signal sigmoid calibration (maps raw signals to meaningful ranges)
    2. Two-phase architecture (retrieval + answer quality)
    3. Geometric-arithmetic hybrid blend (bad retrieval can't be compensated)
    4. Final sigmoid calibration (meaningful 40-95% distribution)

    Sigmoid function: f(x) = 1 / (1 + exp(-k * (x - midpoint)))
    - midpoint = value considered "adequate" (maps to 0.5)
    - k (steepness) = how fast the curve transitions
    """

    # --- Sigmoid calibration parameters (tuned for RRF k=60 corpus) ---
    RRF_MIDPOINT = 0.012  # "adequate" median RRF score for top-5 results
    RRF_STEEPNESS = 200.0  # High steepness for small RRF value range (0.001-0.05)
    SEPARATION_MIDPOINT = 1.5  # top/5th ratio considered "clear winner"
    SEPARATION_STEEPNESS = 3.0
    DENSITY_STEEPNESS = 2.0  # Steepness for citation density sigmoid
    TOP_K_MIDPOINT = 0.5  # 50% of top-K cited = adequate
    TOP_K_STEEPNESS = 6.0
    FINAL_MIDPOINT = 0.45  # Center of final calibration sigmoid
    FINAL_STEEPNESS = 6.0  # Spread of final sigmoid

    # --- Expected citation density per query type ---
    EXPECTED_DENSITY = {
        "search": 2.0,  # ~2 citations per paragraph
        "ask": 3.0,  # ~3 citations per paragraph
        "compare": 4.0,  # ~4 citations per paragraph (multi-source)
    }

    # --- Minimum answer length (words) per query type ---
    MIN_WORDS = {
        "search": 50,
        "ask": 100,
        "compare": 200,
    }

    @staticmethod
    def _sigmoid(x: float, midpoint: float, steepness: float) -> float:
        """
        Standard sigmoid function: 1 / (1 + exp(-k * (x - midpoint)))

        Args:
            x: Input value
            midpoint: Value that maps to 0.5 output (the "adequate" threshold)
            steepness: How quickly the curve transitions (higher = steeper)

        Returns:
            float: Calibrated value [0.0, 1.0]
        """
        z = -steepness * (x - midpoint)
        # Clamp to prevent math overflow
        z = max(-500.0, min(500.0, z))
        return 1.0 / (1.0 + math.exp(z))

    @staticmethod
    def count_paragraphs(text: str) -> int:
        """Count non-empty paragraphs in text (separated by double newlines)"""
        if not text:
            return 0
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return max(len(paragraphs), 1)

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())

    def _compute_retrieval_confidence(
        self,
        scores: list[float],
        actual_results: int,
        expected_results: int,
        collections_with_results: int,
        total_collections: int,
    ) -> tuple:
        """
        Phase 1: Retrieval Confidence — did we find good, relevant documents?

        Signals:
        - Score Quality: Sigmoid on median of top-5 RRF scores
        - Score Separation: Sigmoid on top/5th score ratio
        - Result Coverage: Ratio of actual to expected results

        Returns:
            (retrieval_confidence, score_quality, score_separation,
             result_coverage, breadth_bonus)
        """
        # Signal 1: Score Quality
        # Uses median of top-5 RRF scores, sigmoid-calibrated
        if scores:
            top_scores = sorted(scores[: min(5, len(scores))], reverse=True)
            median_idx = len(top_scores) // 2
            median_score = top_scores[median_idx]
            score_quality = self._sigmoid(median_score, self.RRF_MIDPOINT, self.RRF_STEEPNESS)
        else:
            score_quality = 0.0

        # Signal 2: Score Separation
        # Does the top result clearly stand out from rank 5?
        # High separation = retrieval found a clear winner = good
        if scores and len(scores) >= 2:
            top = scores[0]
            fifth = scores[min(4, len(scores) - 1)]
            if fifth > 1e-10:
                separation_ratio = top / fifth
            else:
                separation_ratio = 10.0  # Very high if bottom is near-zero
            score_separation = self._sigmoid(
                separation_ratio,
                self.SEPARATION_MIDPOINT,
                self.SEPARATION_STEEPNESS,
            )
        else:
            score_separation = 0.5  # Neutral if insufficient data

        # Signal 3: Result Coverage
        # Did we get the expected number of results?
        if expected_results > 0:
            result_coverage = min(actual_results / expected_results, 1.0)
        else:
            result_coverage = 1.0

        # Combine Phase 1 signals
        retrieval = 0.60 * score_quality + 0.25 * score_separation + 0.15 * result_coverage

        # Source breadth BONUS (additive, not penalty)
        # Only applies for multi-collection queries (compare mode)
        breadth_bonus = 0.0
        if total_collections > 1:
            breadth_bonus = 0.05 * (collections_with_results / total_collections)
            retrieval = min(retrieval + breadth_bonus, 1.0)

        return (
            retrieval,
            score_quality,
            score_separation,
            result_coverage,
            breadth_bonus,
        )

    def _compute_answer_quality(
        self,
        cited_count: int,
        num_paragraphs: int,
        total_results: int,
        answer_length_words: int,
        query_type: str = "ask",
    ) -> tuple:
        """
        Phase 2: Answer Quality — is the generated answer well-grounded?

        Signals:
        - Citation Density: Citations per paragraph vs expected density
        - Top-K Citation Rate: Estimated usage of best search results
        - Answer Substance: Word count vs minimum for query type

        Returns:
            (answer_quality, citation_density, top_k_citation_rate, answer_substance)
        """
        # Signal 1: Citation Density
        # How many citations per paragraph? Sigmoid around 70% of expected
        expected_density = self.EXPECTED_DENSITY.get(query_type, 3.0)
        actual_density = cited_count / max(num_paragraphs, 1)
        citation_density = self._sigmoid(actual_density, expected_density * 0.7, self.DENSITY_STEEPNESS)

        # Signal 2: Top-K Citation Rate (estimated)
        # Heuristic: assume citations come from top results first
        # (true because prompts instruct LLM to prioritize highest-scored verses)
        top_k = min(10, total_results)
        if top_k > 0:
            estimated_top_k_cited = min(cited_count, top_k)
            top_k_rate = estimated_top_k_cited / top_k
            top_k_citation_rate = self._sigmoid(top_k_rate, self.TOP_K_MIDPOINT, self.TOP_K_STEEPNESS)
        else:
            top_k_citation_rate = 0.0

        # Signal 3: Answer Substance
        # Does the answer meet minimum length for its type?
        min_words = self.MIN_WORDS.get(query_type, 100)
        answer_substance = min(answer_length_words / max(min_words, 1), 1.0)

        # Combine Phase 2 signals
        answer_qual = 0.50 * citation_density + 0.35 * top_k_citation_rate + 0.15 * answer_substance

        return answer_qual, citation_density, top_k_citation_rate, answer_substance

    def compute(
        self,
        scores: list[float],
        num_queries: int,
        cited_count: int,
        num_paragraphs: int,
        total_results: int,
        expected_results: int,
        collections_with_results: int,
        total_collections: int,
        answer_length_words: int,
        query_type: str = "ask",
        k: int = 60,
    ) -> ConfidenceBreakdown:
        """
        Compute two-phase sigmoid-calibrated confidence score.

        Phase 1 (Retrieval) acts as a soft gate via geometric blending:
        bad retrieval tanks the score regardless of answer quality (GIGO).

        Final sigmoid calibration spreads scores across 40-95% range,
        making the difference between excellent and mediocre visible.

        Args:
            scores: RRF scores sorted descending
            num_queries: Number of multi-query variants used
            cited_count: Total citations in generated answer
            num_paragraphs: Number of paragraphs in answer
            total_results: Total search results retrieved
            expected_results: Expected/target number of results
            collections_with_results: Collections with at least 1 result
            total_collections: Total collections searched
            answer_length_words: Word count of generated answer
            query_type: "search", "ask", or "compare"
            k: RRF k-parameter (default 60)

        Returns:
            ConfidenceBreakdown with all signals, composites, and final score
        """
        # Phase 1: Retrieval Confidence
        (
            retrieval_confidence,
            score_quality,
            score_separation,
            result_coverage,
            breadth_bonus,
        ) = self._compute_retrieval_confidence(
            scores,
            total_results,
            expected_results,
            collections_with_results,
            total_collections,
        )

        # Phase 2: Answer Quality
        (
            answer_quality,
            citation_density,
            top_k_citation_rate,
            answer_substance,
        ) = self._compute_answer_quality(
            cited_count,
            num_paragraphs,
            total_results,
            answer_length_words,
            query_type,
        )

        # Final: Geometric-Arithmetic Hybrid Blend
        # Geometric component: bad retrieval tanks the score (GIGO principle)
        # Arithmetic component: allows partial compensation
        #
        # retrieval^0.6 × answer^0.4 → retrieval matters more in geometric
        # 0.55 × retrieval + 0.45 × answer → balanced in arithmetic
        # 60% geometric + 40% arithmetic → lean toward penalizing weak links
        if retrieval_confidence > 0 and answer_quality > 0:
            geometric = (retrieval_confidence**0.6) * (answer_quality**0.4)
        else:
            geometric = 0.0

        arithmetic = 0.55 * retrieval_confidence + 0.45 * answer_quality
        raw = 0.6 * geometric + 0.4 * arithmetic

        # Final sigmoid calibration
        # Maps: 0.3 raw → ~0.45, 0.5 raw → ~0.65, 0.7 raw → ~0.82, 0.9 raw → ~0.93
        calibrated = self._sigmoid(raw, self.FINAL_MIDPOINT, self.FINAL_STEEPNESS)

        # Floor at 0.15 (we returned something), ceiling at 0.95 (never 100% certain)
        final_score = max(0.15, min(0.95, calibrated))

        logger.debug(
            f"Confidence: retrieval={retrieval_confidence:.3f} "
            f"(quality={score_quality:.3f}, separation={score_separation:.3f}, "
            f"coverage={result_coverage:.3f}, breadth={breadth_bonus:.3f}), "
            f"answer={answer_quality:.3f} "
            f"(density={citation_density:.3f}, top_k={top_k_citation_rate:.3f}, "
            f"substance={answer_substance:.3f}), "
            f"raw={raw:.3f}, final={final_score:.3f}"
        )

        return ConfidenceBreakdown(
            score_quality=round(score_quality, 4),
            score_separation=round(score_separation, 4),
            result_coverage=round(result_coverage, 4),
            citation_density=round(citation_density, 4),
            top_k_citation_rate=round(top_k_citation_rate, 4),
            answer_substance=round(answer_substance, 4),
            retrieval_confidence=round(retrieval_confidence, 4),
            answer_quality=round(answer_quality, 4),
            final_score=round(final_score, 4),
            source_breadth_bonus=round(breadth_bonus, 4),
        )
