# SEL-TG : Assistant Virtuel de l'Administration Togolaise 🇹🇬

**SEL-TG** (Service En Ligne - Togo) est un chatbot intelligent conçu pour aider les citoyens à obtenir des informations précises sur les procédures administratives au Togo (passeport, carte d'identité, casier judiciaire, nationalité, etc.).

Il utilise une architecture **RAG (Retrieval-Augmented Generation)** pour fournir des réponses basées sur les documents officiels scrappés depuis le portail [service-public.gouv.tg](https://service-public.gouv.tg/service-online).

## 🚀 Fonctionnalités

-   **Classification Intelligente** : Distingue les questions générales ("Bonjour") des questions nécessitant une recherche documentaire ("Quelles pièces pour le passeport ?").
-   **RAG (Recherche Documentaire)** : Recherche les informations pertinentes dans une base de connaissances vectorielle pour répondre aux questions spécifiques.
-   **Reformulation Contextuelle** : Comprend le contexte de la conversation (ex: si vous demandez "Combien ça coûte ?" après avoir parlé du passeport, il comprendra qu'il s'agit du coût du passeport).
-   **Sources Officielles** : Fournit les liens vers les démarches en ligne officielles.
-   **Interface Conviviale** : Interface de chat moderne développée avec Streamlit.

## 🛠️ Stack Technique

-   **Langage** : Python 3.10+
-   **Interface** : [Streamlit](https://streamlit.io/)
-   **LLM & Embeddings** : [Mistral AI](https://mistral.ai/)
-   **Base de données Vectorielle** : [FAISS](https://github.com/facebookresearch/faiss)
-   **Scraping** : BeautifulSoup4 & Requests
-   **Orchestration** : LangChain (partiel)

## 📂 Structure du Projet

```
sel_mobile/
├── app.py                      # Point d'entrée de l'application Streamlit
├── collecte_data.py            # Script de scraping et préparation des données
├── manage_store.py             # Gestion de la base vectorielle (FAISS) et des embeddings
├── query_classification.py     # Logique de classification (RAG vs Direct) et reformulation
├── config.py                   # Configuration et variables d'environnement
├── style.py                    # Styles CSS pour l'interface Streamlit
├── requirements.txt            # Liste des dépendances pip
├── Dockerfile                  # Configuration Docker
└── VECTOR_DB/                  # Dossier contenant l'index FAISS et les chunks (généré)
```

## ⚙️ Installation et Configuration

### 1. Cloner le projet

```bash
git clone <votre-repo-url>
cd sel_mobile
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement

Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Mistral :

```env
MISTRAL_API_KEY=votre_cle_api_mistral_ici
```

##  ▶️ Utilisation

### Étape 1 : Préparer les données (Si nécessaire)

Si c'est la première fois ou si vous souhaitez mettre à jour les données depuis le site du gouvernement :

```bash
python collecte_data.py
```
*Cela va scraper le site, découper les textes et créer le fichier JSON des chunks.*

### Étape 2 : Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`.

## 🐳 Docker

Pour lancer l'application avec Docker :

```bash
docker build -t sel-tg-bot .
docker run -p 8501:8501 --env-file .env sel-tg-bot
```

## 📝 Auteur

Projet personnel développé pour faciliter l'accès à l'information administrative au Togo.
