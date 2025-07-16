import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from typing import List, Dict

class IndexBuilder:
    """Faiss index builder for semantic search"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.metadata: List[Dict] = []

    def build_index(self, documents: List[Dict]) -> None:
        """Build Faiss index from given documents"""
        texts = [doc["content"] for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype("float32"))
        self.metadata = documents
        print(f"Index built successfully with {len(documents)} documents.")

    def add_to_index(self, new_documents: List[Dict]) -> None:
        """Add new documents to an existing index"""
        if self.index is None:
            raise ValueError("Please build or load an index first.")

        texts = [doc["content"] for doc in new_documents]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(new_documents)
        print(f"Added {len(new_documents)} new documents to the index.")

    def save_index(self, index_path: str, metadata_path: str) -> None:
        """Save Faiss index and metadata"""
        if self.index is None:
            raise ValueError("No index to save.")
        faiss.write_index(self.index, index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"Index saved to {index_path} and metadata saved to {metadata_path}.")

    def load_index(self, index_path: str, metadata_path: str) -> None:
        """Load Faiss index and metadata"""
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Index or metadata file not found.")
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"Index loaded with {len(self.metadata)} documents.")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search similar documents by query text"""
        if self.index is None:
            raise ValueError("Index not built or loaded.")
        query_vec = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vec, top_k)
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["score"] = float(score)
                results.append(result)
        return results

    def load_documents(self, docs_dir: str) -> List[Dict]:
        """Load documents from a directory (txt/md files)"""
        documents = []
        for filename in os.listdir(docs_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = self.split_text(content)
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "id": f"{filename}_{i}",
                        "content": chunk,
                        "source": filename,
                        "chunk_index": i
                    })
        return documents

    def split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks, current_chunk = [], ""
        sentences = text.replace("\n", " ").split("。")
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + "。"
            else:
                chunks.append(current_chunk)
                current_chunk = current_chunk[-overlap:] + sentence + "。"
        if current_chunk:
            chunks.append(current_chunk)
        return chunks
