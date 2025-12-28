from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url="http://localhost:6333")
print(f"QdrantClient methods: {[m for m in dir(client) if not m.startswith('_')]}")

try:
    cols = client.get_collections()
    print(f"Collections: {[c.name for c in cols.collections]}")
    
    # Check if search exists
    if hasattr(client, 'search'):
        print("client.search exists")
    else:
        print("client.search DOES NOT exist")
        
    # Check if query_points exists
    if hasattr(client, 'query_points'):
        print("client.query_points exists")
    else:
        print("client.query_points DOES NOT exist")
except Exception as e:
    print(f"Error connecting: {e}")
