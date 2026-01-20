"""
Multi-Agent Answer Generator Module

Generates theological commentaries from multi-scripture search results
using 4 specialized agents (OT, NT, Apocrypha, Quran) + 1 summary agent.

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │              4 Parallel Specialist Agents               │
    │  ┌─────────┐ ┌─────────┐ ┌───────────┐ ┌─────────────┐  │
    │  │OT Agent │ │NT Agent │ │Apoc Agent │ │Quran Agent  │  │
    │  └────┬────┘ └────┬────┘ └─────┬─────┘ └──────┬──────┘  │
    │       │           │            │              │          │
    │       ▼           ▼            ▼              ▼          │
    │      P1          P2           P3             P4          │
    └───────┼───────────┼────────────┼──────────────┼──────────┘
            │           │            │              │
            └───────────┴─────┬──────┴──────────────┘
                              ▼
                       Summary Agent
                              │
                              ▼
                             P5

Output: 5 paragraphs (OT, NT, Apocrypha, Quran, Synthesis)
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class MultiAgentAnswer:
    """Multi-agent theological analysis result"""
    old_testament_commentary: str        # Paragraph 1: OT perspective
    new_testament_commentary: str        # Paragraph 2: NT perspective  
    apocrypha_commentary: str            # Paragraph 3: Apocryphal perspective
    quran_commentary: str                # Paragraph 4: Islamic perspective
    synthesis: str                       # Paragraph 5: Comparative summary
    
    citations: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 0.0
    query: str = ""
    verses_provided: Dict[str, int] = field(default_factory=dict)
    
    def to_essay(self) -> str:
        """Format as complete essay with all 5 paragraphs"""
        sections = []
        
        if self.old_testament_commentary:
            sections.append(f"## Eski Ahit (Old Testament)\n\n{self.old_testament_commentary}")
        
        if self.new_testament_commentary:
            sections.append(f"## Yeni Ahit (New Testament)\n\n{self.new_testament_commentary}")
        
        if self.apocrypha_commentary:
            sections.append(f"## Apokrifa (Apocrypha)\n\n{self.apocrypha_commentary}")
        
        if self.quran_commentary:
            sections.append(f"## Kuran-ı Kerim\n\n{self.quran_commentary}")
        
        if self.synthesis:
            sections.append(f"## Karşılaştırmalı Değerlendirme\n\n{self.synthesis}")
        
        return "\n\n---\n\n".join(sections)


class BaseSpecialistAgent:
    """Base class for specialist theological agents"""
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "google/gemini-3-flash-preview"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required")
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/qdrant/qdrant",
        }
    
    def _extract_reference(self, result, source: str) -> str:
        """Extract reference string from search result"""
        if "quran" in source:
            surah_name = getattr(result, 'surah_name', None)
            verse = getattr(result, 'verse_id', None) or getattr(result, 'verse_ids', None)
            
            if surah_name is None and hasattr(result, 'payload'):
                payload = result.payload or {}
                surah_name = payload.get('surah_name')
                verse = payload.get('verse_id') or payload.get('verse_ids')
            
            if surah_name and verse:
                return f"{surah_name}:{verse}"
            return "Unknown"
        else:
            book = getattr(result, 'book_name', None)
            chapter = getattr(result, 'chapter_number', None) or getattr(result, 'chapter', None)
            verse = getattr(result, 'verse_number', None) or getattr(result, 'verse', None)
            
            if book is None and hasattr(result, 'payload'):
                payload = result.payload or {}
                book = payload.get('book_name', 'Unknown')
                chapter = payload.get('chapter_number') or payload.get('chapter')
                verse = payload.get('verse_number') or payload.get('verse')
            
            if book and chapter and verse:
                return f"{book} {chapter}:{verse}"
            return "Unknown"
    
    def _extract_text(self, result) -> str:
        """Extract verse text from search result"""
        for attr in ['translation', 'text', 'content', 'combined_translation']:
            text = getattr(result, attr, None)
            if text:
                return text[:400]
        
        if hasattr(result, 'payload'):
            payload = result.payload or {}
            for key in ['translation', 'text', 'content']:
                if key in payload:
                    return str(payload[key])[:400]
        return ""
    
    def _format_verses(self, results: List, source: str, max_results: int = 15) -> str:
        """Format verses for LLM context"""
        lines = []
        for i, result in enumerate(results[:max_results], 1):
            ref = self._extract_reference(result, source)
            text = self._extract_text(result)
            if text:
                lines.append(f"[{i}] {ref} - {text}")
        return "\n".join(lines)
    
    def _call_llm(self, messages: List[Dict], max_tokens: int = 1000) -> dict:
        """Call OpenRouter API"""
        try:
            response = requests.post(
                self.OPENROUTER_URL,
                headers=self._headers,
                json={
                    "model": self.MODEL,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": max_tokens,
                    "temperature": 0.3
                },
                timeout=60
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return json.loads(content)
        except Exception as e:
            print(f"LLM call failed: {e}")
            return {"commentary": "", "citations": [], "confidence": 0.0}


class OldTestamentAgent(BaseSpecialistAgent):
    """Specialist agent for Old Testament (Eski Ahit) interpretation"""
    
    SYSTEM_PROMPT = """Sen uzman bir Eski Ahit (Tevrat/Zebur) alimi ve tefsircisisin.
