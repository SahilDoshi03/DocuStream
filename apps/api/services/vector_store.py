import faiss
import pickle
import os
import numpy as np
from typing import List, Dict, Tuple
from langchain_huggingface import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self, index_path="faiss_index.bin", metadata_path="faiss_metadata.pkl", dimension=384):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = dimension
        self.embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

        
        # Initialize FAISS index
        # IndexFlatL2 is efficient for small-medium datasets. 
        # For larger datasets, we might want IndexIVFFlat.
        self.index = faiss.IndexFlatL2(dimension)
        
        # Metadata storage: Maps ID (int) -> dict
        self.metadata: Dict[int, Dict] = {}
        
        self.load_local()

    def add_documents(self, documents: List[Dict]):
        """
        Add documents to the store.
        documents: List of dicts, each must have 'text' and 'metadata'.
        """
        if not documents:
            return

        texts = [doc['text'] for doc in documents]
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Convert to numpy float32 array for FAISS
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Add to index
        start_id = self.index.ntotal
        self.index.add(embeddings_np)
        
        # Store metadata
        for i, doc in enumerate(documents):
            self.metadata[start_id + i] = {
                "text": doc['text'],
                **doc.get('metadata', {})
            }
            
        self.save_local()

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for most similar documents.
        Returns list of dicts with 'text', 'metadata', and 'score'.
        """
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedding_model.embed_query(query)
        query_np = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_np, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.metadata:
                results.append({
                    **self.metadata[idx],
                    "score": float(distances[0][i])
                })
        
        return results

    def save_local(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"VectorStore saved to {self.index_path}")

    def load_local(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"VectorStore loaded from {self.index_path} with {self.index.ntotal} vectors")
        else:
            print("Initialized new VectorStore")

# Singleton
vector_store = VectorStore()
