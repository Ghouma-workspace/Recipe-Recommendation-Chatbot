# retrieval.py
import numpy as np
from models import embedding_model, index, recipe_docs

def retriever(query: str, k: int = 1):
    """
    Retrieve the top-k most similar documents for a given query.
    """
    if index is None:
        print("The FAISS index has not been initialized with embeddings.")
        return []
    else:    
        # Encode the query into an embedding
        query_embedding = embedding_model.encode([query])
        
        # Search the FAISS index
        distances, indices = index.search(np.array(query_embedding), k=k)
        
        # Return the top-k results
        results = [recipe_docs[i] for i in indices[0] if i < len(recipe_docs)]
        return results
