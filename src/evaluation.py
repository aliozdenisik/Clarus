"""
Search Quality Evaluation Module

ranx kütüphanesi ile arama kalitesi değerlendirmesi.
Supports precision@k, recall@k, NDCG, MRR, and MAP metrics.
"""
from typing import Dict, List, Optional

try:
    from ranx import Qrels, Run, evaluate, compare
    RANX_AVAILABLE = True
except ImportError:
    RANX_AVAILABLE = False
    print("Warning: ranx not installed. Run 'pip install ranx' for evaluation features.")


class SearchEvaluator:
    """
    Arama kalitesini değerlendiren sınıf.
    
    Kullanım:
        from src.search import QuranSearcher
        from src.evaluation import SearchEvaluator, create_sample_ground_truth
        
        searcher = QuranSearcher()
        evaluator = SearchEvaluator(searcher)
        
        # Ground truth oluştur
        queries, ground_truth = create_sample_ground_truth()
        
        # Değerlendir
        results = evaluator.evaluate(queries, ground_truth, mode="hybrid")
        print(results)
        
        # Modları karşılaştır
        report = evaluator.compare_modes(queries, ground_truth)
        print(report)
    """
    
    def __init__(self, searcher):
        """
        Initialize SearchEvaluator.
        
        Args:
            searcher: QuranSearcher or BibleSearcher instance
        """
        if not RANX_AVAILABLE:
            raise ImportError("ranx library required. Install with: pip install ranx")
        self.searcher = searcher
    
    def _create_run(self, queries: Dict[str, str], mode: str, limit: int) -> dict:
        """
        Test sorgularını çalıştır ve Run formatına dönüştür.
        
        Args:
            queries: {query_id: query_text} sözlüğü
            mode: "hybrid", "semantic", veya "keyword"
            limit: Sonuç sayısı
            
        Returns:
            {query_id: {doc_id: score}} formatında sonuçlar
        """
        run_dict = {}
        for query_id, query_text in queries.items():
            results = self.searcher.search(query_text, mode=mode, limit=limit)
            run_dict[query_id] = {r.id: float(r.score) for r in results}
        return run_dict
    
    def evaluate(
        self, 
        queries: Dict[str, str], 
        ground_truth: Dict[str, Dict[str, int]],
        mode: str = "hybrid",
        limit: int = 10,
        metrics: Optional[List[str]] = None
    ) -> dict:
        """
        Tek bir arama modunu değerlendir.
        
        Args:
            queries: {query_id: query_text} sözlüğü
            ground_truth: {query_id: {doc_id: relevance_score}} sözlüğü
            mode: "hybrid", "semantic", veya "keyword"
            limit: Sonuç sayısı
            metrics: Hesaplanacak metrikler listesi
        
        Returns:
            Metrik skorları içeren sözlük
        """
        if metrics is None:
            metrics = ["precision@5", "recall@10", "ndcg@10", "mrr", "map@10"]
        
        qrels = Qrels(ground_truth)
        run = Run(self._create_run(queries, mode, limit))
        
        return evaluate(qrels, run, metrics)
    
    def compare_modes(
        self,
        queries: Dict[str, str],
        ground_truth: Dict[str, Dict[str, int]],
        limit: int = 10,
        metrics: Optional[List[str]] = None
    ) -> str:
        """
        Hybrid, Semantic ve Keyword modlarını karşılaştır.
        
        Args:
            queries: {query_id: query_text} sözlüğü
            ground_truth: {query_id: {doc_id: relevance_score}} sözlüğü
            limit: Sonuç sayısı
            metrics: Karşılaştırılacak metrikler
        
        Returns:
            Karşılaştırma raporu (tablo formatında)
        """
        if metrics is None:
            metrics = ["precision@5", "ndcg@10", "mrr"]
        
        qrels = Qrels(ground_truth)
        
        runs = []
        for mode in ["hybrid", "semantic", "keyword"]:
            run = Run(self._create_run(queries, mode, limit), name=mode)
            runs.append(run)
        
        report = compare(
            qrels=qrels,
            runs=runs,
            metrics=metrics,
            max_p=0.05  # P-value threshold for statistical significance
        )
        
        return str(report)


def create_sample_ground_truth() -> tuple:
    """
    Örnek test verisi oluştur (geliştirme için).
    
    Ground truth formatı:
    - query_id: Sorgu tanımlayıcısı
    - doc_id: Belge/ayet ID'si (format: surah_id:verse_id)
    - relevance_score: 1-5 arası puan (5 = çok ilgili)
    
    Returns:
        (test_queries, ground_truth) tuple
    """
    # Örnek test sorguları
    test_queries = {
        "q1": "Allah'ın rahmeti",
        "q2": "sabır ve namaz",
        "q3": "cennet ve cehennem",
        "q4": "doğru yol",
        "q5": "şükür etmek"
    }
    
    # Ground truth - ilgili ayet ID'leri ve relevance skorları
    # Format: {query_id: {doc_id: relevance_score (1-5)}}
    # Not: Gerçek kullanımda bu veriler manuel olarak etiketlenmelidir
    ground_truth = {
        "q1": {
            "1:1:1": 5,   # Fatiha 1 - Besmele
            "1:2:163": 4, # Bakara 163
            "1:6:54": 4,  # En'am 54
            "1:7:156": 5  # A'raf 156
        },
        "q2": {
            "1:2:45": 5,  # Bakara 45 - Sabır ve namaz
            "1:2:153": 5, # Bakara 153
            "1:2:155": 4  # Bakara 155
        },
        "q3": {
            "1:2:81": 4,  # Bakara 81
            "1:2:82": 4,  # Bakara 82
            "1:3:185": 5  # Al-i Imran 185
        },
        "q4": {
            "1:1:6": 5,   # Fatiha 6 - Sırat-ı müstakim
            "1:1:7": 4,   # Fatiha 7
            "1:2:142": 3  # Bakara 142
        },
        "q5": {
            "1:2:152": 5, # Bakara 152
            "1:14:7": 5,  # İbrahim 7
            "1:31:12": 4  # Lokman 12
        }
    }
    
    return test_queries, ground_truth


if __name__ == "__main__":
    if RANX_AVAILABLE:
        print("Evaluation module loaded successfully.")
        print("\nSample ground truth:")
        queries, gt = create_sample_ground_truth()
        for qid, qtext in queries.items():
            print(f"  {qid}: {qtext}")
            print(f"       Relevant docs: {list(gt[qid].keys())}")
    else:
        print("ranx not available. Install with: pip install ranx")
