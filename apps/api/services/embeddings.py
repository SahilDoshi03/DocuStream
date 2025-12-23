from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self):
        # Load the model. 'all-MiniLM-L6-v2' is a good balance of speed and performance.
        # It produces 384-dimensional embeddings.
        print("Loading Embedding Model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding Model Loaded.")

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text string."""
        return self.model.encode(text).tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text strings."""
        return self.model.encode(texts).tolist()

# Singleton instance
embedding_service = EmbeddingService()
