"""
Ultimate RAG Pipeline - Maximum Accuracy Search System

Bu modül tüm en iyi RAG metodolojilerini tek bir pipeline'da birleştirir:
1. Query Enhancement (LLM ile sorgu genişletme) - ZORUNLU
2. Multi-Query Generation (3 farklı perspektif) - OPSİYONEL
3. Semantic Search (en iyi performans gösteren arama)
4. Semantic Chunk Search (paralel - gruplu ayetleri arar) - OPSİYONEL
5. Cross-Encoder Reranking (Qwen3-Reranker) - ZORUNLU

Doğruluk odaklı - Süre önemli değil!

Usage:
    from src.ultimate_rag import UltimateRAG
    
    rag = UltimateRAG(enable_semantic_chunks=True)  # Parallel search
    results = rag.search("Kur'an'da şefaat kavramı nasıl açıklanır?")
"""
import os
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console

console = Console()


@dataclass
class UltimateSearchResult:
    """Enhanced search result with full metadata"""
    id: str
    score: float
    text: str
    reference: str  # Surah:Verse or Book Chapter:Verse
    source: str     # quran_tr, bible_kjva, etc.
    original_score: float = 0.0
    rerank_score: float = 0.0
    matched_queries: List[str] = field(default_factory=list)


class UltimateRAG:
    """
    Ultimate RAG Pipeline - Maximum Accuracy
    
    Pipeline aşamaları:
    1. ENHANCE: LLM ile sorguyu genişlet (eşanlamlılar, ilgili kavramlar)
    2. MULTI-QUERY: 3 farklı perspektiften sorgu varyasyonları üret
    3. SEARCH: Tüm sorgularla semantic arama yap, sonuçları birleştir (RRF)
       - Single-verse collection (quran_tr)
       - Semantic chunks collection (quran_semantic_chunks) - OPSİYONEL
    4. RERANK: Cross-encoder ile en alakalı sonuçları seçen final sıralama
    
    Ayarlar:
        enable_multi_query: Multi-query aşamasını aktif et (default: True)
        enable_semantic_chunks: Semantic chunk aramasını paralel çalıştır (default: True)
        search_mode: Arama modu - "semantic" önerilen (default: "semantic")
        rerank_pool_size: Reranker'a gidecek max sonuç sayısı (default: 50)
        final_top_k: Final sonuç sayısı (default: 10)
    """
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        enable_multi_query: bool = True,
        enable_semantic_chunks: bool = True,  # Parallel semantic chunk search
        search_mode: str = "semantic",  # semantic performs best for Turkish
        rerank_pool_size: int = 50,
        final_top_k: int = 10,
        verbose: bool = True
    ):
        self.qdrant_url = qdrant_url
        self.enable_multi_query = enable_multi_query
        self.enable_semantic_chunks = enable_semantic_chunks
        self.search_mode = search_mode
        self.rerank_pool_size = rerank_pool_size
        self.final_top_k = final_top_k
        self.verbose = verbose
        
        # Lazy load components
        self._enhancer = None
        self._reranker = None
        self._quran_searcher = None
        self._bible_searcher = None
        self._semantic_chunk_searcher = None
        
    @property
    def enhancer(self):
        """Lazy load Query Enhancer"""
        if self._enhancer is None:
            from src.query_enhancer import QueryEnhancer
            self._enhancer = QueryEnhancer()
            if self.verbose:
                console.print("[dim]Loaded QueryEnhancer[/dim]")
        return self._enhancer
    
    @property
    def reranker(self):
        """Lazy load Reranker"""
        if self._reranker is None:
            from src.reranker import Reranker
            self._reranker = Reranker()
            if self.verbose:
                console.print("[dim]Loaded Qwen3-Reranker[/dim]")
        return self._reranker
    
    def _get_searcher(self, source: str):
        """Get appropriate searcher for source"""
        if source == "quran_tr":
            if self._quran_searcher is None:
                from src.search import QuranSearcher
                self._quran_searcher = QuranSearcher(qdrant_url=self.qdrant_url)
            return self._quran_searcher
        else:
            if self._bible_searcher is None:
                from src.search import BibleSearcher
                translation = source.replace("bible_", "")
                self._bible_searcher = BibleSearcher(
                    translation=translation, 
                    qdrant_url=self.qdrant_url
                )
            return self._bible_searcher
    
    def _get_semantic_chunk_searcher(self):
        """Get semantic chunk searcher (lazy load)"""
        if self._semantic_chunk_searcher is None:
            from src.search import SemanticChunkSearcher
            self._semantic_chunk_searcher = SemanticChunkSearcher(qdrant_url=self.qdrant_url)
        return self._semantic_chunk_searcher
    
    def _log(self, message: str, style: str = "dim"):
        """Log message if verbose"""
        if self.verbose:
            console.print(f"[{style}]{message}[/{style}]")
    
    def _enhance_query(self, query: str, source: str = "bible_kjva") -> str:
        """Step 1: Enhance query with LLM"""
        self._log("⚡ Step 1: Query Enhancement...")
        start = time.time()
        
        # Determine corpus from source
        corpus = "quran" if "quran" in source else "bible"
        
        enhanced = self.enhancer.expand_query(query, corpus=corpus)
        
        duration = (time.time() - start) * 1000
        self._log(f"   Enhanced ({corpus}) in {duration:.0f}ms: {enhanced[:80]}...")
        return enhanced
    
    def _generate_multi_queries(self, query: str, enhanced_query: str, source: str = "bible_kjva", n: int = 3) -> List[str]:
        """Step 2: Generate multiple query perspectives"""
        if not self.enable_multi_query:
            return [enhanced_query]
        
        self._log("🔄 Step 2: Multi-Query Generation...")
        start = time.time()
        
        # Determine corpus from source
        corpus = "quran" if "quran" in source else "bible"
        
        # Always include original and enhanced
        queries = [query, enhanced_query]
        
        # Generate additional perspectives
        try:
            multi = self.enhancer.generate_multi_query(enhanced_query, n=n, corpus=corpus)
            queries.extend(multi)
        except Exception as e:
            self._log(f"   Warning: Multi-query failed: {e}", "yellow")
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower not in seen:
                seen.add(q_lower)
                unique.append(q)
        
        duration = (time.time() - start) * 1000
        self._log(f"   Generated {len(unique)} queries in {duration:.0f}ms")
        return unique
    
    def _search_all_queries(self, queries: List[str], source: str, limit: int = 30) -> List:
        """Step 3: Search with all queries and merge results (RRF)"""
        self._log(f"🔍 Step 3: Searching with {len(queries)} queries...")
        start = time.time()
        
        searcher = self._get_searcher(source)
        
        # Collect all results with their ranks
        all_results = {}  # id -> (result, rrf_score)
        k = 60  # RRF constant
        
        # Search single-verse collection
        for i, query in enumerate(queries):
            try:
                results = searcher.search(query, mode=self.search_mode, limit=limit)
                
                for rank, result in enumerate(results, 1):
                    result_id = result.id if hasattr(result, 'id') else f"{i}_{rank}"
                    rrf_contribution = 1 / (k + rank)
                    
                    if result_id in all_results:
                        # Accumulate RRF score
                        existing_result, existing_score, matched = all_results[result_id]
                        all_results[result_id] = (
                            existing_result, 
                            existing_score + rrf_contribution,
                            matched + [query]
                        )
                    else:
                        all_results[result_id] = (result, rrf_contribution, [query])
                        
            except Exception as e:
                self._log(f"   Warning: Search failed for query: {e}", "yellow")
        
        # Parallel search: Semantic chunks (only for Quran)
        if self.enable_semantic_chunks and source == "quran_tr":
            try:
                chunk_searcher = self._get_semantic_chunk_searcher()
                if chunk_searcher.collection_exists():
                    self._log("   📦 Including semantic chunks in search...")
                    
                    for i, query in enumerate(queries):
                        try:
                            chunk_results = chunk_searcher.search(query, mode=self.search_mode, limit=limit // 2)
                            
                            for rank, chunk_result in enumerate(chunk_results, 1):
                                # For each verse in the semantic chunk, add to results
                                # This expands the context while keeping individual verse scores
                                chunk_id = chunk_result.chunk_id
                                rrf_contribution = 1 / (k + rank)
                                
                                # Store chunk result with a unique ID
                                if chunk_id in all_results:
                                    existing_result, existing_score, matched = all_results[chunk_id]
                                    all_results[chunk_id] = (
                                        existing_result, 
                                        existing_score + rrf_contribution,
                                        matched + [query]
                                    )
                                else:
                                    # Create a pseudo-result that works with reranker
                                    # Use combined translation as the text to rerank
                                    all_results[chunk_id] = (chunk_result, rrf_contribution, [query])
                                    
                        except Exception as e:
                            self._log(f"   Warning: Chunk search failed: {e}", "yellow")
                else:
                    self._log("   [dim]Semantic chunks collection not found, skipping...[/dim]")
            except Exception as e:
                self._log(f"   Warning: Could not load semantic chunks: {e}", "yellow")
        
        # Sort by RRF score and return top results
        sorted_results = sorted(
            all_results.values(), 
            key=lambda x: x[1], 
            reverse=True
        )[:self.rerank_pool_size]
        
        # Attach RRF info to results
        merged_results = []
        for result, rrf_score, matched_queries in sorted_results:
            result.score = rrf_score
            merged_results.append(result)
        
        duration = (time.time() - start) * 1000
        self._log(f"   Found {len(merged_results)} unique results in {duration:.0f}ms")
        return merged_results
    
    def _rerank_results(self, query: str, results: List, top_k: int = None) -> List:
        """Step 4: Rerank with cross-encoder"""
        self._log(f"🏆 Step 4: Reranking {len(results)} results...")
        start = time.time()
        
        top_k = top_k or self.final_top_k
        
        if not results:
            return []
        
        try:
            reranked = self.reranker.rerank(query, results, top_k=top_k)
            duration = (time.time() - start) * 1000
            self._log(f"   Reranked to top {len(reranked)} in {duration:.0f}ms")
            return reranked
        except Exception as e:
            self._log(f"   Warning: Reranking failed: {e}", "yellow")
            return results[:top_k]
    
    def search(
        self, 
        query: str, 
        source: str = "quran_tr",
        top_k: int = None,
        rerank_query: str = None  # Optional: use different query for reranking
    ) -> List:
        """
        Execute Ultimate RAG Pipeline
        
        Args:
            query: User's search query
            source: Data source - "quran_tr", "bible_kjva"
            top_k: Number of final results (default: self.final_top_k)
            rerank_query: Optional query to use for reranking (useful for translated queries)
            
        Returns:
            List of reranked search results
        """
        top_k = top_k or self.final_top_k
        total_start = time.time()
        
        if self.verbose:
            console.print(f"\n[bold blue]🚀 Ultimate RAG Pipeline[/bold blue]")
            console.print(f"[dim]Query: \"{query}\"[/dim]\n")
        
        # Step 1: Enhance query
        enhanced_query = self._enhance_query(query, source=source)
        
        # Step 2: Generate multi-queries
        all_queries = self._generate_multi_queries(query, enhanced_query, source=source)
        
        # Step 3: Search with all queries (RRF merge)
        search_results = self._search_all_queries(all_queries, source)
        
        # Step 4: Rerank for final precision
        # Use rerank_query if provided (e.g., translated query), otherwise use original
        final_query = rerank_query or query
        final_results = self._rerank_results(final_query, search_results, top_k=top_k)
        
        total_duration = (time.time() - total_start) * 1000
        
        if self.verbose:
            console.print(f"\n[green]✓ Pipeline complete in {total_duration:.0f}ms[/green]")
            console.print(f"[dim]  Enhanced → {len(all_queries)} queries → {len(search_results)} candidates → {len(final_results)} final[/dim]\n")
        
        return final_results
    
    def search_quran(self, query: str, top_k: int = None) -> List:
        """Shortcut for Quran search"""
        return self.search(query, source="quran_tr", top_k=top_k)
    
    def search_bible(self, query: str, translation: str = "kjva", top_k: int = None) -> List:
        """
        Shortcut for Bible search.
        
        For English translations (kjva, kjv), automatically translates Turkish queries to English
        and uses the translated query for reranking to ensure proper cross-lingual matching.
        """
        original_query = query
        translated_query = None
        
        # For English Bible translations, translate Turkish query to English
        if translation in ("kjva", "kjv"):
            try:
                translated_query = self.enhancer.translate_for_bible(query)
                if self.verbose:
                    console.print(f"[dim]📝 Translated: {query} → {translated_query}[/dim]")
                query = translated_query
            except Exception as e:
                if self.verbose:
                    console.print(f"[yellow]Translation warning: {e}[/yellow]")
        
        # Pass translated query for reranking to fix language mismatch
        return self.search(query, source=f"bible_{translation}", top_k=top_k, rerank_query=translated_query)


# Convenience function
def ultimate_search(query: str, source: str = "quran_tr", top_k: int = 10) -> List:
    """
    One-liner for Ultimate RAG search
    
    Usage:
        from src.ultimate_rag import ultimate_search
        results = ultimate_search("Kur'an'da şefaat kavramı")
    """
    rag = UltimateRAG(verbose=True)
    return rag.search(query, source=source, top_k=top_k)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test the Ultimate RAG Pipeline
    console.print("[bold]Testing Ultimate RAG Pipeline[/bold]\n")
    
    rag = UltimateRAG()
    
    test_queries_quran = [
        "Kur'an'da şefaat kavramı nasıl açıklanır?",
    ]
    
    console.print("\n[bold green]--- QURAN TESTS ---[/bold green]")
    for query in test_queries_quran:
        results = rag.search_quran(query, top_k=3)
        console.print(f"\n[bold cyan]Query: {query}[/bold cyan]")
        for i, r in enumerate(results, 1):
            # Handle standard PointStruct or SemanticChunkSearchResult
            payload = getattr(r, 'payload', {}) or {}
            
            # Try to get reference from object attributes or payload
            surah = getattr(r, 'surah_id', payload.get('surah_id'))
            verse = getattr(r, 'verse_id', getattr(r, 'verse_ids', payload.get('verse_id', payload.get('verse_ids'))))
            
            ref = f"{surah}:{verse}" 
            text = getattr(r, 'translation', payload.get('translation', ''))[:100]
            
            console.print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            console.print(f"     {text}...")
            
    console.print("\n[bold green]--- BIBLE TESTS ---[/bold green]")
    test_queries_bible = [
        "God's love and mercy",
    ]
    for query in test_queries_bible:
        results = rag.search_bible(query, top_k=3)
        console.print(f"\n[bold cyan]Query: {query}[/bold cyan]")
        for i, r in enumerate(results, 1):
            payload = getattr(r, 'payload', {}) or {}
            book = getattr(r, 'book_name', payload.get('book_name', 'Unknown'))
            chapter = getattr(r, 'chapter_number', payload.get('chapter_number'))
            verse = getattr(r, 'verse_number', payload.get('verse_number'))
            
            ref = f"{book} {chapter}:{verse}"
            text = getattr(r, 'text', getattr(r, 'content', payload.get('text', '')))[:100]
            
            console.print(f"  {i}. [{ref}] (score: {r.score:.4f})")
            console.print(f"     {text}...")

