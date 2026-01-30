"""
Confidence Scoring Module for Clarus RAG Pipeline

Computes objective confidence scores from 5 measurable signals:
1. Retrieval Quality - Normalized mean of top-5 RRF scores
2. Score Clarity - Spread between highest and lowest scores
3. Citation Coverage - Ratio of cited verses to total context
4. Source Breadth - Diversity across collections
5. Result Volume - Actual results vs expected

Plus LLM confidence as a minor input (10% weight).

All signals are normalized to [0.0, 1.0] and combined via weighted arithmetic mean.
"""

from dataclasses import dataclass, field, asdict
from typing import List
from app.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ConfidenceBreakdown:
    """Structured confidence score breakdown with 6 signals + final score"""

    retrieval_quality: float  # 0.0-1.0: Normalized mean of top-5 RRF scores
    score_clarity: float  # 0.0-1.0: Spread between highest and lowest scores
    citation_coverage: float  # 0.0-1.0: Ratio of cited verses to total context
    source_breadth: float  # 0.0-1.0: Diversity across collections
    result_volume: float  # 0.0-1.0: Actual results vs expected
    llm_confidence: float  # 0.0-1.0: LLM-provided confidence
    final_score: float  # 0.0-1.0: Weighted mean of all signals

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return asdict(self)


