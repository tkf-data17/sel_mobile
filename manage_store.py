from config import *
import json
from typing import List, Dict, Optional
import numpy as np
import faiss
import logging
import pickle
import os
from mistralai.client import Mistral

# Configure logging
logging.basicConfig(level=logging.INFO)

class VectorStoreManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance.index = None
            cls._instance.chunks = None
            cls._instance.mistral_client = None
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the Mistral client and try to load data."""
        if MISTRAL_API_KEY:
            self.mistral_client = Mistral(api_key=MISTRAL_API_KEY)
        else:
            logging.error("MISTRAL_API_KEY is missing in config.")
        
        # Initial load attempt
        self.load_data()

    def load_data(self):
        """Load the FAISS index and chunks from disk if they exist."""
        # Only load if not already loaded to avoid redundant IO
        if self.index is not None and self.chunks is not None:
            return

        if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(DOCUMENT_CHUNKS_FILE):
            try:
                logging.info(f"Loading FAISS index from {FAISS_INDEX_FILE}...")
                self.index = faiss.read_index(FAISS_INDEX_FILE)
                
                logging.info(f"Loading chunks from {DOCUMENT_CHUNKS_FILE}...")
                with open(DOCUMENT_CHUNKS_FILE, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                logging.info(f"Data loaded successfully. {len(self.chunks)} chunks loaded.")
            except Exception as e:
                logging.error(f"Error loading data: {e}")
                self.index = None
                self.chunks = None
        else:
            logging.warning("Index or chunks file not found. Please ensure data is indexed.")

    def _generate_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """Generate embeddings using Mistral API."""
        if not self.mistral_client:
            logging.error("Mistral client not initialized.")
            return None

        all_embeddings = []
        # Calculate batches
        total_batches = (len(texts) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE

        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch_texts = texts[i:i + EMBEDDING_BATCH_SIZE]
            try:
                # logging.info(f"Generating embeddings batch {i//EMBEDDING_BATCH_SIZE + 1}/{total_batches}")
                response = self.mistral_client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    inputs=batch_texts
                )
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logging.error(f"Error generating embeddings for batch {i//EMBEDDING_BATCH_SIZE + 1}: {e}")
        
        if not all_embeddings:
            return None
            
        embeddings_array = np.array(all_embeddings).astype('float32')
        return embeddings_array

    def build_index(self, chunks_path: str = None):
        """Build the FAISS index from the chunks JSON file."""
        path_to_load = chunks_path if chunks_path else ALL_CHUNKS_PATH
        logging.info(f"Building index from {path_to_load}...")
        
        # Load chunks from JSON
        try:
             with open(path_to_load, "r", encoding="utf-8") as f:
                chunks = json.load(f)
        except Exception as e:
            logging.error(f"Error loading chunks JSON: {e}")
            return None, None

        if not chunks:
            logging.warning("No chunks found in JSON.")
            return None, None

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self._generate_embeddings(texts)
        
        if embeddings is None:
            logging.error("Failed to generate embeddings.")
            return None, None

        dimension = embeddings.shape[1]
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        
        # Update internal state
        self.index = index
        self.chunks = chunks
        
        # Save to disk
        try:
            logging.info(f"Saving index to {FAISS_INDEX_FILE}...")
            faiss.write_index(index, FAISS_INDEX_FILE)
            logging.info(f"Saving chunks to {DOCUMENT_CHUNKS_FILE}...")
            with open(DOCUMENT_CHUNKS_FILE, 'wb') as f:
                pickle.dump(chunks, f)
            logging.info("Index and chunks saved successfully.")
        except Exception as e:
            logging.error(f"Error saving index/chunks: {e}")

        return index, chunks

    def search(self, query_text: str, k: int = 5, min_score: float = None) -> List[Dict[str, any]]:
        """Search for relevant chunks."""
        # Ensure data is loaded
        if self.index is None or self.chunks is None:
            self.load_data()
            if self.index is None or self.chunks is None:
                logging.warning("Search impossible: Index not loaded.")
                return []

        if not self.mistral_client:
             logging.error("Search impossible: Mistral client not initialized.")
             return []

        # logging.info(f"Searching for: '{query_text}'")
        try:
            # Generate query embedding
            response = self.mistral_client.embeddings.create(
                model=EMBEDDING_MODEL,
                inputs=[query_text]
            )
            query_embedding = np.array([response.data[0].embedding]).astype('float32')
            faiss.normalize_L2(query_embedding)

            # Search
            search_k = k * 3 if min_score is not None else k
            scores, indices = self.index.search(query_embedding, search_k)

            results = []
            if indices.size > 0:
                for i, idx in enumerate(indices[0]):
                    if 0 <= idx < len(self.chunks):
                        chunk = self.chunks[idx]
                        raw_score = float(scores[0][i])
                        similarity = raw_score * 100
                        
                        min_score_percent = min_score * 100 if min_score is not None else 0
                        
                        if min_score is not None and similarity < min_score_percent:
                            # logging.debug(f"Result filtered: score {similarity} < {min_score_percent}")
                            continue

                        results.append({
                            "score": similarity,
                            "raw_score": raw_score,
                            "text": chunk["text"],
                            "metadata": chunk.get("metadata", {})
                        })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:k]

        except Exception as e:
            logging.error(f"Error during search: {e}")
            return []

# Helper function to access the singleton
def get_store_manager():
    return VectorStoreManager()
