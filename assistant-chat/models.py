from sentence_transformers import SentenceTransformer
from transformers import pipeline
import faiss
import numpy as np
from langchain_groq import ChatGroq
from datasets import load_dataset
from config import GROQ_API_KEY, MODEL_NAME, LOAD_EMBEDDINGS

# Load the sentence transformer model for embeddings
embedding_model = SentenceTransformer(MODEL_NAME)

recipe_docs = []  # Initialize the list of documents
embeddings = np.empty((0, embedding_model.get_sentence_embedding_dimension()), dtype="float32") # Initialize empty embeddings

if LOAD_EMBEDDINGS:
    # Load all-recipes dataset
    recipes = load_dataset("corbt/all-recipes", split="train", trust_remote_code=True)
    
    # Split the input into sections: title, ingredients, and directions
    recipe_texts = []
    for item in recipes:
        recipe = item["input"].lower()
        parts = recipe.split("\n\n")
        if len(parts) >= 3:
            title = parts[0]
            ingredients = parts[1].replace("Ingredients:\n", "").strip()
            directions = parts[2].replace("Directions:\n", "").strip()
            recipe_texts.append(f"Title: {title} - Ingredients: {ingredients} - Directions: {directions}")
    print(f"Processed {len(recipe_texts)} recipes successfully!")

    # Split the recipes into documents
    recipe_docs = [Document(page_content=recipe) for recipe in recipe_texts]

    # Compute the embeddings
    embeddings = embedding_model.encode(recipe_texts)

# Create a FAISS index if embeddings have been loaded/populated
if embeddings.shape[0] > 0:
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
else:
    index = None

# Initialize the Groq LLM
groq_chat = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name='llama3-8b-8192'
)
