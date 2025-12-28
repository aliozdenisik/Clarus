"""
Semantic Chunking Module

Provides advanced chunking strategies for better context preservation:
1. Sliding Window: Overlapping chunks for narrative continuity
2. Semantic: Group by meaning similarity (embedding-based)
3. Hybrid: Both verse-level and sliding window

Usage:
    from src.semantic_chunker import create_sliding_window_chunks
    
    # For Bible or Quran verses
    chunks = create_sliding_window_chunks(verses, window_size=3, overlap=1)
"""
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class SemanticChunk:
    """A chunk that may contain multiple verses"""
    id: str
    text: str
    verse_range: str  # e.g., "1-3" or "5-7"
    chunk_type: str  # "verse", "sliding_window", "semantic"
    source_verses: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


def create_sliding_window_chunks(
    verses: List[Dict],
    window_size: int = 3,
    overlap: int = 1,
    text_field: str = "translation",
    id_field: str = "verse_id"
) -> List[SemanticChunk]:
    """
    Create overlapping chunks using sliding window.
    
    Each chunk contains multiple verses for better context.
    Overlap ensures no information is lost at chunk boundaries.
    
    Args:
        verses: List of verse dictionaries
        window_size: Number of verses per chunk (default: 3)
        overlap: Number of verses shared between adjacent chunks (default: 1)
        text_field: Field name for text content
        id_field: Field name for verse ID
    
    Returns:
        List of SemanticChunk objects
    
    Example:
        verses = [v1, v2, v3, v4, v5]
        window_size=3, overlap=1
        
        Chunks:
        - [v1, v2, v3]
        - [v3, v4, v5]
    """
    if not verses:
        return []
    
    chunks = []
    step = window_size - overlap
    
    for i in range(0, len(verses), step):
        window = verses[i:i + window_size]
        
        # Skip if window is too small (less than 2 verses)
        if len(window) < 2:
            continue
        
        # Combine text from all verses in window
        combined_text = " ".join([v.get(text_field, v.get("text", "")) for v in window])
        
        # Get verse IDs for range
        first_id = window[0].get(id_field, window[0].get("verse", i))
        last_id = window[-1].get(id_field, window[-1].get("verse", i + len(window) - 1))
        verse_range = f"{first_id}-{last_id}"
        
        # Build metadata from first verse (for surah/book info)
        metadata = {}
        first_verse = window[0]
        for key in ["surah_id", "surah_name", "book_name", "chapter", "testament"]:
            if key in first_verse:
                metadata[key] = first_verse[key]
        
        # Create unique ID
        if "surah_id" in metadata:
            chunk_id = f"quran_sw_{metadata['surah_id']}_{verse_range}"
        elif "book_name" in metadata:
            book = metadata.get("book_name", "").replace(" ", "_").lower()
            chapter = metadata.get("chapter", "")
            chunk_id = f"bible_sw_{book}_{chapter}_{verse_range}"
        else:
            chunk_id = f"chunk_sw_{i}_{verse_range}"
        
        chunk = SemanticChunk(
            id=chunk_id,
            text=combined_text,
            verse_range=verse_range,
            chunk_type="sliding_window",
            source_verses=window,
            metadata=metadata
        )
        chunks.append(chunk)
    
    return chunks


def create_verse_chunks(
    verses: List[Dict],
    text_field: str = "translation"
) -> List[SemanticChunk]:
    """
    Create individual verse chunks (traditional approach).
    
    Each verse becomes one chunk.
    """
    chunks = []
    
    for i, verse in enumerate(verses):
        text = verse.get(text_field, verse.get("text", ""))
        verse_id = verse.get("verse_id", verse.get("verse", i))
        
        metadata = {}
        for key in ["surah_id", "surah_name", "book_name", "chapter", "testament"]:
            if key in verse:
                metadata[key] = verse[key]
        
        if "surah_id" in metadata:
            chunk_id = f"quran_v_{metadata['surah_id']}_{verse_id}"
        elif "book_name" in metadata:
            book = metadata.get("book_name", "").replace(" ", "_").lower()
            chapter = metadata.get("chapter", "")
            chunk_id = f"bible_v_{book}_{chapter}_{verse_id}"
        else:
            chunk_id = f"chunk_v_{i}"
        
        chunk = SemanticChunk(
            id=chunk_id,
            text=text,
            verse_range=str(verse_id),
            chunk_type="verse",
            source_verses=[verse],
            metadata=metadata
        )
        chunks.append(chunk)
    
    return chunks


def create_hybrid_chunks(
    verses: List[Dict],
    window_size: int = 3,
    overlap: int = 1,
    text_field: str = "translation"
) -> List[SemanticChunk]:
    """
    Create both verse-level and sliding window chunks.
    
    This is the recommended approach:
    - Verse chunks: Good for exact matching and keyword search
    - Sliding window: Good for context-dependent queries
    
    Returns:
        Combined list of verse + sliding window chunks
    """
    verse_chunks = create_verse_chunks(verses, text_field)
    sliding_chunks = create_sliding_window_chunks(
        verses, 
        window_size=window_size, 
        overlap=overlap,
        text_field=text_field
    )
    
    return verse_chunks + sliding_chunks


# Helper function to convert SemanticChunk to dict for indexing
def chunk_to_payload(chunk: SemanticChunk) -> Dict:
    """Convert SemanticChunk to payload dict for Qdrant indexing"""
    payload = {
        "id": chunk.id,
        "text": chunk.text,
        "verse_range": chunk.verse_range,
        "chunk_type": chunk.chunk_type,
        **chunk.metadata
    }
    return payload


if __name__ == "__main__":
    # Test with sample verses
    sample_verses = [
        {"verse_id": 1, "translation": "Bismillahirrahmanirrahim", "surah_id": 1, "surah_name": "Fatiha"},
        {"verse_id": 2, "translation": "Hamd alemlerin Rabbi Allah'a mahsustur", "surah_id": 1, "surah_name": "Fatiha"},
        {"verse_id": 3, "translation": "Rahman ve Rahim olan", "surah_id": 1, "surah_name": "Fatiha"},
        {"verse_id": 4, "translation": "Din gününün maliki", "surah_id": 1, "surah_name": "Fatiha"},
        {"verse_id": 5, "translation": "Ancak sana kulluk eder, ancak senden yardım dileriz", "surah_id": 1, "surah_name": "Fatiha"},
    ]
    
    print("=== Verse Chunks ===")
    verse_chunks = create_verse_chunks(sample_verses)
    for c in verse_chunks:
        print(f"{c.id}: {c.text[:50]}...")
    
    print("\n=== Sliding Window Chunks ===")
    sliding_chunks = create_sliding_window_chunks(sample_verses, window_size=3, overlap=1)
    for c in sliding_chunks:
        print(f"{c.id} (verses {c.verse_range}): {c.text[:60]}...")
    
    print("\n=== Hybrid Chunks ===")
    hybrid_chunks = create_hybrid_chunks(sample_verses)
    print(f"Total: {len(hybrid_chunks)} chunks ({len(verse_chunks)} verse + {len(sliding_chunks)} sliding)")
