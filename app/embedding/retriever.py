import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Dict

class SemanticRetriever:
    """Semantic search module using Faiss and SentenceTransformer."""

    def __init__(self,
                 index_path: str = "embedding/faiss_index/qol_vector.index",
                 metadata_path: str = "embedding/faiss_index/metadata.pkl",
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata: List[Dict] = []
        self.load_index(index_path, metadata_path)

    def load_index(self, index_path: str, metadata_path: str):
        """Load Faiss index and metadata."""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"Index loaded with {len(self.metadata)} documents.")

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for the most relevant documents."""
        if self.index is None:
            raise ValueError("Index not loaded.")

        query_vector = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1 or idx >= len(self.metadata):
                continue
            result = {
                "content": self.metadata[idx]["content"],
                "score": float(1 / (1 + dist)),  # Convert L2 distance to similarity score
                "metadata": self.metadata[idx],
                "rank": rank + 1
            }
            results.append(result)
        return results

    async def add_document(self, document: Dict):
        """Add a new document to the current index (memory only, not auto-save)."""
        if self.index is None:
            raise ValueError("Index not loaded.")
        embedding = self.model.encode([document["content"]]).astype("float32")
        self.index.add(embedding)
        self.metadata.append(document)
        print("Document added. Remember to save the index afterwards.")
