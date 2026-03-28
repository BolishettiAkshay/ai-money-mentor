import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple

class VectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "db/vector_store"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []
        
        # Load existing index if it exists
        if os.path.exists(f"{index_path}.index"):
            self.load()

    def add_texts(self, texts: List[str], embeddings: np.ndarray):
        if len(texts) == 0:
            return
        
        self.index.add(embeddings.astype('float32'))
        self.texts.extend(texts)
        self.save()

    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            return []
            
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.texts):
                results.append(self.texts[idx])
        return results

    def save(self):
        if not os.path.exists("db"):
            os.makedirs("db")
        faiss.write_index(self.index, f"{self.index_path}.index")
        with open(f"{self.index_path}.texts", "wb") as f:
            pickle.dump(self.texts, f)

    def load(self):
        self.index = faiss.read_index(f"{self.index_path}.index")
        with open(f"{self.index_path}.texts", "rb") as f:
            self.texts = pickle.load(f)
            
    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts = []
        if os.path.exists(f"{self.index_path}.index"):
            os.remove(f"{self.index_path}.index")
        if os.path.exists(f"{self.index_path}.texts"):
            os.remove(f"{self.index_path}.texts")
