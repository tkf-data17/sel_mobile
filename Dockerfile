FROM python:3.12

WORKDIR /01_RAG_Fin_de_formation

# Copie uniquement requirements.txt pour profiter du cache
COPY requirements.txt .

# Installe les dépendances (caché si requirements.txt n’a pas changé)
RUN pip install --no-cache-dir -r requirements.txt


# copier notre projet dans l'image de python
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py" ]