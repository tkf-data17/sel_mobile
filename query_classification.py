
import logging
from typing import Tuple, Dict, List, Optional
from config import *
from manage_store import get_store_manager
from mistralai.client import Mistral


def classify_with_llm(query: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[bool, str]:
        """
        Utilise le LLM pour classifier la requête

        Args:
            query: Requête de l'utilisateur

        Returns:
            Tuple (besoin_rag, confiance, raison)
        """
        try:

            # Construction de l'historique
            history_text = ""
            if history:
                # On prend les 3 derniers échanges, excluant potentiellement la requête actuelle si elle est déjà dans l'historique
                # Mais généralement on passe l'historique *précédent*.
                recent = history[-6:] # Derniers 3 échanges (user+assistant)
                for msg in recent:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    # On évite d'inclure la query actuelle si elle est déjà dans la liste (simple heuristique)
                    if content != query: 
                         history_text += f"{role.upper()}: {content}\n"

            system_prompt = f"""Vous êtes un classificateur de requêtes pour un assistant virtuel du service en ligne du Gouvenement Togolais.
Votre tâche est de déterminer si une question nécessite une recherche dans une base de connaissances spécifique au gouvernement.

Utilisez l'historique de la conversation pour comprendre le contexte si la question est ambiguë (ex: "combien ça coûte?" fait référence au sujet précédent).

Historique récent:
{history_text}

Répondez UNIQUEMENT par "RAG" ou "DIRECT" suivi d'une brève explication:
- "RAG" si la question porte sur des informations spécifiques sur les documents admnistratifs (même si implicite via l'historique)
- "DIRECT" si c'est une question générale, une salutation, ou une question qui ne nécessite pas d'informations spécifiques à la commune.

Exemples:
Question: "Bonjour, comment ça va?"
Réponse: DIRECT - Simple salutation

Question: "merci?"
Réponse: DIRECT - remerciements

Question: "au revoir?"
Réponse: DIRECT - remerciements

Question: "à combien se fait le passeport togolais?"
Réponse: RAG - Demande d'informations spécifiques a la demande de passeport

Question: "Quel sont les pieces a fournir pour faire la demande de casier judiciare?"
Réponse: RAG - Demande d'informations spécifiques aux services en ligne

Question: "Quel est la durée maximale pour obtenir ma nationalité?"
Réponse: RAG - Demande d'informations spécifiques aux services en ligne

Question: "Qu'est-ce que l'intelligence artificielle?"
Réponse: DIRECT - Question générale de connaissance

Question (avec contexte Passeport): "Combien ça coûte ?"
Réponse: RAG - Demande implicite sur le coût du passeport (contexte)
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            response = mistral_client.chat.complete(
                model="mistral-small",
                messages=messages,
                temperature=0.1,  # Température basse pour des réponses cohérentes
            )

            result = response.choices[0].message.content.strip()

            logging.info(f"Classification LLM pour '{query}': {result}")

            # Analyser la réponse
            if result.startswith("RAG"):
                reason = result.replace("RAG - ", "").replace("RAG-", "").replace("RAG:", "").strip()
                return True, reason
            elif result.startswith("DIRECT"):
                reason = result.replace("DIRECT - ", "").replace("DIRECT-", "").replace("DIRECT:", "").strip()
                return False, reason
            else:
                # Réponse ambiguë, utiliser RAG par défaut
                return True, "Classification ambiguë, utilisation de RAG par précaution"

        except Exception as e:
            logging.error(f"Erreur lors de la classification avec LLM: {e}")
            # En cas d'erreur, utiliser RAG par défaut
            return True, f"Erreur de classification: {str(e)}"

#-----------------------------------------------------------------------------------------------------------
# FONCTION POUR AMELIORER LA QUESTION DE L'UTILISATEUR
#-----------------------------------------------------------------------------------------------------------


def rewrite_question(user_question: str, conversation_history: List[Dict], max_history_entries: int = 3) -> str:
    """
    Reformule la `user_question` de manière autonome en tenant compte de l'historique.
    conversation_history : liste d'entrées {"role":"user"/"assistant", "content": "..."}
    On limite l'historique pour rester dans les tokens.
    """
    # Construire un historique textuel limité (les dernières N échanges)
    recent = conversation_history[-max_history_entries * 2 :] if conversation_history else []
    hist_text = ""
    for item in recent:
        role = item.get("role", "")
        content = item.get("content", "")
        hist_text += f"{role.upper()}: {content}\n"

    system_prompt = (
        f"""Vous êtes un assistant de réécriture de requêtes pour un service administratif TOGOLAIS.
        Votre tâche est de prendre l'historique de conversation et la dernière question de l'utilisateur
        pour générer une nouvelle question unique qui capture toute l'intention et le contexte. La nouvelle question doit être une requête autonome, claire, précise et ne pas faire référence à la conversation.
        Reformule la question finale de façon autonome
        afin qu'elle soit compréhensible hors-contexte (sans dépendre des pronoms ou
        références implicites).
        *** Regles importantes ***
        - si l'historique est vide, retourne la question exactement comme elle est;
        - Réponds uniquement par la question reformulée, n'ajoute rien d'autre, pas d'information superflux provenant de tes données personnelles;
        - Si la question est déjà autonome ou si elle introduit un NOUVEAU SUJET (ex: passer du passeport au casier judiciaire), ne la mélange pas avec l'ancien sujet. Reformule-la de manière autonome sans mentionner l'ancien sujet;
        - NE JAMAIS ajouter de référence géographique (pays, ville, région) qui n'est pas dans la question originale. Le service est au TOGO, ne mentionne jamais "en France" ou tout autre pays étranger;
        - La reponse doit etre OBLIGATOIREMENT EN FRANçAIS, concise et precise.

        Réécris la question:
        Historique de la conversation (derniers échanges):
        {hist_text}
        Question à reformuler: {user_question}
        """
    )
    try:


        messages_for_api = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]

        resp = mistral_client.chat.complete(
            model="mistral-small",
            messages=messages_for_api,
            temperature=0.2,
        )
        result = resp.choices[0].message.content
        return result

    except Exception as e:
        logging.error("Erreur rewrite_question: %s", e)
        return user_question




#-----------------------------------------------------------------------------------------------------------
# FONCTION POUR GENERER LES REPONSES
#-----------------------------------------------------------------------------------------------------------

def answer_question(query):
    needs_rag, _ = classify_with_llm(query)

    if needs_rag:
        logging.info(f"Mode RAG - Recherche de documents pour la question: {query}")

        manager = get_store_manager()
        retrieved_docs = manager.search(query, min_score=0.75)
          # Préparer le contexte pour le LLM
        context_str = "\n\n---\n\n".join([
            f"Source: {doc['metadata'].get('source', 'Inconnue')} (Score: {doc['score']:.4f})\nContenu: {doc['text']}"
            for doc in retrieved_docs
        ])
        sources_for_log = [ # Version simplifiée pour le log et l'affichage
            {"text": doc["text"]}   #, "metadata": doc["metadata"], "score": doc["score"]
            for doc in retrieved_docs
        ]

        # Construction du prompt RAG avec placeholders pour le contexte et la question
        system_prompt = f"""Votre nom est SEL, Vous êtes un assistant utile de l'administration publique togolaise qui répond aux questions relatives au processus d'obtention des documents administratives (description, délai d'exécution, coût de la procédure, durée de validité, pièces à fournir, étapes à suivre, etc).

Utilisez le contexte suivant pour répondre à la question.

Règles importantes :
- Répondez uniquement avec les informations présentes dans les documents fournis
- Si l'information n'est pas dans les documents, dites : "Je n'ai pas cette information dans ma base de données."
- Ne jamais inventer ou supposer des prix, délais ou procédures.
- Citez toujours vos sources quand possible.

Contexte fourni :
---
{context_str}

"""


    else:
        logging.info(f"Mode direct - Réponse basée sur les connaissances générales du modèle")

        system_prompt = """Votre nom est SEL, vous êtes un assistant virtuel pour le service en ligne du gouvernement togolais.

Répondez à la question de l'utilisateur en utilisant vos connaissances générales.
Soyez concis, précis et utile.

Si la question concerne des informations spécifiques aux services en ligne du gouvernement togolais que vous ne connaissez pas, indiquez clairement que vous n'avez pas cette information spécifique.
N'inventez pas d'informations sur le gouvernement togolais.
"""

    messages_for_api = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    # 3. Appel à l'API Mistral Chat
    chat_response = mistral_client.chat.complete(
        model="mistral-small",
        messages=messages_for_api,
        temperature=0.5,
    )

    result = chat_response.choices[0].message.content

    return result
