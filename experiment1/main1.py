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

def retrieve_similar_texts(query, top_k=4): ###-----------------------------------------------změnit 
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
def save_results_to_file(query, response, min_score, max_score, token_usage, filename="outputs1.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        # Zápis informací o dotazu a odpovědi
        file.write(f"Původní uživatelský dotaz: {query}\n")
        file.write(f"Vygenerovaná odpověď modelem: {response}\n")
        file.write(f"Verze experimentu: 1d\n")  ###------------------------------------------------------změnit
        file.write(f"Minimální skóre podobnosti: {min_score}\n")
        file.write(f"Maximální skóre podobnosti: {max_score}\n")
        file.write(f"Spotřeba tokenů: {token_usage}\n")
        file.write("\n" + "-" * 50 + "\n\n")  # Oddělení jednotlivých dotazů

# Globální proměnná pro uchování historie dotazů a odpovědí
history = []  


# Inicializace historie pomocí session_state
if 'history' not in st.session_state:
    st.session_state.history = []  # Inicializace historie jako prázdného seznamu při prvním běhu

def generate_response(query, retrieved_texts):
    # Získání minimálního a maximálního skóre z nalezených textů
    if retrieved_texts:
        min_score = min(match['score'] for match in retrieved_texts)
        max_score = max(match['score'] for match in retrieved_texts)
    else:
        min_score, max_score = None, None

    # Sestavení kontextu z nalezených textů
    context = "\n\n".join([
        f"Zdroj: {match['source']}, Text: {match['chunk_text']}"
        for match in retrieved_texts if 'chunk_text' in match
    ])

    # Sestavení historie pomocí seznamu 'messages'
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based solely on provided texts."}
    ]

    # Přidání minulých dotazů a odpovědí do historie
    for i, (q, a) in enumerate(st.session_state.history, 1):
        combined_content = f"Dotaz č. {i}: {q} | Odpověď č. {i}: {a}"
        messages.append({"role": "assistant", "content": combined_content})

    # Přidání aktuálního kontextu a dotazu
    messages.append({"role": "user", "content": f"Následující texty jsou relevantní k dotazu:\n\n{context}\n\nOtázka: {query}\nOdpověď:"})

    # Zobrazení historie, která se použije pro generování odpovědi, a kontrolního výpisu struktury `messages`
    with st.expander("Zobrazit historii použité pro generování odpovědi", expanded=True):
        if messages:
            # Kontrolní výpis struktury `messages`
            st.write("**Struktura messages:**", messages)
        else:
            st.write("Žádné zprávy nejsou k dispozici pro zobrazení.")

    try:
        # Generování odpovědi pomocí OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.5
        )

        # Uložení odpovědi a aktualizace historie
        answer = response['choices'][0]['message']['content'].strip()
        st.session_state.history.append((query, answer))

        # Získání spotřeby tokenů
        token_usage = response['usage']['total_tokens']

        # Uložení relevantních výsledků do souboru
        save_results_to_file(query, answer, min_score, max_score, token_usage)

        return answer
    except Exception as e:
        st.error(f"Chyba při generování odpovědi: {e}")
        return "Omlouvám se, došlo k chybě při generování odpovědi."







# Streamlit aplikace
st.title("Testovací RAGbot")
st.write("Experimentální Verze 1d") ##############------------------------------------------ změnit

# Vstup uživatele
query = st.text_input("Zadejte svůj dotaz:")

if query:
    with st.spinner("Vyhledávání relevantních textů..."):
        # Vyhledání podobných textů
        retrieved_texts = retrieve_similar_texts(query, top_k=4) ##############------------------------------------------ změnit

        # Generování odpovědi
        st.subheader("Generovaná odpověď:")
        response = generate_response(query, retrieved_texts)
        st.write(response)
        
        # Zobrazení nalezených textů
        st.subheader("Nalezené texty:")
        for i, text in enumerate(retrieved_texts, 1):
            st.write(f"{i}. Skóre: {text['score']}, Číslo chunku: {text['chunk_index']}, Zdroj: {text['source']}, Text: {text['chunk_text']}")
