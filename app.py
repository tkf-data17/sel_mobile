
import streamlit as st
import logging
from typing import Optional
import numpy as np
import uuid
from streamlit_feedback import streamlit_feedback
# import spacy

from mistralai.client import Mistral

from config import MISTRAL_API_KEY
from manage_store import get_store_manager
from query_classification import classify_with_llm, rewrite_question
from style import HEADER_STYLE, CHAT_STYLE, BODY_STYLE, FEEDBACK_STYLE
from database_manage import DatabaseManager


st.set_page_config(
    layout="wide" # Pour utiliser toute la largeur de l'écran
)

# --- Initialisation de la Base de Données ---
db_manager = DatabaseManager()

# --- Fonction de gestion du feedback ---
def handle_feedback(feedback, interaction_id):
    if feedback and feedback.get("score") == "👍":
        # Retrouver la réponse et la question associée
        messages = st.session_state.messages
        response = None
        query = None
        
        for i, msg in enumerate(messages):
            if msg.get("interaction_id") == interaction_id:
                response = msg["content"]
                # Utiliser la question reformulée si disponible, sinon la question utilisateur précédente
                query = msg.get("rewrited_query")
                if not query and i > 0 and messages[i-1]["role"] == "user":
                    query = messages[i-1]["content"]
                break
        
        if query and response:
            db_manager.save_feedback(
                user_id=st.session_state.get("user_id", "anonymous"),
                query=query,
                response=response,
                score="thumbs_up"
            )
            # Optionnel : petit message de confirmation (invisible à l'utilisateur final si souhaité)
            logging.info(f"Feedback positif enregistré pour l'interaction {interaction_id}")

# --- initialisation de l'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Chargement du Store Manager (Singleton) ---
@st.cache_resource
def get_manager():
    return get_store_manager()

manager = get_manager()


# Met en cache le client Mistral
@st.cache_resource
def get_mistral_client():
    if not MISTRAL_API_KEY:
        st.error("Erreur: La clé API Mistral (MISTRAL_API_KEY) n'est pas configurée.")
        st.stop()
    logging.info("Initialisation du client Mistral...")
    return Mistral(api_key=MISTRAL_API_KEY)

mistral_client = get_mistral_client()


#------------------------------------------------------------------------------------------------

# --- Styles ---
st.markdown(HEADER_STYLE, unsafe_allow_html=True)
st.markdown(BODY_STYLE, unsafe_allow_html=True)
st.markdown(CHAT_STYLE, unsafe_allow_html=True)
st.markdown(FEEDBACK_STYLE, unsafe_allow_html=True)


#-------------------------------------------------------------------------------------------------------

# --- Interface Utilisateur ---


#----------------------------------------------------------
# Creation de la sidebar pour l'assistant virtuel
#-----------------------------------------------------------

# Barre latérale (sidebar)
with st.sidebar:
    st.title(f"📚 SEL-TG")
    st.caption(f"Assistant virtuel du Gouvernement Togolais")

    # Bouton pour lancer une nouvelle conversation
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        # Réinitialiser l'historique des messages
        st.session_state.messages = []
        st.session_state.last_interaction_id = None
        st.rerun()  # Recharger l'application pour afficher la nouvelle conversation


# ----------------------------------------------------------
# Affichage de l'historique
# ----------------------------------------------------------
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    bubble_class = "user-bubble" if role == "user" else "bot-bubble"

    # Affichage de la bulle
    st.markdown(f"<div class='chat-bubble {bubble_class}'>{content}</div>", unsafe_allow_html=True)

    # Feedback sous chaque réponse de l'assistant
    if role == "assistant" and "interaction_id" in message:
        # Colonnes : gauche petite pour le feedback, droite vide
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            st.markdown('<div class="feedback-wrapper">', unsafe_allow_html=True)
            streamlit_feedback(
                feedback_type="thumbs",
                key=f"feedback_{message['interaction_id']}",
                align="flex-start",
                on_submit=handle_feedback,
                args=(message['interaction_id'],)
            )
            st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT INPUT ---
