# import sqlite3

# conn = sqlite3.connect("chat_logs.db")
# cursor = conn.cursor()
# query = "Je n''ai pas cette information dans ma base de données."
# cursor.execute(f"DELETE FROM chat_logs WHERE response = '{query}'")
# conn.commit()
# conn.close()
# print("Données supprimées avec succès.")


import faiss
import pickle

# Charger l'index FAISS (les vecteurs)
index = faiss.read_index(r"VECTOR_DB\faiss_index.idx")

# Charger les textes
with open(r"VECTOR_DB\document_chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# Maintenant vous pouvez afficher ce que vous voulez
print(f"Nombre total de chunks : {len(chunks)}")

# Afficher les 5 premiers
for i in range(min(5, len(chunks))):
    print(f"--- Index {i} ---")
    print(chunks[i]['text'])