# models.py
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import faiss
import numpy as np
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, MODEL_NAME

# Load the sentence transformer model for embeddings
embedding_model = SentenceTransformer(MODEL_NAME)

recipe_docs = []  # list of Document objects
embeddings = np.empty((0, embedding_model.get_sentence_embedding_dimension()), dtype="float32")

# Create a FAISS index if embeddings have been loaded/populated
if embeddings.shape[0] > 0:
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
else:
    index = None

# Initialize the Groq chat object (for LLM generation)
groq_chat = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name='llama3-8b-8192'
)
