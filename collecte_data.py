
from bs4 import BeautifulSoup as bs
import json
import os
import sys
import pandas as pd
from requests import get
from urllib.parse import urljoin

# recuperation des données sur la page principale

top_url = "https://service-public.gouv.tg/service-online"
def collect_data_list():
    # Faire une requête GET pour récupérer le contenu de la page
    print(f"Collecte des données depuis {top_url}...")
        # Utiliser requests pour obtenir le contenu de la page
    resp = get(top_url)
    soup = bs(resp.content, "html.parser")

    # recupération de toute les catégories de services en ligne
    categories = soup.find_all("div", class_="d-flex pb-2")

    # recuperation de tous les liens du site et les noms de chaque rubrique

    data_links = []
    title_list = []
    for categorie in categories:
        try:
            relative_path = categorie.find("a", class_="primary-link")["href"]    # recuperation des lien relatives de chaque rubriques
            title = categorie.find("a", class_="primary-link").text               # recuperation des titres des rubriques
            absolute_path = urljoin(top_url, relative_path)
            data_links.append(absolute_path)
            title_list.append(title)
        except:
            pass

    return data_links, title_list


# collecte de toutes les informations relatives a chaque rubrique

 # fonction pour recuperer les données sur un site
def scrape_data(url, title):

  try:
      resp = get(url)
      resp.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
      soup = bs(resp.text, "html.parser")

      # recuperation des données
      conteneurs = soup.find_all("div", class_="bg-light-blue p-3 rounded-3 mb-2 mb-md-4")

      # Check if conteneurs has enough elements before accessing
      if len(conteneurs) >= 3:
          durée = conteneurs[0].find("span").text if conteneurs[0].find("span") else "N/A"
          prix = conteneurs[1].find("span").text if conteneurs[1].find("span") else "N/A"
          validité = conteneurs[2].find("span").text if conteneurs[2].find("span") else "N/A"
      else:
          durée, prix, validité = "N/A", "N/A", "N/A"
          print(f"Warning: Could not find enough conteneurs for {url}")


      contact_direction_tag = soup.find("div", class_="d-flex flex-column")
      contact_direction = contact_direction_tag.text.strip() if contact_direction_tag else "N/A"

      description_tag = soup.find("div", class_="service-description")
      description = description_tag.text.strip() if description_tag else "N/A"


      dic ={
          f"delai de traitement pour {title}" : durée,
          f"prix à payer pour {title}" : prix,
          f"durée de validité pour {title}" : validité,
          f"information pour {title}" : contact_direction,
          f"description pour {title}" : description,
          f"source pour {title}" : url
          }
      return dic

  except Exception as e:
      print(f"Error scraping {url}: {e}")
      return {}

# Recuperer le contenu et transformer en format document

from langchain_core.documents import Document

def buil_documents_from_links(data_links, title_list):

    documents = []

    # Parcours de chaque service
    for url, title in zip(data_links, title_list):
        info = scrape_data(url, title)
        if not info:
            continue  # Skip si scraping échoué

        # Formatage en texte brut
        text = "\n".join(f"{k} : {v}" for k, v in info.items())

        # Création d’un Document par service
        doc = Document(page_content=text, metadata={"title": title, "source": url})
        documents.append(doc)

    # Affichage (facultatif) pour validation
    print(f"{len(documents)} documents collectés.")
    return documents


# Faire le nettoyage et le chunking

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Chunking des documents
def _split_documents_and_chunks(documents):
  text_splitter = RecursiveCharacterTextSplitter(
  chunk_size      = 1500,    # nombre de tokens par chunk
  chunk_overlap   = 200,    # chevauchement entre les chunks
  length_function = len,
  separators=[
      "\n\n",
      "\n",
      " ",
      ".",
      ",",
      "\u200b",  # Zero-width space
      "\uff0c",  # Fullwidth comma
      "\u3001",  # Ideographic comma
      "\uff0e",  # Fullwidth full stop
      "\u3002",  # Ideographic full stop
      "",
    ],
  )

  all_chunks = []
  doc_counter = 0
  for num in range(len(documents)):

    chunks = text_splitter.split_documents([documents[num]])

    # Enrichit chaque chunk avec des métadonnées supplémentaires
    for i, chunk in enumerate(chunks):
      chunk_dict = {
          "id": f"{doc_counter}_{i}", # Identifiant unique du chunk (doc_index_chunk_index)
          "text": chunk.page_content,
          "metadata": {
              "chunk_id_in_doc": i, # Position du chunk dans son document d'origine
              "start_index": chunk.metadata.get("start_index", -1) # Position de début (en caractères)
          }
      }
      all_chunks.append(chunk_dict)
    doc_counter += 1

#   logging.info(f"Total de {len(all_chunks)} chunks créés.")
  return all_chunks


def save_all_chunks(all_chunks):

  # Nom du fichier de sortie
  output_file_json = "save_chunks/chunks_save.json"

  # Ouvrir le fichier en mode écriture ('w') avec encodage UTF-8
  # Utiliser json.dump pour écrire la liste de dictionnaires
  with open(output_file_json, "w", encoding="utf-8") as f:
      # indent=4 rend le fichier JSON lisible par un humain (indentation de 4 espaces)
      # ensure_ascii=False permet de sauvegarder les caractères non-ASCII (comme les accents) directement
      json.dump(all_chunks, f, indent=4, ensure_ascii=False)

  print(f"Vos chunks (dictionnaires) ont été sauvegardés avec succès dans le fichier : '{output_file_json}'")


def collect_data():
   data_list, title_list = collect_data_list()
   documents = buil_documents_from_links(data_list, title_list)
   all_chunks = _split_documents_and_chunks(documents)
   save_all_chunks(all_chunks)
   print("Collecte de données terminée.")
   return data_list, title_list

if __name__ == "__main__":
    # Exécuter la collecte de données
    collect_data()