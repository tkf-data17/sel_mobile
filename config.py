import os
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()  # Charge les variables depuis .env

VECTOR_DB_DIR = "VECTOR_DB"
ALL_CHUNKS_PATH = "save_chunks/chunks_save.json" # Corrected path
FAISS_INDEX_FILE = os.path.join(VECTOR_DB_DIR, "faiss_index.idx")
DOCUMENT_CHUNKS_FILE = os.path.join(VECTOR_DB_DIR, "document_chunks.pkl")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None
EMBEDDING_MODEL    = "mistral-embed" #"sentence-transformers/all-mpnet-base-v2"
EMBEDDING_BATCH_SIZE = 32
LLM_MODEL = "mistral-7B"
IMAGE_PATH = "Armoiries_du_Togo.png"



def get_mistral_client():
    if not MISTRAL_API_KEY:
        print("Erreur: La clé API Mistral (MISTRAL_API_KEY) n'est pas configurée.")
    return Mistral(api_key=MISTRAL_API_KEY)