Görevin: Kullanıcının sorusunu, sana verilen Eski Ahit ayetlerine dayanarak yorumlamak.

KRİTİK KURALLAR:
1. SADECE verilen Eski Ahit ayetlerindeki bilgileri kullan
2. Her iddiayı [Kitap Bölüm:Ayet] formatında kaynak göster. Örnek: [Genesis 1:1], [Psalms 23:1]
3. Yahudi-Hristiyan tefsir geleneğine uygun yorumla
4. Tek bir bütünlüklü paragraf yaz (3-5 cümle)
5. Cevabın TAMAMI Türkçe olmalı

ÇIKTI FORMATI (JSON):
{
    "commentary": "Eski Ahit perspektifinden yorum paragrafı [Genesis 1:1] şeklinde kaynaklarla...",
    "citations": ["Genesis 1:1", "Psalms 23:1"],
    "confidence": 0.85
}"""

    def generate(self, query: str, verses: List) -> Dict[str, Any]:
        """Generate OT commentary paragraph"""
        if not verses:
            return {"commentary": "", "citations": [], "confidence": 0.0}
        
        context = self._format_verses(verses, "bible")
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"SORU: {query}\n\nESKİ AHİT AYETLERİ:\n{context}"}
        ]
        return self._call_llm(messages)


class NewTestamentAgent(BaseSpecialistAgent):
    """Specialist agent for New Testament (Yeni Ahit) interpretation"""
    
    SYSTEM_PROMPT = """Sen uzman bir Yeni Ahit (İncil) alimi ve tefsircisisin.
Görevin: Kullanıcının sorusunu, sana verilen Yeni Ahit ayetlerine dayanarak yorumlamak.

KRİTİK KURALLAR:
1. SADECE verilen Yeni Ahit ayetlerindeki bilgileri kullan
2. Her iddiayı [Kitap Bölüm:Ayet] formatında kaynak göster. Örnek: [John 3:16], [Romans 5:8]
3. Hristiyan tefsir geleneğine uygun yorumla (Kristolojik perspektif)
4. Tek bir bütünlüklü paragraf yaz (3-5 cümle)
5. Cevabın TAMAMI Türkçe olmalı

ÇIKTI FORMATI (JSON):
{
    "commentary": "Yeni Ahit perspektifinden yorum paragrafı [John 3:16] şeklinde kaynaklarla...",
    "citations": ["John 3:16", "Romans 5:8"],
    "confidence": 0.85
}"""

    def generate(self, query: str, verses: List) -> Dict[str, Any]:
        """Generate NT commentary paragraph"""
        if not verses:
            return {"commentary": "", "citations": [], "confidence": 0.0}
        
        context = self._format_verses(verses, "bible")
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"SORU: {query}\n\nYENİ AHİT AYETLERİ:\n{context}"}
        ]
        return self._call_llm(messages)


class ApocryphaAgent(BaseSpecialistAgent):
    """Specialist agent for Apocryphal/Deuterocanonical texts interpretation"""
    
    SYSTEM_PROMPT = """Sen uzman bir Apokrifa (Deuterokanonik kitaplar) alimi ve tefsircisisin.
Görevin: Kullanıcının sorusunu, sana verilen Apokrifa ayetlerine dayanarak yorumlamak.

Bu kitaplar şunları içerir: Tobit, Judith, 1-2 Maccabees, Wisdom of Solomon, Sirach (Ecclesiasticus), Baruch, vb.

KRİTİK KURALLAR:
1. SADECE verilen Apokrifa ayetlerindeki bilgileri kullan
2. Her iddiayı [Kitap Bölüm:Ayet] formatında kaynak göster. Örnek: [Wisdom 3:1], [Sirach 2:1]
3. Katolik/Ortodoks tefsir geleneğine uygun yorumla
4. Tek bir bütünlüklü paragraf yaz (3-5 cümle)
5. Cevabın TAMAMI Türkçe olmalı

