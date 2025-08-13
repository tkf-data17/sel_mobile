import streamlit as st
import os
import base64
from config import*


# --- 2. Chemin et vérification de l'image ---
image_file_name = "ressources/Armoiries_du_Togo.png"

if not os.path.exists(image_file_name):
    st.error(f"Erreur : Le fichier image '{image_file_name}' n'a pas été trouvé. Assurez-vous qu'il est dans le même répertoire que votre script Streamlit.")
    st.stop() # Arrête l'exécution si l'image n'est pas trouvée

# --- NOUVEAU : Lecture et encodage de l'image en Base64 ---
try:
    with open(image_file_name, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    # Le format de l'image (png, jpeg, etc.) doit correspondre au type MIME
    image_mime_type = "image/png" # Changez ceci si votre image est un .jpg, .jpeg, etc.
    image_src = f"data:{image_mime_type};base64,{encoded_image}"
except Exception as e:
    st.error(f"Erreur lors de l'encodage de l'image : {e}")
    st.stop()

HEADER_STYLE = f"""
<style>

/* Empêche le layout de devenir trop étroit */
body {{
    min-width: 1100px;
}}

/* Conteneur principal de l’en-tête */
.fixed-header {{
    position: fixed;
    top: 10px;
    left: 0;
    right: 0;
    margin: 0 auto; /* Centre l'élément horizontalement */
    max-width: 1200px; /* Définissez une largeur maximale pour l'en-tête */
    width: 100%;
    border-bottom: 1px solid #ccc;   /*c'est pour afficher la bordure de l'entete*/
    z-index: 9999;  /* ← TRÈS IMPORTANT */
    background-color: white;
    color: black;
    padding: 50px 20px 20px 320px; /* ← ajusté ici */
    box-sizing: border-box; /* ← protection contre débordement */
    box-shadow: 0 0px 0px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}

/* Zone supérieure : logo + titre */
.header-top {{
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}}

.header-top img {{
    height: 60px;
    margin-right: 15px;
}}

.header-top h1 {{
    color: black;
    margin: 0;
    font-size: 2em;
    line-height: 1;
}}

/* Texte défilant */
.marquee-container {{
    width: 100%;
    overflow: hidden;
    height: 30px;
    /*position: fixed;*/
    top: 125px;  /* ou l'ajuster selon ton header */
    width: 100%;
    z-index: 9998;
}}

.marquee-text {{
    display: inline-block;
    white-space: nowrap;
    padding-left: 100%;
    animation: scroll-left 50s linear infinite;
    font-size: 16px;
    color: yellow;
    font-weight: bold;
    line-height: 30px;
}}

@keyframes scroll-left {{
    0% {{ transform: translateX(0%); }}
    100% {{ transform: translateX(-100%); }}
}}

/* Décalage du contenu principal */
.block-container {{
    padding-top: 160px;
}}

/* Responsive: réduire la marge gauche si petit écran */
@media (max-width: 768px) {{
    .fixed-header {{
        padding-left: 20px;
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

