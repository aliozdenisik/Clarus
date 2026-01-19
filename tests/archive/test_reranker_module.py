
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.getcwd())

load_dotenv()

from src.reranker import Reranker

print("Initializing Reranker...")
reranker = Reranker()
print(f"Model: {reranker.model_name}")
print(f"API URL: {reranker.API_URL}")

query = "Apple"
docs = [
    type('obj', (object,), {'text': 'Apple is a tasty fruit', 'score': 0.5})(),
    type('obj', (object,), {'text': 'Apple is a technology company', 'score': 0.4})(),
    type('obj', (object,), {'text': 'Oranges are citrus', 'score': 0.1})()
]

print("\nReranking...")
try:
    results = reranker.rerank(query, docs, top_k=2)
    print(f"Success! Got {len(results)} results.")
    for i, r in enumerate(results):
        print(f"{i+1}. {r.text} (Score: {r.score})")
except Exception as e:
    print(f"Reranking failed: {e}")