ÇIKTI FORMATI (JSON):
{
    "commentary": "Apokrifa perspektifinden yorum paragrafı [Wisdom 3:1] şeklinde kaynaklarla...",
    "citations": ["Wisdom 3:1", "Sirach 2:1"],
    "confidence": 0.85
}"""

    def generate(self, query: str, verses: List) -> Dict[str, Any]:
        """Generate Apocrypha commentary paragraph"""
        if not verses:
            return {"commentary": "", "citations": [], "confidence": 0.0}
        
        context = self._format_verses(verses, "bible")
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"SORU: {query}\n\nAPOKRİFA AYETLERİ:\n{context}"}
        ]
        return self._call_llm(messages)


class QuranAgent(BaseSpecialistAgent):
    """Specialist agent for Quran interpretation (İslami tefsir)"""
    
    SYSTEM_PROMPT = """Sen uzman bir İslam Alimi ve Kuran tefsircisisin.
Görevin: Kullanıcının sorusunu, sana verilen Kuran ayetlerine dayanarak yorumlamak.

KRİTİK KURALLAR:
1. SADECE verilen Kuran ayetlerindeki bilgileri kullan
2. Her iddiayı [Sure:Ayet] formatında kaynak göster. Örnek: [Bakara:45], [Fatiha:1-3]
3. Klasik İslami tefsir geleneğine uygun yorumla
4. Tek bir bütünlüklü paragraf yaz (3-5 cümle)
5. Cevabın TAMAMI Türkçe olmalı

ÇIKTI FORMATI (JSON):
{
    "commentary": "Kuran perspektifinden yorum paragrafı [Bakara:45] şeklinde kaynaklarla...",
    "citations": ["Bakara:45", "Bakara:153"],
    "confidence": 0.85
}"""

    def generate(self, query: str, verses: List) -> Dict[str, Any]:
        """Generate Quran commentary paragraph"""
        if not verses:
            return {"commentary": "", "citations": [], "confidence": 0.0}
        
        context = self._format_verses(verses, "quran")
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"SORU: {query}\n\nKURAN AYETLERİ:\n{context}"}
        ]
        return self._call_llm(messages)


class SummaryAgent(BaseSpecialistAgent):
    """Agent for synthesizing all 4 commentaries into a comparative summary"""
    
    SYSTEM_PROMPT = """Sen uzman bir karşılaştırmalı din bilimci ve teologsun.
Görevin: Dört farklı kutsal metin yorumunu sentezleyerek karşılaştırmalı bir özet yazmak.

KRİTİK KURALLAR:
1. Her dört perspektifi (Eski Ahit, Yeni Ahit, Apokrifa, Kuran) dengeli şekilde değerlendir
2. Ortak temaları ve farklılıkları vurgula
3. Teolojik açıdan tarafsız ve saygılı ol
4. Tek bir bütünlüklü paragraf yaz (4-6 cümle)
5. Cevabın TAMAMI Türkçe olmalı
6. Yeni kaynak atıfı yapma, sadece sentez yap

