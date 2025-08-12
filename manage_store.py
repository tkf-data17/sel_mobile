from config import *
import json
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
import logging
import pickle

# FONCTION POUR RECHARCHER LES CHUNKS
def load_all_chunks(CHUNKS_PATH):

  # Lire le fichier JSON et charger les données
  with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
      chunks_recharges = json.load(f)

  # Vérification
  print(f"{len(chunks_recharges)} chunks ont été rechargés avec succès.")
  return chunks_recharges

# FONCTION POUR GENERER LES EMBEDDINGS

def _generate_embeddings(chunks: List[Dict[str, any]], mistral_client) -> Optional[np.ndarray]:
        """Génère les embeddings pour une liste de chunks via l'API Mistral."""

        # logging.info(f"Génération des embeddings pour {len(chunks)} chunks (modèle: {EMBEDDING_MODEL})...")
        all_embeddings = []
        total_batches = (len(chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE

        for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
            batch_num = (i // EMBEDDING_BATCH_SIZE) + 1
            batch_chunks = chunks[i:i + EMBEDDING_BATCH_SIZE]
            texts_to_embed = [chunk["text"] for chunk in batch_chunks]
            # logging.info(f"  Traitement du lot {batch_num}/{total_batches} ({len(texts_to_embed)} chunks)")
            try:
                response = mistral_client.embeddings(
                    model=EMBEDDING_MODEL,
                    input=texts_to_embed
                )
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)

            except Exception as e:
              pass
                # logging.error(f"Erreur inattendue lors de la génération d'embeddings (lot {batch_num}): {e}")

        if not all_embeddings:
            #  logging.error("Aucun embedding n'a put être généré.")
             return None

        embeddings_array = np.array(all_embeddings).astype('float32')
        # logging.info(f"Embeddings générés avec succès. Shape: {embeddings_array.shape}")
        print(f"Embeddings générés avec succès. Shape: {embeddings_array.shape}")
        return embeddings_array


# FONCTION POUR CONSTRUIRE L'INDEX FAISS A PARTIR DE DOCUMENTS

def build_index(ALL_CHUNKS_PATH):
      """Construit l'index Faiss à partir des documents."""

      chunks = load_all_chunks(ALL_CHUNKS_PATH)
      if not chunks:
          logging.warning("Aucun document fourni pour construire l'index.")
          return
      # 2. Générer les embeddings
      embeddings =_generate_embeddings(chunks, mistral_client)
      if embeddings is None:
          logging.error("Aucun embedding n'a pu être généré. L'index ne peut pas être construit.")
          return

      # 3. Créer l'index Faiss optimisé pour la similarité cosinus
      dimension = embeddings.shape[1]
      logging.info(f"Création de l'index Faiss optimisé pour la similarité cosinus avec dimension {dimension}...")
      # Normaliser les embeddings pour la similarité cosinus
      faiss.normalize_L2(embeddings)

      # Créer un index pour la similarité cosinus (IndexFlatIP = produit scalaire)
      index = faiss.IndexFlatIP(dimension)
      index.add(embeddings)
      logging.info(f"Index Faiss créé avec {index.ntotal} vecteurs.")

      # 4. Sauvegarder l'index et les chunks
      try:
          logging.info(f"Sauvegarde de l'index Faiss dans {FAISS_INDEX_FILE}...")
          faiss.write_index(index, FAISS_INDEX_FILE)
          logging.info(f"Sauvegarde des chunks dans {DOCUMENT_CHUNKS_FILE}...")
          with open(DOCUMENT_CHUNKS_FILE, 'wb') as f:
              pickle.dump(chunks, f)
          logging.info("Index et chunks sauvegardés avec succès.")
          print("Index et chunks sauvegardés avec succès.")
      except Exception as e:
          logging.error(f"Erreur lors de la sauvegarde de l'index/chunks: {e}")

      return index, chunks


# FONCTION POUR RECHERCHER DANS LA BASE DE RECHERCHE

def search(query_text: str, k: int = 5, min_score: float = None) -> List[Dict[str, any]]:
        """
        Recherche les k chunks les plus pertinents pour une requête.

        Args:
            query_text: Texte de la requête
            k: Nombre de résultats à retourner
            min_score: Score minimum (entre 0 et 1) pour inclure un résultat

        Returns:
            Liste des chunks pertinents avec leurs scores
        """
        # chargement des index
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(DOCUMENT_CHUNKS_FILE, 'rb') as f:
            chunks = pickle.load(f)

        if index is None or not chunks:
            logging.warning("Recherche impossible: l'index Faiss n'est pas chargé ou est vide.")
            return []
        if not MISTRAL_API_KEY:
             logging.error("Recherche impossible: MISTRAL_API_KEY manquante pour générer l'embedding de la requête.")
             return []

        logging.info(f"Recherche des {k} chunks les plus pertinents pour: '{query_text}'")
        try:
            # 1. Générer l'embedding de la requête
            response = mistral_client.embeddings(
                model=EMBEDDING_MODEL,
                input=[query_text] # La requête doit être une liste
            )
            query_embedding = np.array([response.data[0].embedding]).astype('float32')

            # Normaliser l'embedding de la requête pour la similarité cosinus
            faiss.normalize_L2(query_embedding)

            # 2. Rechercher dans l'index Faiss
            # Pour IndexFlatIP: scores = produit scalaire (plus grand = meilleur)
            # indices: index des chunks correspondants dans chunks
            # Demander plus de résultats si un score minimum est spécifié
            search_k = k * 3 if min_score is not None else k
            scores, indices = index.search(query_embedding, search_k)

            # 3. Formater les résultats
            results = []
            if indices.size > 0: # Vérifier s'il y a des résultats
                for i, idx in enumerate(indices[0]):
                    if 0 <= idx < len(chunks): # Vérifier la validité de l'index
                        chunk = chunks[idx]
                        # Convertir le score en similarité (0-1)
                        # Pour IndexFlatIP avec vecteurs normalisés, le score est déjà entre -1 et 1
                        # On le convertit en pourcentage (0-100%)
                        raw_score = float(scores[0][i])
                        similarity = raw_score * 100

                        # Filtrer les résultats en fonction du score minimum
                        # Le min_score est entre 0 et 1, mais similarity est en pourcentage (0-100)
                        min_score_percent = min_score * 100 if min_score is not None else 0
                        if min_score is not None and similarity < min_score_percent:
                            logging.debug(f"Document filtré (score {similarity:.2f}% < minimum {min_score_percent:.2f}%)")
                            continue

                        results.append({
                            "score": similarity, # Score de similarité en pourcentage
                            "raw_score": raw_score, # Score brut pour débogage
                            "text": chunk["text"],
                            "metadata": chunk["metadata"] # Contient source, category, chunk_id_in_doc, start_index etc.
                        })
                    else:
                        logging.warning(f"Index Faiss {idx} hors limites (taille des chunks: {len(chunks)}).")

            # Trier par score (similarité la plus élevée en premier)
            results.sort(key=lambda x: x["score"], reverse=True)

            # Limiter au nombre demandé (k) si nécessaire
            if len(results) > k:
                results = results[:k]

            if min_score is not None:
                min_score_percent = min_score * 100
                logging.info(f"{len(results)} chunks pertinents trouvés (score minimum: {min_score_percent:.2f}%).")
            else:
                logging.info(f"{len(results)} chunks pertinents trouvés.")

            return results

        except Exception as e:
            logging.error(f"Erreur inattendue lors de la recherche: {e}")
            return []

