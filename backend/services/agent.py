from .file_parser import FileParser
from .embeddings import EmbeddingService
from .retriever import VectorStore
from .llm import LLMService
import os

class Orchestrator:
    def __init__(self):
        self.file_parser = FileParser()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    async def process_file(self, file_path: str):
        # 1. Extract text
        text = self.file_parser.extract_text(file_path)
        clean_text = self.file_parser.clean_text(text)
        
        # 2. Chunk text
        chunks = self.embedding_service.chunk_text(clean_text)
        
        # 3. Generate embeddings
        if chunks:
            embeddings = self.embedding_service.get_embeddings(chunks)
            
            # 4. Store in FAISS
            self.vector_store.add_texts(chunks, embeddings)
            
        return {"status": "success", "chunks_processed": len(chunks)}

    async def analyze_query(self, query: str):
        # 1. Generate query embedding
        query_embedding = self.embedding_service.get_embeddings([query])
        
        # 2. Retrieve relevant context
        context_chunks = self.vector_store.search(query_embedding)
        context = "\n---\n".join(context_chunks)
        
        # 3. Generate response from LLM
        response = self.llm_service.generate_response(query, context)
        
        return {
            "query": query,
            "response": response,
            "has_context": len(context_chunks) > 0
        }
        
    def clear_history(self):
        self.vector_store.clear()
