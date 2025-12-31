from typing import List, Dict
from sqlalchemy import select
from langchain_huggingface import HuggingFaceEmbeddings
from database import SessionLocal, DocumentChunk

class VectorStore:
    def __init__(self, dimension=384):
        self.dimension = dimension
        # Initialize embedding model locally
        # Using all-MiniLM-L6-v2 which creates 384-dim embeddings
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def add_documents(self, documents: List[Dict]):
        """
        Add documents to the store.
        documents: List of dicts, each must have 'text' and 'metadata'.
        """
        if not documents:
            return

        texts = [doc['text'] for doc in documents]
        # Generate embeddings using the local model
        embeddings = self.embedding_model.embed_documents(texts)
        
        db = SessionLocal()
        try:
            chunks = []
            for i, doc in enumerate(documents):
                chunk = DocumentChunk(
                    text=doc['text'],
                    metadata_=doc.get('metadata', {}),
                    embedding=embeddings[i]
                )
                chunks.append(chunk)
            
            db.add_all(chunks)
            db.commit()
            print(f"Added {len(chunks)} documents to Postgres vector store.")
        except Exception as e:
            print(f"Error adding documents: {e}")
            db.rollback()
        finally:
            db.close()

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for most similar documents.
        Returns list of dicts with 'text', 'metadata', and 'score'.
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        
        db = SessionLocal()
        try:
            # L2 distance (Euclidean distance) -> smaller is better
            stmt = select(DocumentChunk).order_by(
                DocumentChunk.embedding.l2_distance(query_embedding)
            ).limit(k)
            
            results = db.execute(stmt).scalars().all()
            
            output = []
            for chunk in results:
                output.append({
                    "text": chunk.text,
                    **chunk.metadata_
                })
            
            return output
        finally:
            db.close()

# Singleton
vector_store = VectorStore()
