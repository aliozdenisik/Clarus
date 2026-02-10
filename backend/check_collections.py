import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from qdrant_client import QdrantClient


def check_collections():
    try:
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        print(f"Found {len(collections.collections)} collections:")
        for col in collections.collections:
            info = client.get_collection(col.name)
            print(f"- {col.name}: {info.points_count} points, status: {info.status}")
    except Exception as e:
        print(f"Error accessing Qdrant: {e}")


if __name__ == "__main__":
    check_collections()
