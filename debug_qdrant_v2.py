from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(url="http://localhost:6333")
methods = [m for m in dir(client) if not m.startswith('_')]

with open("qdrant_debug_output.txt", "w") as f:
    f.write(f"QdrantClient methods: {methods}\n")
    try:
        cols = client.get_collections()
        f.write(f"Collections: {[c.name for c in cols.collections]}\n")
        
        if hasattr(client, 'search'):
            f.write("client.search exists\n")
        else:
            f.write("client.search DOES NOT exist\n")
            
        if hasattr(client, 'query_points'):
            f.write("client.query_points exists\n")
        else:
            f.write("client.query_points DOES NOT exist\n")
    except Exception as e:
        f.write(f"Error connecting: {e}\n")
