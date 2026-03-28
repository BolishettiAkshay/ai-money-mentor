from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        # Simple word-based chunking
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
                
        return chunks
