
import streamlit as st
import logging
from typing import Optional
import numpy as np
import uuid
from streamlit_feedback import streamlit_feedback
# import spacy

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from config import MISTRAL_API_KEY, ALL_CHUNKS_PATH
from manage_store import load_all_chunks, build_index, search, _generate_embeddings
from query_classification import classify_with_llm, rewrite_question
from style import HEADER_STYLE, CHAT_STYLE, BODY_STYLE, FEEDBACK_STYLE


st.set_page_config(
    layout="wide" # Pour utiliser toute la largeur de l'écran
)

# --- initialisation de l'HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_data
def load_chunks():
  # Lire le fichier JSON et charger les données
  return load_all_chunks(ALL_CHUNKS_PATH)

# chargement des données
@st.cache_data
def get_load_data():
    logging.info("Chargement des données...")
    return build_index(chunks_recharges)

@st.cache_data
def get_generate_embeddings() -> Optional[np.ndarray]:
    """Génère les embeddings pour une liste de chunks via l'API Mistral."""
    logging.info("Génération des embeddings...")
    return _generate_embeddings(chunks_recharges, mistral_client)

@st.cache_data
def get_build_index():
      """Construit l'index Faiss à partir des documents."""
      logging.info("Construction de l'index Faiss...")
      return build_index(ALL_CHUNKS_PATH)

# Met en cache le client Mistral
@st.cache_resource
def get_mistral_client():
    if not MISTRAL_API_KEY:
        st.error("Erreur: La clé API Mistral (MISTRAL_API_KEY) n'est pas configurée.")
        st.stop()
    logging.info("Initialisation du client Mistral...")
    return MistralClient(api_key=MISTRAL_API_KEY)

chunks_recharges = load_chunks()
mistral_client = get_mistral_client()
embedding = get_generate_embeddings()
index, chunks = get_build_index()

# nlp = spacy.load("fr_core_news_sm")

# # Lemmatisation de la question
# def lemmatize_question(question: str) -> str:
#     """
#     Lemmatisation d'une question en français.
#     Renvoie la question reconstruite avec les lemmes des mots.
#     """
#     doc = nlp(question)
#     # On ignore les espaces et ponctuations inutiles
#     lemmatized = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]
#     return " ".join(lemmatized)


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
    if st.button("🔄 Nouvelle conversation", use_container_width=True):
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
            )
            st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT INPUT ---
if query := st.chat_input("Posez votre question ici..."):

    if query.strip() == "":
        st.warning("Veuillez poser une question.")
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
        needs_rag, _ = classify_with_llm(query)

        if needs_rag:
            logging.info(f"Mode RAG - Recherche de documents pour la question: {query}")
            # reformuler la question
            rewrited_query = rewrite_question(query, st.session_state.messages)

            # Lemmatisation de la question
            # lemmatized_query = lemmatize_question(rewrited_query)

            # recherche de documents
            retrieved_docs = search(rewrited_query, min_score=0.80)
            # 🔹 Trier et garder uniquement les 3 meilleurs chunks
            retrieved_docs = sorted(retrieved_docs, key=lambda x: x['score'], reverse=True)[:3]
                # Préparer le contexte pour le LLM
            context_str = "\n\n---\n\n".join([
                f"Source: {doc['metadata'].get('source', 'Inconnue')}\nContenu: {doc['text']}"
                for doc in retrieved_docs
            ])
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
            temperature = 0.3
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

        user_message = ChatMessage(role="user", content=rewrited_query)
        system_message = ChatMessage(role="system", content=system_prompt)
        messages_for_api = [system_message, user_message]

        # 3. Appel à l'API Mistral Chat

        chat_response = mistral_client.chat(
            model="mistral-small",
            messages=messages_for_api,
            temperature=temperature,
            # max_tokens=1024
        )
        result = chat_response.choices[0].message.content
        logging.info(f"Réponse du LLM: {result}")
        
        # def contains_keywords(result, docs, min_match=2):
        #     for doc in docs:
        #         words = doc["text"].split()[:10]  # 10 premiers mots du chunk
        #         matches = sum(1 for w in words if w.lower() in result.lower())
        #         if matches >= min_match:
        #             return True
        #     return False
        
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
            "interaction_id": interaction_id
        })

        # Remplacer le placeholder par la réponse finale
        placeholder.markdown(
            f"<div class='chat-bubble bot-bubble'>{result}</div>",
            unsafe_allow_html=True
        )

        # Feedback pour la réponse courante dans colonne compacte à gauche
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            st.markdown('<div class="feedback-wrapper">', unsafe_allow_html=True)
            streamlit_feedback(
                feedback_type="thumbs",
                key=f"feedback_{interaction_id}",
                align="flex-start",
            )
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        logging.error(f"Erreur dans le chat: {e}")
        # msg_box.markdown(f"❌ Une erreur{e} s’est produite. Veuillez réessayer.")