if query := st.chat_input("Posez votre question ici..."):

    # Vérification pour éviter de retraiter la même question en cas de rerun (feedback click, etc.)
    last_user_msg = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
    
    if query.strip() == "":
        st.warning("Veuillez poser une question.")
    elif query == last_user_msg:
        # La question est identique à la dernière, on ne fait rien pour éviter le double traitement
        pass
    else:
        # Ajouter et afficher immédiatement la question de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": query})
        st.markdown(f"<div class='chat-bubble user-bubble'>{query}</div>", unsafe_allow_html=True)

        # Placeholder pour la réponse
        placeholder = st.empty()
        placeholder.markdown(
            "<div class='chat-bubble bot-bubble'>⏳ Traitement en cours...</div>",
            unsafe_allow_html=True
        )

        try:
            # --- CLASSIFICATION ---
            # prompt = powered_query(query, st.session_state.messages)
            needs_rag, _ = classify_with_llm(query, st.session_state.messages)

            if needs_rag:
                logging.info(f"Mode RAG - Recherche de documents pour la question: {query}")
                # reformuler la question
                rewrited_query = rewrite_question(query, st.session_state.messages)
                logging.info(f"Question reformulée : {rewrited_query}")

                # recherche de documents (on prend un peu plus de chunks pour être sûr)
                retrieved_docs = manager.search(rewrited_query, k=10, min_score=0.70)
                logging.info(f"Nombre de documents trouvés : {len(retrieved_docs)}")
                
                if retrieved_docs:
                    best_score = max(doc['score'] for doc in retrieved_docs)
                    logging.info(f"Meilleur score de similarité : {best_score:.2f}%")
                    # Log des titres des documents pour voir ce qui est récupéré
                    for i, doc in enumerate(retrieved_docs):
                        title = doc['metadata'].get('title', 'Sans titre')
                        logging.info(f"Doc {i+1} : {title} (Score: {doc['score']:.2f}%)")
                else:
                    logging.warning("Aucun document trouvé au-dessus du seuil.")

                # 🔹 Trier et garder uniquement les 6 meilleurs chunks (au lieu de 5 précédemment)
                retrieved_docs = sorted(retrieved_docs, key=lambda x: x['score'], reverse=True)[:6]
                
                # Log du début du contenu pour vérification
                for i, doc in enumerate(retrieved_docs):
                    snippet = doc['text'][:100].replace('\n', ' ')
                    logging.info(f"Contenu Doc {i+1} : {snippet}...")
                    # Préparer le contexte pour le LLM
                context_str = "\n\n---\n\n".join([
                    f"Document: {doc['metadata'].get('title', 'Sans titre')}\nSource: {doc['metadata'].get('source', 'Inconnue')}\nContenu: {doc['text']}"
                    for doc in retrieved_docs
                ])
                logging.info(f"Contexte préparé ({len(retrieved_docs)} chunks)")
                sources_for_log = [ # Version simplifiée pour le log et l'affichage
                    {"text": doc["text"]}   #, "metadata": doc["metadata"], "score": doc["score"]
                    for doc in retrieved_docs
                ]
                # fixation de la temperature
                temperature = 0.2
                # Construction du prompt RAG avec placeholders pour le contexte et la question
                system_prompt = f"""Votre nom est SEL, Vous êtes l'assistant utile de l'administration publique togolaise qui répond aux questions relatives au processus d'obtention des documents administratives (description, délai d'exécution, coût de la procédure, durée de validité, pièces à fournir, étapes à suivre, etc).

      
        Règles importantes :
        - Répondez uniquement avec les informations présentes dans le contexte fourni
        - Répondez obligatoirement en français
        - si l'utilisateur pose une question sans donner la precision sur le documents recherché, dit lui de preciser le document recherché.
            Exemple:
            user: combien?
            system: veuillez reformuler votre question en precisant le type de documents que vous recherchez.
        - Si l'information n'est pas dans les documents, dites : "Je n'ai pas cette information dans ma base de données."
        - Ne jamais inventer une information.
        - Proposez à l'utilisateur le lien vers la page officiel quand c'est disponible dans le contexte.
        - si l'utilisateur pose une question concernant le certificat de nationalité sans précisé le mot clé "certificat", traite la demande en remplaçant 'nationalité' par 'certificat de nationalité'.
        - si l'utilisateur pose une question concernant le casier judiciaire sans précisé le mot clé "extrait", traite la demande en remplaçant 'casier judiciaire' par 'extrait de casier judiciaire'.

        Contexte fourni :
        ---
        {context_str}

        QUESTION :
        {rewrited_query}

        """

            else:
                logging.info(f"Mode direct - Réponse basée sur les connaissances générales du modèle")
                # pas de reformulation de question
                rewrited_query = query
                # fixation de la temperature
                temperature = 0.5
                system_prompt = """
                    Votre nom est SEL. Vous êtes l'assistant virtuel du gouvernement togolais.  

                    ⚠️ Règles importantes :
                    - Répondez uniquement en français.  
                    - Donnez une réponse courte (max 2 phrases).  
                    - Soyez concis, précis et utile.  
                    - Si vous n'êtes pas sûr de la réponse, dites exactement : "Je n'ai pas cette information à ma disposition."  
                    - Ne jamais inventer, extrapoler ou supposer des informations.  

                    Le lien pour consulter les services en ligne est :  
                    https://service-public.gouv.tg/service-online
        """

            messages_for_api = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": rewrited_query}
            ]

            # 3. Appel à l'API Mistral Chat en STREAMING
            stream_response = mistral_client.chat.stream(
                model="mistral-small",
                messages=messages_for_api,
                temperature=temperature,
            )

            # Initialisation de la réponse vide
            full_response = ""
            
            # 4. Boucle de lecture du flux et mise à jour en temps réel
            with stream_response as event_stream:
                for chunk in event_stream:
                    chunk_content = chunk.data.choices[0].delta.content
                    if chunk_content:
                        full_response += chunk_content
                        # Mise à jour avec le style CSS + curseur
                        placeholder.markdown(
                            f"<div class='chat-bubble bot-bubble'>{full_response}▌</div>", 
                            unsafe_allow_html=True
                        )

            result = full_response
            logging.info(f"Réponse du LLM (Streamée): {result}")
            
            # 🔹 Vérification anti-hallucination
            if needs_rag:
                result = result
            else:
                # Vérifier que la réponse n'est pas trop longue ou hors-sujet
                if len(result.split()) > 50:  # max ~2 phrases
                    result = "Je n'ai pas cette information à ma disposition."

            interaction_id = str(uuid.uuid4())

            # Ajouter la réponse à l'historique
            st.session_state.messages.append({
                "role": "assistant",
                "content": result,
                "interaction_id": interaction_id,
                "rewrited_query": rewrited_query
            })

            # Remplacer le placeholder par la réponse finale (sans curseur)
            placeholder.markdown(
                f"<div class='chat-bubble bot-bubble'>{result}</div>",
                unsafe_allow_html=True
            )

            # On force un rerun pour que l'historique (avec le nouveau message et son feedback) 
            # soit affiché proprement en haut par la boucle principale.
            st.rerun()

        except Exception as e:
            logging.error(f"Erreur dans le chat: {e}")
            placeholder.markdown(
                "<div class=’chat-bubble bot-bubble’>❌ Une erreur s’est produite. Veuillez réessayer.</div>",
                unsafe_allow_html=True
            )
    
    # st.write(rewrited_query)
