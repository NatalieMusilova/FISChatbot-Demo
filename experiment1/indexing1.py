#pip install openai==0.28
#pip install pinecone-client
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

# Funkce pro extrakci textu z webové stránky
def extract_text_from_web(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Zkontrolujeme, zda nedošlo k chybě
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ')
        return text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the page: {url} - Error: {e}")
        return ""  # Vrátíme prázdný text při selhání

# Funkce pro očištění textu a vytvoření metadat
def clean_text_and_create_metadata(text, source_url):
    # Odstranění nepotřebných HTML tagů, speciálních znaků a nadbytečných mezer
    cleaned_text = text.replace('\n', ' ').replace('\r', '').strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Odstranění přebytečných mezer
    cleaned_text = re.sub(r'[^\w\s.,?!-]', '', cleaned_text)  # Odstranění speciálních znaků

    # Odstranění nežádoucího textu (autor, copyright, cookies informace)
    cleaned_text = re.sub(
        r"(Kontakt|"
        r"Programy magisterského studia Fakulta informatiky a statistiky  Vysoká škola ekonomická v Praze Partneři.*?Kurzy pro veřejnost Vzdělání středních škol VŠE FIS Magisterské studium Programy magisterského studia Programy magisterského studia|"
        r"Kontakt|"
        r"O programu Autor Webmaster FIS webmasterFISvse.*?Clarity Uložit nastavení|"
        r"Programy bakalářského studia  Fakulta informatiky a statistiky  Vysoká škola ekonomická v Praze Partneři.*?Vzdělání středních škol VŠE FIS Bakalářské studium Programy bakalářského studia Programy bakalářského studia|"
        r"Fakulta informatiky a statistiky  Vysoká škola ekonomická v Praze Partneři Absolventi MERCH.*?VŠE FIS Zájemci o studium Doktorské studium Programy doktorského studia Programy doktorského studia Programy doktorského studia|"
        r"Faculty of Informatics and Statistics  Prague University of Economics and Business Ask students anything! FIS MERCH.*?ISM ISM ISM Sorry, your browser does not allow direct display of this embedded content. Show content...|"
        r"Would you like to stay in contact with us.*?Maps Microsoft Clarity Save settings|"
        r"Faculty of Informatics and Statistics  Prague University of Economics and Business Ask students anything.*?allow direct display of this embedded content. Show content...|"
        r"lease enter the security code EDA.*?Maps Microsoft Clarity Save settings|"
        r"Fakulta informatiky a statistiky  Vysoká škola ekonomická v Praze Partneři Absolventi.*?Kurzy pro veřejnost Vzdělání středních škol VŠE FIS|"
        r"en English version Autor Webmaster FIS.*?Clarity Uložit nastavení|"
        r"Veškeré informace nalezneš zde . Kalendář přijímacího řízení.*?Clarity Uložit nastavení|"
        r"Termíny přijímaček na VŠ  Scio SCIO Hlavní navigace.*?Čeština Čeština Úvod|"
        r"Co se vám může hodit Jak NSZ probíhají Krok.*?PeckaDesign|"
        r"Scio SCIO Hlavní navigace scio.*?Čeština Úvod Detail fakulty|"
        r"420 234 705 555.*?PeckaDesign|"
        r"Autor Webmaster FIS webmasterFIS.*?Clarity Uložit nastavení|"
        r"Jak na to.*?Clarity Uložit nastavení|"
        r"Portál jednotné digitální brány VŠE v Praze.*?na VŠE Stipendia na VŠE Stipendia na VŠE|"
        r"Autor Dominik Proch.*?Clarity Uložit nastavení|"
        r"Vysoká škola ekonomická v Praze Střední školy Absolventi.*?VŠE Předpisy Poplatky spojené se studiem v akademickém roce 20242025|"
        r"Odpovědná osoba doc. Ing. Pavel Hnátviz Článek 5 odstavec 1 Stipendijního řádu VŠE aClarity Uložit nastavení|"
        r"Ubytovací stipendium  Koleje VŠE v Praze  Vysoká škola ekonomická v.*?viz Článek 5 odstavec 1 Stipendijního řádu VŠE a|"
        r"Autor Centrální ubytování ubytovanivse.*?Clarity Uložit nastavení|"
        r"Stipendijní řád Vysoké školy ekonomické v Praze  Vysoká.*?Mezinárodní spolupráce VŠE Předpisy Stipendijní řád Vysoké školy ekonomické v Praze Stipendijní řád Vysoké školy ekonomické v Praze|"
        r"Tento stipendijní řád nabývá účinnosti podle.*?Clarity Uložit nastavení|"
        r"O programu Autor Webmaster FIS webmasterFISvse.*?Clarity Uložit nastavení)",
        '',
        cleaned_text,
        flags=re.DOTALL
    )

    # Generování metadat pro daný textový úsek
    metadata = {
        "source": source_url,  # URL původu textu
    }
    return cleaned_text, metadata

# Seznam URL pro extrakci textu (uveden v příloze D)
urls = [
    "https://fis.vse.cz/magisterske-studium/magisterske-programy/",
    "https://fis.vse.cz/bakalarske-studium/bakalarske-programy/",
    "https://fis.vse.cz/doktorske-studium/doktorske-programy/",
    "https://fis.vse.cz/english/about/about-the-programmes/ism/",
    "https://fis.vse.cz/english/about/about-the-programmes/economic-data-analysis/",
    "https://fis.vse.cz/bakalarske-studium/informace-pro-cizince/",
    "https://fis.vse.cz/bakalarske-studium/prijimaci-rizeni/",
    "https://edu.vse.cz/",
    "https://www.scio.cz/terminy-prijimacek-na-vs",
    "https://www.scio.cz/detail-fakulty?facultyId=112",
    "https://fis.vse.cz/magisterske-studium/prijimaci-rizeni/",
    "https://fis.vse.cz/magisterske-studium/informace-pro-cizince-mgr/",
    "https://fis.vse.cz/doktorske-studium/prijimaci-rizeni/",
    "https://databusiness.cz/mba-programy-data-business/mba-program-vse-data-analytics-for-business-management/",
    "https://databusiness.cz/english/mba-it-management-business-transformation-powered-by-cios/",
    "https://studyfinance.vse.cz/financovani-studia/stipendia-na-vse/",
    "https://www.vse.cz/predpisy/poplatky-spojene-se-studiem-v-akademickem-roce-2024-2025-2/",
    "https://suz.vse.cz/zajemci-o-ubytovani/rady-a-tipy/ubytovaci-stipendium/",
    "https://www.vse.cz/predpisy/stipendijni-rad-vse/",
]

all_texts = []
for url in urls:
    print(f"Processing URL: {url}")
    raw_text = extract_text_from_web(url)

    # Pokud je text prázdný, přeskočíme další zpracování
    if not raw_text:
        print(f"No content to process for URL: {url}")
        continue

    cleaned_text, metadata = clean_text_and_create_metadata(raw_text, url)

    # Rozdělení textu na úseky
    chunk_size = 256 #postupně vyzkoušet 370, 512, 640, 768, 1024
    chunk_overlap = 10 #postupně vyzkoušet 20, 40, 60, 80, 100
    start = 0
    chunks = []
    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))  # Zajistíme, že nepřekročíme délku textu
        chunk_text = cleaned_text[start:end]
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_start"] = start  # Pozice začátku chunku
        chunk_metadata["chunk_end"] = end      # Pozice konce chunku
        chunks.append((chunk_text, chunk_metadata))
        start += chunk_size - chunk_overlap  # Posun s překryvem
        
    all_texts.extend(chunks)  # Přidáme všechny chunky k výsledkům

# Uložíme chunky do Pinecone
for i, (chunk_text, chunk_metadata) in enumerate(all_texts):
    chunk_metadata["chunk_index"] = i
    chunk_metadata["chunk_text"] = chunk_text  # Přidání chunk_text do metadat
    embedding = get_embedding(chunk_text)
    vector_id = f"combined_chunk_{i}"
    index.upsert([(vector_id, embedding, chunk_metadata)])

# Zjistíme celkový počet chunků
total_chunks = len(all_texts)
print("Celkový počet chunků:", total_chunks)

for i, (chunk_text, chunk_metadata) in enumerate(all_texts):
    if i in [0, 1, 2]:  # Zadejte indexy chunků, které chcete vytisknout
        print(f"Chunk {i + 1}:")
        print(f"Text: {chunk_text}")
        print(f"Metadata: {chunk_metadata}")
        print("-" * 40)  # Oddělovač pro přehlednost