class ConfidenceScorer:
    """
    Computes objective confidence scores from measurable signals.

    Weights (default):
    - retrieval_quality: 0.25 (most important - quality of search results)
    - score_clarity: 0.20 (consistency of results)
    - citation_coverage: 0.25 (how much context was actually cited)
    - source_breadth: 0.10 (diversity of sources)
    - result_volume: 0.10 (quantity of results)
    - llm_confidence: 0.10 (LLM's own confidence estimate)
    """

    def __init__(
        self,
        weight_retrieval_quality: float = 0.25,
        weight_score_clarity: float = 0.20,
        weight_citation_coverage: float = 0.25,
        weight_source_breadth: float = 0.10,
        weight_result_volume: float = 0.10,
        weight_llm_confidence: float = 0.10,
    ):
        """
        Initialize ConfidenceScorer with custom weights.

        Args:
            weight_retrieval_quality: Weight for retrieval quality signal
            weight_score_clarity: Weight for score clarity signal
            weight_citation_coverage: Weight for citation coverage signal
            weight_source_breadth: Weight for source breadth signal
            weight_result_volume: Weight for result volume signal
            weight_llm_confidence: Weight for LLM confidence signal

        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        self.weights = {
            "retrieval_quality": weight_retrieval_quality,
            "score_clarity": weight_score_clarity,
            "citation_coverage": weight_citation_coverage,
            "source_breadth": weight_source_breadth,
            "result_volume": weight_result_volume,
            "llm_confidence": weight_llm_confidence,
        }

        total_weight = sum(self.weights.values())
        if not (0.99 <= total_weight <= 1.01):
            logger.warning(
                f"Weights sum to {total_weight}, expected ~1.0. Normalizing weights."
            )
            # Normalize weights to sum to 1.0
            for key in self.weights:
                self.weights[key] /= total_weight

    def _retrieval_quality(
        self, scores: List[float], num_queries: int, k: int = 60
    ) -> float:
        """
        Compute retrieval quality from RRF scores.

        RRF scores are normalized by the theoretical maximum based on number of queries.
        Theoretical max = num_queries / (k + 1)

        Args:
            scores: List of RRF scores (typically 0.016-0.08)
            num_queries: Number of query variants used
            k: RRF k-parameter (default 60)

        Returns:
            float: Normalized retrieval quality [0.0, 1.0]
        """
        # Edge cases
        if not scores:
            return 0.0
        if num_queries <= 0:
            return 0.0

        # Use top-5 scores or all if fewer than 5
        top_scores = scores[: min(5, len(scores))]
        mean_score = sum(top_scores) / len(top_scores)

        # Theoretical maximum: num_queries / (k + 1)
        theoretical_max = num_queries / (k + 1)

        if theoretical_max <= 0:
            return 0.0

        # Normalize by theoretical max
        normalized = mean_score / theoretical_max

        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, normalized))

    def _score_clarity(self, scores: List[float]) -> float:
        """
        Compute score clarity from spread between highest and lowest scores.

        Clarity = (max - min) / max
        High clarity = consistent results (good)
        Low clarity = inconsistent results (bad)

        Args:
            scores: List of RRF scores

        Returns:
            float: Score clarity [0.0, 1.0]
        """
        # Edge cases
        if not scores:
            return 0.0
        if len(scores) == 1:
            return 1.0

        max_score = scores[0]
        min_score = scores[-1]

        # If top score is 0 or negative, return 0
        if max_score <= 0:
            return 0.0

        # If top and bottom are equal, return 0 (no clarity)
        if max_score == min_score:
            return 0.0

        clarity = (max_score - min_score) / max_score

        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, clarity))

    def _citation_coverage(self, cited_count: int, total_context: int) -> float:
        """
        Compute citation coverage ratio.

        Coverage = cited_count / total_context
        High coverage = most context was cited (good)
        Low coverage = little context was cited (bad)

        Args:
            cited_count: Number of verses actually cited in answer
            total_context: Total number of verses provided as context

        Returns:
            float: Citation coverage [0.0, 1.0]
        """
        if total_context <= 0:
            return 0.0

        coverage = cited_count / total_context

        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, coverage))

    def _source_breadth(
        self, collections_with_results: int, total_collections: int
    ) -> float:
        """
        Compute source breadth from collection diversity.

        Breadth = collections_with_results / total_collections
        High breadth = results from multiple sources (good)
        Low breadth = results from single source (less good)

        Args:
            collections_with_results: Number of collections with at least 1 result
            total_collections: Total number of collections searched

        Returns:
            float: Source breadth [0.0, 1.0]
        """
        if total_collections <= 0:
            return 1.0  # Defensive: if no collections, assume good

        breadth = collections_with_results / total_collections

        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, breadth))

    def _result_volume(self, actual_results: int, expected_results: int) -> float:
        """
        Compute result volume ratio.

        Volume = actual_results / expected_results
        High volume = got expected number of results (good)
        Low volume = fewer results than expected (less good)

        Args:
            actual_results: Number of results actually retrieved
            expected_results: Expected/target number of results

        Returns:
            float: Result volume [0.0, 1.0]
        """
        if expected_results <= 0:
            return 1.0  # Defensive: if no expectation, assume good

        volume = actual_results / expected_results

        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, volume))

    def compute(
        self,
        scores: List[float],
        num_queries: int,
        cited_count: int,
        total_context: int,
        collections_with_results: int,
        total_collections: int,
        actual_results: int,
        expected_results: int,
        llm_confidence: float,
        k: int = 60,
    ) -> ConfidenceBreakdown:
        """
        Compute comprehensive confidence score from all signals.

        Args:
            scores: List of RRF scores from search results
            num_queries: Number of query variants used
            cited_count: Number of verses cited in answer
            total_context: Total verses provided as context
            collections_with_results: Number of collections with results
            total_collections: Total collections searched
            actual_results: Number of results retrieved
            expected_results: Expected number of results
            llm_confidence: LLM's confidence estimate [0.0, 1.0]
            k: RRF k-parameter (default 60)

        Returns:
            ConfidenceBreakdown: Detailed confidence breakdown with final score
        """
        # Compute individual signals
        retrieval_quality = self._retrieval_quality(scores, num_queries, k)
        score_clarity = self._score_clarity(scores)
        citation_coverage = self._citation_coverage(cited_count, total_context)
        source_breadth = self._source_breadth(
            collections_with_results, total_collections
        )
        result_volume = self._result_volume(actual_results, expected_results)

        # Clamp LLM confidence to [0.0, 1.0]
        llm_confidence = min(1.0, max(0.0, llm_confidence))

        # Compute weighted mean
        signals = {
            "retrieval_quality": retrieval_quality,
            "score_clarity": score_clarity,
            "citation_coverage": citation_coverage,
            "source_breadth": source_breadth,
            "result_volume": result_volume,
            "llm_confidence": llm_confidence,
        }

        final_score = sum(signals[key] * self.weights[key] for key in signals.keys())

        # Clamp final score to [0.0, 1.0]
        final_score = min(1.0, max(0.0, final_score))

        logger.debug(
            f"Confidence breakdown: retrieval_quality={retrieval_quality:.3f}, "
            f"score_clarity={score_clarity:.3f}, "
            f"citation_coverage={citation_coverage:.3f}, "
            f"source_breadth={source_breadth:.3f}, "
            f"result_volume={result_volume:.3f}, "
            f"llm_confidence={llm_confidence:.3f}, "
            f"final_score={final_score:.3f}"
        )

        return ConfidenceBreakdown(
            retrieval_quality=retrieval_quality,
            score_clarity=score_clarity,
            citation_coverage=citation_coverage,
            source_breadth=source_breadth,
            result_volume=result_volume,
            llm_confidence=llm_confidence,
            final_score=final_score,
        )
