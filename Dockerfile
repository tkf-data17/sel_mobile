FROM python:3.12

WORKDIR /app

# Copier requirements et mettre pip à jour
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# Installer le modèle spaCy français
# RUN python -m spacy download fr_core_news_sm

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
