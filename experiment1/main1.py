#pip install openai==0.28
#pip install pinecone-client
import openai
from pinecone import Pinecone
import streamlit as st

# Nastavení přístupových klíčů pomocí Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace Pinecone
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("fischatbot")

def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def retrieve_similar_texts(query, top_k=5):
    try:
        query_embedding = get_embedding(query)
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        matches = []
        for match in result['matches']:
            score = match['score']
            chunk_index = match['metadata'].get('chunk_index', 'No chunk index available')
            source = match['metadata'].get('source', 'No source available')
            chunk_text = match['metadata'].get('chunk_text', 'No chunk text available')
            matches.append({'score': score, 'chunk_index': chunk_index, 'source': source, 'chunk_text': chunk_text})
        return matches
    except Exception as e:
        st.error(f"Chyba při vyhledávání textů: {e}")
        return []

# Funkce pro ukládání výsledků do souboru, včetně generované odpovědi a spotřeby tokenů
def save_results_to_file(results, response, token_usage, filename="outputs1.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        # Uložení každého výsledku do souboru
        for i, result in enumerate(results, 1):
            line = (f"{i}. Skóre: {result['score']}, "
                    f"Číslo chunku: {result['chunk_index']}, "
                    f"Zdroj: {result['source']}, "
                    f"Text: {result['chunk_text']}\n")
            file.write(line)
        
        # Zápis generované odpovědi a spotřeby tokenů
        file.write(f"\nGenerovaná odpověď: {response}\n")
        file.write(f"Spotřeba tokenů: {token_usage}\n")
        file.write("\n" + "-" * 50 + "\n\n")  # Oddělení jednotlivých dotazů

# Globální proměnná pro uchování historie dotazů a odpovědí
history = []  


def generate_response(query, retrieved_texts):
    global history
    
    # Sestavení kontextu z nalezených textů
    context = "\n\n".join([
        f"Zdroj {i + 1}: Skóre: {match['score']}, Číslo chunku: {match['chunk_index']}, Text: {match['chunk_text']}"
        for i, match in enumerate(retrieved_texts) if 'chunk_text' in match
    ])
    
    # Přidání historie do promptu
    history_text = "\n".join([f"Otázka: {q}\nOdpověď: {a}" for q, a in history])
    prompt = f"{history_text}\n\nNásledující texty jsou relevantní k dotazu:\n\n{context}\n\nOtázka: {query}\nOdpověď:"

    try:
        # Generování odpovědi pomocí OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based solely on provided texts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        # Uložení odpovědi a aktualizace historie
        answer = response['choices'][0]['message']['content'].strip()
        history.append((query, answer))  # Uložení dotazu a odpovědi do historie
        
        # Získání spotřeby tokenů
        token_usage = response['usage']['total_tokens']
        
        # Uložení výsledků, generované odpovědi a spotřeby tokenů do souboru
        save_results_to_file(retrieved_texts, answer, token_usage)
        
        return answer
    except Exception as e:
        st.error(f"Chyba při generování odpovědi: {e}")
        return "Omlouvám se, došlo k chybě při generování odpovědi."

# Streamlit aplikace
st.title("Testovací RAGbot")
st.write("Experimentální Verze 1")

# Vstup uživatele
query = st.text_input("Zadejte svůj dotaz:")

if query:
    with st.spinner("Vyhledávání relevantních textů..."):
        # Vyhledání podobných textů
        retrieved_texts = retrieve_similar_texts(query, top_k=5)
        
        # Zobrazení nalezených textů
        st.subheader("Nalezené texty:")
        for i, text in enumerate(retrieved_texts, 1):
            st.write(f"{i}. Skóre: {text['score']}, Číslo chunku: {text['chunk_index']}, Zdroj: {text['source']}, Text: {text['chunk_text']}")

        # Generování odpovědi
        st.subheader("Generovaná odpověď:")
        response = generate_response(query, retrieved_texts)
        st.write(response)




#query = "Informace o přijímacím řízení na univerzitě"
#results = retrieve_similar_texts(query, top_k=5)

