import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"