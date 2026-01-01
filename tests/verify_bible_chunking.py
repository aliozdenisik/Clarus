
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.bible_loader import BibleDataLoader
from src.bible_semantic_chunker import BibleSemanticVerseChunker
from src.indexer import BibleSemanticChunkIndexer
from src.search import BibleSemanticChunkSearcher

def verify_chunking():
    print("1. Loading Bible data...")
    loader = BibleDataLoader(translation="kjva")
    all_verses = loader.create_chunks(show_progress=False)
    
    # Take first 200 verses (Genesis)
    subset = all_verses[:200]
    print(f"   Loaded {len(subset)} verses for testing.")
    
    print("\n2. Creating semantic chunks (subset)...")
    chunker = BibleSemanticVerseChunker(
        translation="kjva",
        similarity_threshold=0.75,
        max_chunk_size=10
    )
    
    # Force recompute to avoid using full bible cache if exists
    chunks = chunker.create_semantic_chunks(verses=subset, show_progress=True, use_cache=False)
    
    print(f"   Created {len(chunks)} chunks.")
    for i, c in enumerate(chunks[:3]):
        print(f"   Chunk {i}: {c.book_name} {c.chapter}:{c.start_verse}-{c.end_verse} ({c.verse_count}v)")
    
    print("\n3. Indexing chunks (test collection)...")
    indexer = BibleSemanticChunkIndexer(translation="kjva_test") # Use test translation name to avoid conflicts
    indexer.create_collection(recreate=True)
    indexer.index_chunks(chunks, show_progress=True)
    
    print("\n4. Searching chunks...")
    searcher = BibleSemanticChunkSearcher(translation="kjva_test")
    
    query = "light and darkness"
    print(f"   Query: '{query}'")
    results = searcher.search(query, limit=3)
    
    for i, r in enumerate(results):
        print(f"   {i+1}. [{r.book_name} {r.chapter}:{r.start_verse}-{r.end_verse}] {r.text[:100]}... (Score: {r.score:.4f})")
    
    if len(results) > 0:
        print("\n[SUCCESS] Bible Semantic Chunking verification passed!")
    else:
        print("\n[FAILURE] No results found.")

if __name__ == "__main__":
    verify_chunking()
