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

/* Empêche le layout de devenir trop étroit */
body {{
    min-width: unset;
}}

/* Contenu principal décalé pour le header fixe */
main[data-testid="stAppViewContainer"] {{
    background-color: red;  /* noir clair */
    color: white;  
    padding-top: 80px;  /* même hauteur que ton header */
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
    margin: 0 auto;
    width: 100%;
    border-bottom: 0px solid transparent;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    z-index: 9999;
    background-color: #FFD700; /* Jaune clair */
    color: black;
    padding: 10px;
    box-sizing: border-box;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}

/* Zone supérieure : logo + titre */
.header-top {{
    display: flex;
    align-items: center;
    margin-top: 10;
    margin-bottom: 5px;
    flex-wrap: wrap;
}}

.header-top img {{
    height: 50px;
    margin-right: 10px;
}}

.header-top h1 {{
    color: black;
    font-size: 1.5em;
    margin: 0;
    line-height: 1.2;
}}

/* Texte défilant */
.marquee-container {{
    width: 100%;
    overflow: hidden;
    height: 24px;
    background-color: #FFD70020; /* Jaune clair avec transparence */
}}

.marquee-text {{
    display: inline-block;
    white-space: nowrap;
    padding-left: 100%;
    animation: scroll-left 40s linear infinite;
    font-size: 14px;
    color: black;
    font-weight: bold;
    line-height: 24px;
}}

@keyframes scroll-left {{
    0% {{ transform: translateX(0%); }}
    100% {{ transform: translateX(-100%); }}
}}

/* Décalage du contenu principal */
.block-container {{
    padding-top: 80px;
    margin-top: 0px;    /*utilisation de l'espace */
}}

/* 📱 Version mobile */
@media (max-width: 768px) {{
    .fixed-header {{
        width: 100%;
        padding: 10px;
        align-items: center;
        text-align: left;
        margin: 0 auto;
    }}
    .header-top {{
        flex-direction: row;
        align-items: center;
        gap: 4px;
    }}
    .header-top img {{
        height: 50px;
        margin-right: 8px;
    }}
    .header-top h1 {{
        font-size: 1.5em;
    }}
    .marquee-text {{
        font-size: 12px;
    }}
    .block-container {{
        padding-top: 100px;
    }}
    .chat-bubble {{
        max-width: 95%;
        font-size: 16px;
    }}
}}

</style>

<div class="fixed-header">
    <div class="header-top">
        <img src="{image_src}" alt="Armoiries du Togo">
        <h1>📚SEL - TG</h1>
    </div>
    <div class="marquee-container">
        <div class="marquee-text">
            🔔 Hello, Renseigne-toi sur les procédures (Délai de traitement, Coût, Validité, Pièces à fournir, etc.) d'obtention des documents administratifs du Togo ! 🇹🇬
            🔔 Hello, Renseigne-toi sur les procédures (Délai de traitement, Coût, Validité, Pièces à fournir, etc.) d'obtention des documents administratifs du Togo ! 🇹🇬
        </div>
    </div>
</div>
"""

CHAT_STYLE = f"""
<style>
/* Bulles de chat */
.chat-bubble {{
    border-radius: 18px;
    padding: 10px 15px;
    margin-top: 10px;
    margin: 8px 0;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.4;
}}

.chat-container {{
    margin-top: 40px; /* décale tous les messages sous l’entête */
}}

/* Messages utilisateur */
.user-bubble {{
    background-color: #FFD700;  /* Jaune clair */
    color: black;
    margin-left: auto;            /* Aligne à droite */
    text-align: right;
}}

/* Messages assistant */
.bot-bubble {{
    background-color: green;
    color: white;
    margin-right: auto;           /* Aligne à gauche */
    text-align: left;
}}

/* 📱 Adaptation mobile */
@media (max-width: 768px) {{
    .chat-bubble {{
        margin-top: 4px;
        max-width: 95%;  /* Presque toute la largeur */
        font-size: 16px; /* Texte un peu plus gros */
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
/* Fond global de l'application */
body, .stApp, main[data-testid="stAppViewContainer"] {{
    background-color: white !important; /*#1e1e1e*/
    color: black !important;
}}

/* Zone de saisie du chat */
div[data-testid="stBottomBlockContainer"] {{
    background-color: white !important;
}}

/* Filigrane logo depuis fichier local */
.stApp::before {{
    content: "";
    position: fixed;
    top: 50%;
    left: 50%;
    width: 250px;
    height: 250px;
    background: url("data:image/png;base64,{encoded_logo}") no-repeat center;
    background-size: contain;
    opacity: 0.25;
    pointer-events: none;
    transform: translate(-50%, -50%);
    z-index: 0; /* bien derrière tout le contenu */
}}

/* Supprimer l'entête Streamlit par défaut */
header[data-testid="stHeader"] {{
    display: none;
}}
</style>
"""

FEEDBACK_STYLE = """
<style>
/* Limiter la largeur du feedback */
.feedback-wrapper {
    max-width: 60px; /* ou la largeur que tu veux */
    display: inline-block;
}
</style>
"""