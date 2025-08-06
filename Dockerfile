FROM python:3.12

WORKDIR /01_RAG_Fin_de_formation

# copier notre projet dans l'image de python
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py" ]