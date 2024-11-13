import json
import re
import requests
from bs4 import BeautifulSoup
import openai
import os
from pinecone import Pinecone, ServerlessSpec

# Nastavení přístupových klíčů
openai.api_key = '***'
pinecone_api_key ="***"
pinecone_environment = '***'

# Inicializace Pinecone klienta pomocí nové metody
pc = Pinecone(api_key=pinecone_api_key)
index_name = "fischatbot"

# Kontrola existence indexu
if index_name in pc.list_indexes().names():
    # Přístup k existujícímu indexu
    index = pc.Index(index_name)
    # Vymazání všech vektorů v indexu
    index.delete(delete_all=True)
else:
    # Vytvoření indexu, pokud neexistuje
    pc.create_index(
        name=index_name,
        dimension=1536,  # Dimenze 1536 pro model `text-embedding-ada-002`
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region=pinecone_environment
        )
    )
    # Přístup k nově vytvořenému indexu
    index = pc.Index(index_name)

# Funkce pro získání embeddingu
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

# Načtení textů a metadat ze souboru
with open('/content/text_pairs2.txt', 'r', encoding='utf-8') as file:
    texts_and_metadata = json.load(file)

# Smyčka pro generování embeddingů a jejich ukládání do Pinecone
for i, item in enumerate(texts_and_metadata):
    # Text a metadata z aktuální položky
    text = item["question"]
    metadata = item["metadata"]

    # Generování embeddingu pro text
    embedding = get_embedding(text)

    # Vytvoření jedinečného vector_id, například pomocí číselného ID
    vector_id = f"text_query_{i}"

    # Upsert do Pinecone indexu
    index.upsert([(vector_id, embedding, metadata)])

    # Výpis stavu pro kontrolu
    print(f"Uložen embedding pro text '{text}' s ID '{vector_id}'")
