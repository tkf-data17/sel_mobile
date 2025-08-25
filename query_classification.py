
import logging
from typing import Tuple, Dict, List
from config import *
from manage_store import search
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import google.genai as genai

# FONCTION POUR UNE CLASSIFICATION DES REQUETES

def classify_with_llm(query: str) -> Tuple[bool, str]:
        """
        Utilise le LLM pour classifier la requête

        Args:
            query: Requête de l'utilisateur

        Returns:
            Tuple (besoin_rag, confiance, raison)
        """
        try:
            system_prompt = f"""Vous êtes un classificateur de requêtes pour un assistant virtuel du service en ligne du Gouvenement Togolais.
Votre tâche est de déterminer si une question nécessite une recherche dans une base de connaissances spécifique au gouvernement.

Répondez UNIQUEMENT par "RAG" ou "DIRECT" suivi d'une brève explication:
- "RAG" si la question porte sur des informations spécifiques a la demande de passeport
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
"""

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=query)
            ]

            #  Fixation de Température
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=query)
            ]

            response = mistral_client.chat(
                model="mistral-small",
                messages=messages,
                temperature=0.1,  # Température basse pour des réponses cohérentes
                max_tokens=50  # pour avoir une reponse courte et ne pas laisser le llm faire des discours inutile
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
        f"""Vous êtes un assistant de réécriture de requêtes. Votre tâche est de prendre l'historique de conversation et la dernière question de l'utilisateur
        pour générer une nouvelle question unique qui capture toute l'intention et le contexte. La nouvelle question doit être une requête autonome, claire, précise et ne pas faire référence à la conversation.
        Reformule la question finale de façon autonome
        afin qu'elle soit compréhensible hors-contexte (sans dépendre des pronoms ou
        références implicites).
        *** Regles importantes ***
        - si l'historique est vide, retourne la question exactement comme elle est;
        - si la question ne fournit pas suffisamment de contexte, demande des précisions à l'utilisateur;
        - Réponds uniquement par la question reformulée, n'ajoute rien d'autre, pas d'information superflux provenant de tes données personnelles;
        - Si la question est déjà autonome, la renvoyer telle quelle;
        - La reponse doit etre OBLIGATOIREMENT EN FRANçAIS, concise et precise.

        Réécris la question:
        Historique de la conversation (derniers échanges):
        {hist_text}
        Question à reformuler: {user_question}
        """
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",  # Remplace par le modèle souhaité
            contents=system_prompt
        )
            # Essayer d'extraire correctement le texte
        rewritten = None
        if hasattr(resp, "text") and resp.text:
            rewritten = resp.text.strip()
        elif hasattr(resp, "candidates") and resp.candidates:
            parts = resp.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                rewritten = parts[0].text.strip()
        
        # Fallback : si pas de texte, renvoyer la question brute
        if not rewritten:
            return user_question
        return rewritten
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

        retrieved_docs = search(query, min_score=0.75)
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

    user_message = ChatMessage(role="user", content=query)
    system_message = ChatMessage(role="system", content=system_prompt)
    messages_for_api = [system_message, user_message]

    # 3. Appel à l'API Mistral Chat

    chat_response = mistral_client.chat(
        model="mistral-small",
        messages=messages_for_api,
        temperature=0.5,
        # max_tokens=1024
    )
    result = chat_response.choices[0].message.content

    return result
