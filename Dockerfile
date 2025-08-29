FROM python:3.12

WORKDIR /02_RAG_SEL_V_Mobile

# Copie uniquement requirements.txt pour profiter du cache
COPY requirements.txt .

# Installe les dépendances (caché si requirements.txt n’a pas changé)
RUN pip install --no-cache-dir -r requirements.txt


# copier notre projet dans l'image de python
COPY . .

# Installer le modèle spaCy français
RUN python -m spacy download fr_core_news_sm

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py","--server.port=8501", "--server.address=0.0.0.0" ]