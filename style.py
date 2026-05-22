# import streamlit as st
import os
import base64


# --- 2. Chemin et vérification de l'image ---
image_file_name = "ressources/Armoiries_du_Togo.png"

if not os.path.exists(image_file_name):
    # st.error(f"Erreur : Le fichier image '{image_file_name}' n'a pas été trouvé. Assurez-vous qu'il est dans le même répertoire que votre script Streamlit.")
    # st.stop() # Arrête l'exécution si l'image n'est pas trouvée
    print(f"Erreur : Le fichier image '{image_file_name}' n'a pas été trouvé. Assurez-vous qu'il est dans le même répertoire que votre script Streamlit.")

# --- NOUVEAU : Lecture et encodage de l'image en Base64 ---
try:
    with open(image_file_name, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    # Le format de l'image (png, jpeg, etc.) doit correspondre au type MIME
    image_mime_type = "image/png" # Changez ceci si votre image est un .jpg, .jpeg, etc.
    image_src = f"data:{image_mime_type};base64,{encoded_image}"
except Exception as e:
    print(f"Erreur lors de la lecture de l'image : {e}")
    # st.error(f"Erreur lors de l'encodage de l'image : {e}")
    # st.stop()


HEADER_STYLE = f"""
<style>
/* Importation de police Google Fonts (Inter pour un look moderne) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* Cache complètement l'entête par défaut de Streamlit */
header[data-testid="stHeader"] {{
    display: none;
}}

/* Conteneur principal de l’en-tête */
.fixed-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 9999;
    background: linear-gradient(135deg, #FFD700 0%, #FFC107 100%); /* Dégradé Or */
    color: #1a1a1a;
    padding: 12px 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    gap: 8px;
    backdrop-filter: blur(10px); /* Effet de flou moderne */
}}

/* Zone supérieure : logo + titre */
.header-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
}}

.logo-container {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.header-top img {{
    height: 48px;
    width: auto;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    transition: transform 0.3s ease;
}}

.header-top img:hover {{
    transform: scale(1.05);
}}

.header-top h1 {{
    color: #1a1a1a;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}}

.header-subtitle {{
    font-size: 0.9rem;
    font-weight: 500;
    opacity: 0.8;
}}

/* Texte défilant (Marquee) amélioré */
.marquee-container {{
    width: 100%;
    overflow: hidden;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 6px 0;
}}

.marquee-text {{
    display: inline-block;
    white-space: nowrap;
    animation: scroll-left 30s linear infinite;
    font-size: 14px;
    color: #000080;
    font-weight: 600;
}}

@keyframes scroll-left {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}

/* Ajustement du container principal pour éviter que le header ne cache le contenu */
.block-container {{
    padding-top: 130px !important;
    max-width: 1000px;
}}

/* 📱 Version mobile */
@media (max-width: 768px) {{
    .fixed-header {{
        padding: 10px 16px;
    }}
    .header-top img {{
        height: 40px;
    }}
    .header-top h1 {{
        font-size: 1.2rem;
    }}
    .header-subtitle {{
        display: none;
    }}
    .block-container {{
        padding-top: 140px !important;
    }}
}}

</style>

<div class="fixed-header">
    <div class="header-top">
        <div class="logo-container">
            <img src="{image_src}" alt="Armoiries du Togo">
            <div>
                <h1>SEL - TG 🇹🇬</h1>
                <span class="header-subtitle">Service En Ligne - Administration Togolaise</span>
            </div>
        </div>
    </div>
    <div class="marquee-container">
        <div class="marquee-text">
            🔔 Bienvenue ! Renseignez-vous facilement sur les procédures administratives (Passeport, Nationalité, Casier Judiciaire, etc.) • Service officiel d'information 🇹🇬
        </div>
    </div>
</div>
"""

CHAT_STYLE = f"""
<style>
/* Conteneur global */
.stChatFloatingInputContainer {{
    background: white !important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
}}

/* Bulles de chat communes */
.chat-bubble {{
    border-radius: 16px;
    padding: 10px 14px; /* Padding réduit (était 12px 18px) */
    margin: 4px 0;      /* Marge verticale réduite (était 8px 0) */
    max-width: 75%;
    width: fit-content;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.4;   /* Interligne réduit (était 1.5) */
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    animation: fadeIn 0.3s ease;
    position: relative;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Messages utilisateur */
.user-bubble {{
    background-color: #FFD700;  /* Jaune or (couleur du drapeau) */
    color: #1a1a1a;
    margin-left: auto;
    margin-right: 0;
    border-bottom-right-radius: 4px;
    text-align: left; /* Meilleure lisibilité */
    font-weight: 500;
}}

/* Messages assistant */
.bot-bubble {{
    background-color: #006a4e; /* Vert Togo */
    color: white;
    margin-right: auto;
    margin-left: 0;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,106,78,0.15);
}}

/* Liens dans les messages du bot */
.bot-bubble a {{
    color: #FFD700 !important;
    text-decoration: underline;
    font-weight: bold;
}}
.bot-bubble a:hover {{
    color: #ffffff !important;
}}

/* Listes dans les messages */
.bot-bubble ul, .bot-bubble ol {{
    margin-left: 20px;
    margin-top: 4px;    /* Réduit (était 8px) */
    margin-bottom: 4px; /* Réduit (était 8px) */
}}

/* Titres dans les messages */
.bot-bubble h3, .bot-bubble strong {{
    color: #FFD700;
    font-weight: 700;
}}

/* 📱 Adaptation mobile */
@media (max-width: 768px) {{
    .chat-bubble {{
        max-width: 90%;
        font-size: 15px;
    }}
}}
</style>
"""

# Chemin vers ton logo local
logo_path = "ressources/drapeau.jpg"

with open(logo_path, "rb") as f:
    encoded_logo = base64.b64encode(f.read()).decode("utf-8")



BODY_STYLE = f"""
<style>
/* Réduire l'espacement vertical global entre les éléments Streamlit */
div[data-testid="stVerticalBlock"] > div {{
    gap: 0.5rem !important; /* Force un écart plus petit entre les blocs (défaut ~1rem) */
}}
div[class*="stMarkdown"] {{
    margin-bottom: -5px; /* Remonte légèrement les blocs markdown */
}}

/* Fond global de l'application */
.stApp {{
    background-color: #f8f9fa !important; /* Gris très clair pour le fond */
}}

/* Zone de saisie du chat */
div[data-testid="stBottomBlockContainer"] {{
    background-color: #f8f9fa !important;
    padding-bottom: 20px;
    border-top: 1px solid rgba(0,0,0,0.05);
}}

/* Input du chat */
.stChatInputContainer textarea {{
    border-radius: 12px !important;
    border: 1px solid #e0e0e0 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    font-family: 'Inter', sans-serif;
}}
.stChatInputContainer textarea:focus {{
    border-color: #006a4e !important;
    box-shadow: 0 0 0 2px rgba(0,106,78,0.2) !important;
}}

/* Filigrane logo */
.stApp::before {{
    content: "";
    position: fixed;
    top: 55%;
    left: 50%;
    width: 400px;
    height: 400px;
    background: url("data:image/png;base64,{encoded_logo}") no-repeat center;
    background-size: contain;
    opacity: 0.08; /* Très subtil */
    pointer-events: none;
    transform: translate(-50%, -50%);
    z-index: 0; 
    filter: grayscale(100%); /* Plus élégant en gris */
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: #ffffff;
    border-right: 1px solid rgba(0,0,0,0.05);
}}

[data-testid="stSidebar"] h1 {{
    color: #006a4e;
    font-size: 1.4rem;
    font-weight: 700;
}}
</style>
"""

FEEDBACK_STYLE = """
<style>
/* Limiter la largeur du feedback et le rendre discret */
.feedback-wrapper {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-top: 4px;
    opacity: 0.7;
    transition: opacity 0.2s;
}
.feedback-wrapper:hover {
    opacity: 1;
}
/* Cibler les boutons de feedback streamlit pour les rendre plus petits */
[data-testid="stThumbSentiment"] button {
    border: none;
    background: transparent;
    padding: 0 4px;
}
</style>
"""