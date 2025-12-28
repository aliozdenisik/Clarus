"""
RAGAS Evaluation Module

Provides comprehensive RAG quality evaluation beyond traditional IR metrics.

Metrics:
- Faithfulness: How factually consistent is the answer with the context?
- Context Precision: How relevant are the retrieved chunks?
- Context Recall: Did we retrieve all necessary information?
- Answer Relevancy: How relevant is the answer to the question?

Usage:
    from src.evaluation_ragas import RAGASEvaluator
    
    evaluator = RAGASEvaluator()
    results = evaluator.evaluate(questions, contexts, answers, ground_truths)
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class RAGASResult:
    """Results from RAGAS evaluation"""
    faithfulness: float
    context_precision: float
    context_recall: float
    answer_relevancy: float
    overall_score: float
    details: Dict


class RAGASEvaluator:
    """
    RAG evaluation using RAGAS framework.
    
    Provides deeper quality assessment than traditional IR metrics.
    
    Why RAGAS over ranx?
    - ranx: Measures retrieval ranking (Precision@K, nDCG)
    - RAGAS: Measures end-to-end RAG quality (faithfulness, hallucination detection)
    
    For sacred texts, faithfulness is critical - misquoting is unacceptable.
    """
    
    def __init__(self, use_llm_judge: bool = True):
        """
        Initialize RAGAS evaluator.
        
        Args:
            use_llm_judge: If True, use LLM for evaluation (more accurate but costly)
                          If False, use heuristic methods (faster, less accurate)
        """
        self.use_llm_judge = use_llm_judge
        self._ragas_available = self._check_ragas()
    
    def _check_ragas(self) -> bool:
        """Check if RAGAS library is available"""
        try:
            import ragas
            return True
        except ImportError:
            print("Warning: RAGAS not installed. Install with: pip install ragas")
            print("Using heuristic evaluation methods instead.")
            return False
    
    def evaluate(
        self,
        questions: List[str],
        contexts: List[List[str]],  # List of retrieved context chunks per question
        answers: Optional[List[str]] = None,
        ground_truths: Optional[List[str]] = None
    ) -> RAGASResult:
        """
        Evaluate RAG quality.
        
        Args:
            questions: List of user queries
            contexts: Retrieved context chunks for each query
            answers: Generated answers (optional, for full RAG eval)
            ground_truths: Expected answers (optional, for comparison)
        
        Returns:
            RAGASResult with all metrics
        """
        if self._ragas_available and self.use_llm_judge:
            return self._evaluate_with_ragas(questions, contexts, answers, ground_truths)
        else:
            return self._evaluate_heuristic(questions, contexts, answers, ground_truths)
    
    def _evaluate_with_ragas(
        self,
        questions: List[str],
        contexts: List[List[str]],
        answers: Optional[List[str]],
        ground_truths: Optional[List[str]]
    ) -> RAGASResult:
        """Evaluate using RAGAS library with LLM judge"""
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
        from datasets import Dataset
        
        # Prepare data
        data = {
            "question": questions,
            "contexts": contexts,
        }
        
        if answers:
            data["answer"] = answers
        if ground_truths:
            data["ground_truth"] = ground_truths
        
        dataset = Dataset.from_dict(data)
        
        # Select metrics based on available data
        metrics = [context_precision]
        if answers:
            metrics.extend([faithfulness, answer_relevancy])
        if ground_truths:
            metrics.append(context_recall)
        
        # Run evaluation
        result = evaluate(dataset=dataset, metrics=metrics)
        
        # Extract scores
        scores = result.to_pandas().mean().to_dict()
        
        return RAGASResult(
            faithfulness=scores.get("faithfulness", 0.0),
            context_precision=scores.get("context_precision", 0.0),
            context_recall=scores.get("context_recall", 0.0),
            answer_relevancy=scores.get("answer_relevancy", 0.0),
            overall_score=sum(scores.values()) / len(scores) if scores else 0.0,
            details=scores
        )
    
    def _evaluate_heuristic(
        self,
        questions: List[str],
        contexts: List[List[str]],
        answers: Optional[List[str]],
        ground_truths: Optional[List[str]]
    ) -> RAGASResult:
        """
        Heuristic evaluation without LLM judge.
        
        Uses simple text overlap and keyword matching.
        Less accurate but much faster and free.
        """
        results = {
            "context_precision": [],
            "context_recall": [],
            "faithfulness": [],
            "answer_relevancy": []
        }
        
        for i, (question, context_list) in enumerate(zip(questions, contexts)):
            # Context precision: keyword overlap between question and context
            q_words = set(question.lower().split())
            ctx_words = set(" ".join(context_list).lower().split())
            
            if q_words:
                overlap = len(q_words & ctx_words) / len(q_words)
                results["context_precision"].append(min(1.0, overlap))
            
            # Context recall (if ground truth available)
            if ground_truths and i < len(ground_truths):
                gt = ground_truths[i]
                gt_words = set(gt.lower().split())
                if gt_words:
                    recall = len(gt_words & ctx_words) / len(gt_words)
                    results["context_recall"].append(min(1.0, recall))
            
            # Faithfulness (if answer available)
            if answers and i < len(answers):
                answer = answers[i]
                ans_words = set(answer.lower().split())
                if ans_words:
                    # How much of the answer is grounded in context?
                    grounded = len(ans_words & ctx_words) / len(ans_words)
                    results["faithfulness"].append(min(1.0, grounded))
            
            # Answer relevancy
            if answers and i < len(answers):
                answer = answers[i]
                ans_words = set(answer.lower().split())
                if q_words and ans_words:
                    relevancy = len(q_words & ans_words) / len(q_words)
                    results["answer_relevancy"].append(min(1.0, relevancy))
        
        # Calculate averages
        def safe_avg(lst):
            return sum(lst) / len(lst) if lst else 0.0
        
        faithfulness = safe_avg(results["faithfulness"])
        context_precision = safe_avg(results["context_precision"])
        context_recall = safe_avg(results["context_recall"])
        answer_relevancy = safe_avg(results["answer_relevancy"])
        
        all_scores = [s for s in [faithfulness, context_precision, context_recall, answer_relevancy] if s > 0]
        
        return RAGASResult(
            faithfulness=faithfulness,
            context_precision=context_precision,
            context_recall=context_recall,
            answer_relevancy=answer_relevancy,
            overall_score=sum(all_scores) / len(all_scores) if all_scores else 0.0,
            details={
                "faithfulness_samples": len(results["faithfulness"]),
                "precision_samples": len(results["context_precision"]),
                "recall_samples": len(results["context_recall"]),
                "relevancy_samples": len(results["answer_relevancy"]),
                "method": "heuristic"
            }
        )
    
    def evaluate_retrieval(
        self,
        searcher,
        test_queries: List[Dict[str, str]]
    ) -> Dict:
        """
        Evaluate retrieval quality for a set of test queries.
        
        Args:
            searcher: QuranSearcher or BibleSearcher
            test_queries: List of {"query": str, "expected": str} dicts
        
        Returns:
            Evaluation results with per-query and aggregate scores
        """
        questions = []
        contexts = []
        ground_truths = []
        
        for item in test_queries:
            query = item["query"]
            expected = item.get("expected", "")
            
            # Run search
            results = searcher.search(query, mode="hybrid", limit=5)
            
            # Extract context
            context_texts = []
            for r in results:
                text = getattr(r, "translation", None) or getattr(r, "text", "")
                context_texts.append(text)
            
            questions.append(query)
            contexts.append(context_texts)
            if expected:
                ground_truths.append(expected)
        
        # Evaluate
        result = self.evaluate(
            questions=questions,
            contexts=contexts,
            ground_truths=ground_truths if ground_truths else None
        )
        
        return {
            "overall_score": result.overall_score,
            "context_precision": result.context_precision,
            "context_recall": result.context_recall,
            "num_queries": len(questions),
            "details": result.details
        }


# Sample test queries for evaluation
SAMPLE_TEST_QUERIES = [
    {"query": "Allah'ın rahmeti", "expected": "Rahman ve Rahim"},
    {"query": "sabır ve namaz", "expected": "sabır namaz yardım"},
    {"query": "cennet nimetleri", "expected": "cennet altından nehirler"},
    {"query": "İsa mucizeleri", "expected": "ölüleri diriltir hastalara şifa"},
]


if __name__ == "__main__":
    print("=== RAGAS Evaluator Test ===\n")
    
    evaluator = RAGASEvaluator(use_llm_judge=False)  # Use heuristic
    
    # Test data
    questions = ["Allah'ın rahmeti nedir?", "Sabır nasıl övülür?"]
    contexts = [
        ["Allah Rahman ve Rahimdir", "O çok merhametlidir"],
        ["Sabredenler için büyük mükafat vardır", "Sabır imanın yarısıdır"]
    ]
    ground_truths = ["Rahman Rahim merhamet", "sabır mükafat iman"]
    
    result = evaluator.evaluate(questions, contexts, ground_truths=ground_truths)
    
    print(f"Context Precision: {result.context_precision:.2f}")
    print(f"Context Recall: {result.context_recall:.2f}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"\nDetails: {result.details}")