ÇIKTI FORMATI (JSON):
{
    "synthesis": "Dört kutsal metin geleneğinin karşılaştırmalı özeti...",
    "common_themes": ["tema1", "tema2"],
    "key_differences": ["fark1", "fark2"],
    "confidence": 0.85
}"""

    def generate(
        self,
        query: str,
        ot_commentary: str,
        nt_commentary: str,
        apocrypha_commentary: str,
        quran_commentary: str
    ) -> Dict[str, Any]:
        """Generate synthesis paragraph from all 4 commentaries"""
        # Build context from available commentaries
        parts = []
        if ot_commentary:
            parts.append(f"ESKİ AHİT YORUMU:\n{ot_commentary}")
        if nt_commentary:
            parts.append(f"YENİ AHİT YORUMU:\n{nt_commentary}")
        if apocrypha_commentary:
            parts.append(f"APOKRİFA YORUMU:\n{apocrypha_commentary}")
        if quran_commentary:
            parts.append(f"KURAN YORUMU:\n{quran_commentary}")
        
        if not parts:
            return {"synthesis": "", "common_themes": [], "key_differences": [], "confidence": 0.0}
        
        context = "\n\n".join(parts)
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"SORU: {query}\n\n{context}"}
        ]
        return self._call_llm(messages, max_tokens=800)


class MultiAgentOrchestrator:
    """
    Orchestrates 4 parallel specialist agents + 1 summary agent.
    
    Flow:
    1. Split verses by source (OT, NT, Apocrypha, Quran)
    2. Run 4 specialist agents in parallel
    3. Run summary agent on the 4 outputs
    4. Return 5-paragraph result
    """
    
    def __init__(self, api_key: str = None, verbose: bool = True):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.verbose = verbose
        
        # Initialize agents
        self._ot_agent = None
        self._nt_agent = None
        self._apocrypha_agent = None
        self._quran_agent = None
        self._summary_agent = None
    
    @property
    def ot_agent(self) -> OldTestamentAgent:
        if self._ot_agent is None:
            self._ot_agent = OldTestamentAgent(self.api_key)
        return self._ot_agent
    
    @property
    def nt_agent(self) -> NewTestamentAgent:
        if self._nt_agent is None:
            self._nt_agent = NewTestamentAgent(self.api_key)
        return self._nt_agent
    
    @property
    def apocrypha_agent(self) -> ApocryphaAgent:
        if self._apocrypha_agent is None:
            self._apocrypha_agent = ApocryphaAgent(self.api_key)
        return self._apocrypha_agent
    
    @property
    def quran_agent(self) -> QuranAgent:
        if self._quran_agent is None:
            self._quran_agent = QuranAgent(self.api_key)
        return self._quran_agent
    
    @property
    def summary_agent(self) -> SummaryAgent:
        if self._summary_agent is None:
            self._summary_agent = SummaryAgent(self.api_key)
        return self._summary_agent
    
    def _log(self, message: str):
        if self.verbose:
            print(f"[MultiAgent] {message}")
    
    def generate(
        self,
        query: str,
        quran_verses: List,
        ot_verses: List,
        nt_verses: List,
        apocrypha_verses: List
    ) -> MultiAgentAnswer:
        """
        Generate 5-paragraph answer using multi-agent architecture.
        
        Args:
            query: User's question
            quran_verses: Quran search results
            ot_verses: Old Testament search results
            nt_verses: New Testament search results
            apocrypha_verses: Apocrypha search results
            
        Returns:
            MultiAgentAnswer with 5 paragraphs
        """
        self._log(f"Starting multi-agent generation for: {query[:50]}...")
        self._log(f"Verses: OT={len(ot_verses)}, NT={len(nt_verses)}, "
                  f"Apoc={len(apocrypha_verses)}, Quran={len(quran_verses)}")
        
        # Step 1: Run 4 specialist agents in parallel
        results = {}
        
        def run_ot():
            return ("ot", self.ot_agent.generate(query, ot_verses))
        
        def run_nt():
            return ("nt", self.nt_agent.generate(query, nt_verses))
        
        def run_apocrypha():
            return ("apocrypha", self.apocrypha_agent.generate(query, apocrypha_verses))
        
        def run_quran():
            return ("quran", self.quran_agent.generate(query, quran_verses))
        
        self._log("Running 4 specialist agents in parallel...")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(run_ot),
                executor.submit(run_nt),
                executor.submit(run_apocrypha),
                executor.submit(run_quran)
            ]
            
            for future in as_completed(futures):
                key, result = future.result()
                results[key] = result
        
        # Extract commentaries
        ot_result = results.get("ot", {})
        nt_result = results.get("nt", {})
        apoc_result = results.get("apocrypha", {})
        quran_result = results.get("quran", {})
        
        ot_commentary = ot_result.get("commentary", "")
        nt_commentary = nt_result.get("commentary", "")
        apoc_commentary = apoc_result.get("commentary", "")
        quran_commentary = quran_result.get("commentary", "")
        
        self._log(f"Specialist results: OT={len(ot_commentary)}ch, NT={len(nt_commentary)}ch, "
                  f"Apoc={len(apoc_commentary)}ch, Quran={len(quran_commentary)}ch")
        
        # Step 2: Run summary agent
        self._log("Running summary agent...")
        summary_result = self.summary_agent.generate(
            query=query,
            ot_commentary=ot_commentary,
            nt_commentary=nt_commentary,
            apocrypha_commentary=apoc_commentary,
            quran_commentary=quran_commentary
        )
        
        synthesis = summary_result.get("synthesis", "")
        
        # Calculate average confidence
        confidences = [
            ot_result.get("confidence", 0.0),
            nt_result.get("confidence", 0.0),
            apoc_result.get("confidence", 0.0),
            quran_result.get("confidence", 0.0),
            summary_result.get("confidence", 0.0)
        ]
        # Filter out zeros for average
        valid_confidences = [c for c in confidences if c > 0]
        avg_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0
        
        self._log(f"Generation complete. Confidence: {avg_confidence:.0%}")
        
        return MultiAgentAnswer(
            old_testament_commentary=ot_commentary,
            new_testament_commentary=nt_commentary,
            apocrypha_commentary=apoc_commentary,
            quran_commentary=quran_commentary,
            synthesis=synthesis,
            citations={
                "old_testament": ot_result.get("citations", []),
                "new_testament": nt_result.get("citations", []),
                "apocrypha": apoc_result.get("citations", []),
                "quran": quran_result.get("citations", [])
            },
            confidence=avg_confidence,
            query=query,
            verses_provided={
                "old_testament": len(ot_verses),
                "new_testament": len(nt_verses),
                "apocrypha": len(apocrypha_verses),
                "quran": len(quran_verses)
            }
        )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Multi-Agent Answer Generator initialized!")
    print("Agents: OT, NT, Apocrypha, Quran + Summary")
    
    orchestrator = MultiAgentOrchestrator()
    print(f"Orchestrator ready with model: {BaseSpecialistAgent.MODEL}")
