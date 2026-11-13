import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
from groq import Groq


load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        ".env"
    )
)


DATABASE_URL = os.getenv("DATABASE_URL")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Existing LLM client used by your RAG system
llm_client = InferenceClient(
    api_key=GROQ_API_KEY,
    provider="groq"
)


# Groq client used by Prompt Guard
groq_client = Groq(
    api_key=GROQ_API_KEY
)


LLM_MODEL = "openai/gpt-oss-120b"


# Embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)