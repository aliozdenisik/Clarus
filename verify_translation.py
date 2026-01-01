import sys
sys.path.insert(0, '.')
from src.ultimate_rag import UltimateRAG
from dotenv import load_dotenv
import time

load_dotenv()

def main():
    print("Initializing RAG...")
    # Initialize RAG with verbose=True to see translation logs
    rag = UltimateRAG(verbose=True)
    
    queries = [
        "Tanrı dünyayı o kadar çok sevdi ki",  # John 3:16
        "İsa'nın dağdaki vaazı",               # Sermon on the Mount
        "Davut'un mezmuru Rab çobanımdır"      # Psalm 23
    ]
    
    print("\n--- Verifying Translation and Search ---")
    for q in queries:
        print(f"\nQUERY (TR): {q}")
        try:
            # search_bible automatically translates Turkish queries to English
            results = rag.search_bible(q, translation="kjva", top_k=1)
            
            if results:
                r = results[0]
                # Handle different result attributes safely
                text = getattr(r, 'text', getattr(r, 'content', str(r)))
                book = getattr(r, 'book_name', 'Unknown')
                chapter = getattr(r, 'chapter', '?')
                verse = getattr(r, 'verse', '?')
                score = getattr(r, 'score', 0.0)
                
                print(f"TOP RESULT: {book} {chapter}:{verse}")
                print(f"TEXT: {text[:100]}...")
                print(f"SCORE: {score:.3f}")
            else:
                print("NO RESULTS")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
