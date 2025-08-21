# import streamlit as st
import os
import base64
from config import*


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

/* Conteneur principal de l’en-tête */
.fixed-header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    margin: 0 auto;
    width: 100%;
    border-bottom: 1px solid #ccc;
    z-index: 9999;
    background-color: white;
    color: black;
    padding: 20px;
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
    margin-bottom: 10px;
}}

.header-top img {{
    height: 50px;
    margin-right: 10px;
}}

.header-top h1 {{
    color: black;
    margin: 0;
    font-size: 1.5em;
    line-height: 1.2;
}}

/* Texte défilant */
.marquee-container {{
    width: 100%;
    overflow: hidden;
    height: 24px;
    background-color: #f0f0f0;
}}

.marquee-text {{
    display: inline-block;
    white-space: nowrap;
    padding-left: 100%;
    animation: scroll-left 40s linear infinite;
    font-size: 14px;
    color: darkblue;
    font-weight: bold;
    line-height: 24px;
}}

@keyframes scroll-left {{
    0% {{ transform: translateX(0%); }}
    100% {{ transform: translateX(-100%); }}
}}

/* Décalage du contenu principal */
.block-container {{
    padding-top: 120px;
}}


/* 📱 Version mobile */
@media (max-width: 768px) {{
    .fixed-header {{
        padding: 10px 15px;
        align-items: center;
        text-align: center;
    }}
    .header-top {{
        flex-direction: column;
    }}
    .header-top img {{
        height: 40px;
        margin: 0 0 5px 0;
    }}
    .header-top h1 {{
        font-size: 1.2em;
    }}
    .marquee-text {{
        font-size: 12px;
    }}
    .block-container {{
        padding-top: 100px;
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
    margin: 8px 0;
    max-width: 70%;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.4;
}}

/* Messages utilisateur */
.user-bubble {{
    background-color: #00800020;  /* Vert léger */
    margin-left: auto;            /* Aligne à droite */
    text-align: right;
}}

/* Messages assistant */
.bot-bubble {{
    background-color: #FFD70020;  /* Jaune clair */
    margin-right: auto;           /* Aligne à gauche */
    text-align: left;
}}

/* 📱 Adaptation mobile */
@media (max-width: 768px) {{
    .chat-bubble {{
        max-width: 95%;  /* Presque toute la largeur */
        font-size: 16px; /* Texte un peu plus gros */
    }}
}}
</style>
"""
