"""
HyDE (Hypothetical Document Embeddings) Module

Improves retrieval by generating a hypothetical answer first,
then using that answer's embedding to search for real documents.

This bridges the semantic gap between questions and answers,
especially effective for religious text queries.

Features:
- Hypothetical document generation via LLM
- Hallucination prevention through prompt engineering
- Confidence scoring for generated answers
"""
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class HyDEResult:
    """Result from HyDE search"""
    hypothetical: str  # Generated hypothetical answer
    confidence: float  # Confidence score (0-1)
    results: List  # Search results


class HyDESearch:
    """
    Hypothetical Document Embeddings (HyDE) search.
    
    Instead of searching with the user's question directly,
    generates a hypothetical answer and searches with that.
    
    Usage:
        hyde = HyDESearch()
        result = hyde.search(searcher, "nasıl namaz kılınır?")
        
        # Access results
        print(f"Hypothetical: {result.hypothetical}")
        print(f"Confidence: {result.confidence}")
        for r in result.results:
            print(r.translation)
    """
    
    # Prompt designed to minimize hallucination
    HYDE_PROMPT = """Sen kutsal metinler (Kuran ve İncil) konusunda uzman bir din alimisin.

Aşağıdaki soruya kısa ve öz bir cevap yaz (1-2 cümle).
Cevabın kutsal metinlerdeki bir ayetten alıntı gibi olmalı.

ÖNEMLİ KURALLAR:
1. Sadece kutsal metinlerde gerçekten var olan kavramları kullan
2. Spesifik ayet numaraları veya isimler UYDURMA
3. Genel dini öğretilere sadık kal
4. Emin değilsen "Bu konuda kutsal metinlerde..." şeklinde başla

Soru: {query}

Cevap (1-2 cümle, ayet tarzında):"""

    # Keywords that indicate low confidence (hallucination risk)
    LOW_CONFIDENCE_MARKERS = [
        "sanırım", "belki", "galiba", "olabilir", "muhtemelen",
        "i think", "maybe", "perhaps", "probably", "might"
    ]
    
    # Keywords that indicate high confidence
    HIGH_CONFIDENCE_MARKERS = [
        "ayet", "sure", "kutsal", "tanrı", "allah", "rab",
        "verse", "chapter", "lord", "god"
    ]
    
    def __init__(self):
        self._enhancer = None
        self._encoder = None
    
    @property
    def enhancer(self):
        """Lazy load QueryEnhancer for LLM calls"""
        if self._enhancer is None:
            from src.query_enhancer import QueryEnhancer
            self._enhancer = QueryEnhancer()
        return self._enhancer
    
    @property
    def encoder(self):
        """Lazy load DenseEncoder for embeddings"""
        if self._encoder is None:
            from src.embeddings import DenseEncoder
            self._encoder = DenseEncoder()
        return self._encoder
    
    def generate_hypothetical(self, query: str) -> Tuple[str, float]:
        """
        Generate hypothetical answer with confidence score.
        
        Returns:
            (hypothetical_text, confidence_score)
        """
        prompt = self.HYDE_PROMPT.format(query=query)
        
        try:
            hypothetical = self.enhancer._call_llm(prompt)
            hypothetical = hypothetical.strip()
            
            # Calculate confidence based on content
            confidence = self._calculate_confidence(hypothetical)
            
            return hypothetical, confidence
            
        except Exception as e:
            print(f"Warning: HyDE generation failed: {e}")
            # Fallback to original query
            return query, 0.0
    
    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate confidence score for generated text.
        
        Higher score = more likely to be reliable
        Lower score = more likely hallucination
        """
        text_lower = text.lower()
        
        # Check for low confidence markers
        low_count = sum(1 for marker in self.LOW_CONFIDENCE_MARKERS 
                       if marker in text_lower)
        
        # Check for high confidence markers
        high_count = sum(1 for marker in self.HIGH_CONFIDENCE_MARKERS 
                        if marker in text_lower)
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on markers
        confidence -= low_count * 0.15
        confidence += high_count * 0.05
        
        # Length penalty (too short or too long is suspicious)
        word_count = len(text.split())
        if word_count < 5:
            confidence -= 0.2
        elif word_count > 50:
            confidence -= 0.1
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def search(
        self, 
        searcher,  # QuranSearcher or BibleSearcher
        query: str, 
        limit: int = 10,
        min_confidence: float = 0.3
    ) -> HyDEResult:
        """
        Perform HyDE search.
        
        1. Generate hypothetical answer from query
        2. If confidence is too low, fall back to regular search
        3. Search using hypothetical's embedding
        
        Args:
            searcher: QuranSearcher or BibleSearcher instance
            query: User's search query
            limit: Number of results
            min_confidence: Minimum confidence to use HyDE (else fallback)
        
        Returns:
            HyDEResult with hypothetical, confidence, and results
        """
        # Generate hypothetical
        hypothetical, confidence = self.generate_hypothetical(query)
        
        print(f"[HyDE] Confidence: {confidence:.2f}")
        print(f"[HyDE] Hypothetical: {hypothetical[:100]}...")
        
        # If confidence too low, fall back to regular search
        if confidence < min_confidence:
            print(f"[HyDE] Low confidence ({confidence:.2f} < {min_confidence}), using original query")
            hypothetical = query
            confidence = 0.0
        
        # Encode hypothetical (or original query if fallback)
        hyde_embedding = self.encoder.encode(hypothetical)
        
        # Search with the embedding
        results = searcher.client.query_points(
            collection_name=searcher.COLLECTION_NAME,
            query=hyde_embedding,
            using="dense",
            limit=limit,
            with_payload=True
        )
        
        # Parse results
        parsed_results = searcher._parse_results(results)
        
        return HyDEResult(
            hypothetical=hypothetical,
            confidence=confidence,
            results=parsed_results
        )


# CLI integration helper
def add_hyde_to_cli(search_parser):
    """Add --hyde flag to search parser"""
    search_parser.add_argument(
        "--hyde",
        action="store_true",
        help="Use HyDE (Hypothetical Document Embeddings) for improved retrieval"
    )


if __name__ == "__main__":
    # Test HyDE
    print("Testing HyDE...\n")
    
    hyde = HyDESearch()
    
    test_queries = [
        "Allah'ın rahmeti nedir?",
        "Sabır nasıl övülür?",
        "İsa'nın mucizeleri",
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        hypothetical, confidence = hyde.generate_hypothetical(query)
        print(f"  Hypothetical: {hypothetical}")
        print(f"  Confidence: {confidence:.2f}")
        print()
