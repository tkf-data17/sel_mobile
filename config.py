import os
from dotenv import load_dotenv
from mistralai.client import MistralClient

load_dotenv()  # Charge les variables depuis .env

VECTOR_DB_DIR = "VECTOR_DB"
ALL_CHUNKS_PATH = "save_chunks/chunks_save.json" # Corrected path
FAISS_INDEX_FILE = os.path.join(VECTOR_DB_DIR, "faiss_index.idx")
DOCUMENT_CHUNKS_FILE = os.path.join(VECTOR_DB_DIR, "document_chunks.pkl")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
mistral_client = MistralClient(api_key = MISTRAL_API_KEY)
EMBEDDING_MODEL    = "mistral-embed"
EMBEDDING_BATCH_SIZE = 32
LLM_MODEL = "mistral-small"
IMAGE_PATH = "Armoiries_du_Togo.png"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_mistral_client():
    if not MISTRAL_API_KEY:
        print("Erreur: La clé API Mistral (MISTRAL_API_KEY) n'est pas configurée.")
    return MistralClient(api_key=MISTRAL_API_KEY)
