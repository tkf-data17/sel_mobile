
from query_classification import *
# Interagir avec l'assistant

def ask_assistant(query):
    result = need_rag_or_not(query)
    print(query, "\n", result)
    print("*" * 100)

querys = [
    "Bonjour",
    "Merci beaucoup",
    "Comment ça va ?",
    "quel est le service qui delivre le passeport?",
    "Qui es-tu ?",
    "quel sont les pieces a fournir pour faire le passeport?",
    "quel sont les pieces a fournir pour faire le certificat de nationalité?",
    "quel est le delai de traitement du passeport?",
    "comment obtenir le casier judiciaire?",
    "Au revoir",
    "qui es-tu?",
    "J'ai besoin d'aide",
    "Quelles sont vos heures d'ouverture le mardi?", # Cette question ira toujours au LLM
    "Combien coûte l'analyse d'urine?" # Cette question ira toujours au LLM


          ]
