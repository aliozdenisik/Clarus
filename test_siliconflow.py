
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SILICONFLOW_API_KEY")
url = "https://api.siliconflow.com/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

print(f"Listing models from: {url}")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json().get("data", [])
        rerankers = [m["id"] for m in models if "rerank" in m["id"].lower()]
        print(f"Found {len(rerankers)} rerankers:")
        for r in rerankers:
            print(f" - {r}")
        
        # Also print all models just in case
        if not rerankers:
            print("All models:")
            for m in models:
                print(f" - {m['id']}")
    else:
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
