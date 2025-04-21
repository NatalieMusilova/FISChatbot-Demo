#pip install openai==0.28
#pip install pinecone-client
import openai
import pinecone
import streamlit as st
from datetime import datetime
import io

# Nastavení přístupových klíčů pomocí Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace Pinecone
pinecone.init(
    api_key=st.secrets["PINECONE_API_KEY"]
)
index = pinecone.Index("fischatbot")

# Inicializace session_state proměnných
if 'history' not in st.session_state:
    st.session_state.history = []
if 'log' not in st.session_state:
    st.session_state.log = ""
if 'unanswered_log' not in st.session_state:
    st.session_state.unanswered_log = ""

def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def save_no_results_to_file(query, response="Omlouvám se, ale nejsou k dispozici žádná relevantní data k vašemu dotazu."):
    log_entry = (
        f"Původní uživatelský dotaz: {query}\n"
        f"Vygenerovaná odpověď modelem: {response}\n"
        f"Verze experimentu: Final\n"
        f"Minimální skóre podobnosti: 0.82\n"
        f"Maximální skóre podobnosti: 0.90\n"
        f"Spotřeba tokenů: 0\n"
        f"Spotřeba tokenů - Vstupní (prompt): 0\n"
        f"Spotřeba tokenů - Výstupní (completion): 0\n"
        + "-" * 50 + "\n\n"
    )
    st.session_state.unanswered_log += log_entry

def save_results_to_file(query, response, min_score, max_score, token_usage, prompt_tokens, completion_tokens, context=""):
    log_entry = (
        f"Původní uživatelský dotaz: {query}\n"
        f"Vygenerovaná odpověď modelem: {response}\n"
        f"Verze experimentu: 3a\n"
        f"Minimální skóre podobnosti: {min_score}\n"
        f"Maximální skóre podobnosti: {max_score}\n"
        f"Spotřeba tokenů: {token_usage}\n"
        f"Spotřeba tokenů - Vstupní (prompt): {prompt_tokens}\n"
        f"Spotřeba tokenů - Výstupní (completion): {completion_tokens}\n"
        f"Použitý kontext pro generování odpovědi:\n{context}\n"
        + "-" * 50 + "\n\n"
    )
    st.session_state.log += log_entry

def retrieve_similar_texts(query, top_k=2): 
    try:
        query_embedding = get_embedding(query)
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"metadata_field_name": {"$eq": "text_query"}}
        )
        matches = []
        for match in result['matches']:
            score = match['score']
            if score >= 0.82:
                chunk_text = match['metadata'].get('chunk_text', 'No chunk text available')
                matches.append({'score': score, 'chunk_text': chunk_text})
        if not matches:
            save_no_results_to_file(query)
        return matches
    except Exception as e:
        st.error(f"Chyba při vyhledávání textů: {e}")
        return []

def generate_response(query, retrieved_texts):
    if not retrieved_texts:
        return "Omlouvám se, ale nejsou k dispozici žádná relevantní data k vašemu dotazu."
    min_score = min(match['score'] for match in retrieved_texts)
    max_score = max(match['score'] for match in retrieved_texts)
    context = "\n\n".join([f"Text: {match['chunk_text']}" for match in retrieved_texts if 'chunk_text' in match])
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant specializing in providing information to prospective students of the Faculty of Informatics and Statistics (FIS). "
                "Your responses should be based exclusively on the provided FIS materials."
            )
        }
    ]
    for i, (q, a) in enumerate(st.session_state.history, 1):
        combined_content = f"Dotaz č. {i}: {q} | Odpověď č. {i}: {a}"
        messages.append({"role": "assistant", "content": combined_content})
    messages.append({"role": "user", "content": f"Následující texty jsou relevantní k dotazu:\n\n{context}\n\nOtázka: {query}\nOdpověď:"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.5,
            top_p=0.7
        )
        answer = response['choices'][0]['message']['content'].strip()
        st.session_state.history.append((query, answer))
        token_usage = response['usage']['total_tokens']
        prompt_tokens = response['usage']['prompt_tokens']
        completion_tokens = response['usage']['completion_tokens']
        save_results_to_file(query, answer, min_score, max_score, token_usage, prompt_tokens, completion_tokens, context)
        return answer
    except Exception as e:
        st.error(f"Chyba při generování odpovědi: {e}")
        return "Omlouvám se, došlo k chybě při generování odpovědi."

def retrieve_and_respond(query, top_k=1):
    try:
        query_embedding = get_embedding(query)
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"metadata_field_name": {"$eq": "text_response"}}
        )
        matches = []
        for match in result.get('matches', []):
            score = match['score']
            if score >= 0.90:
                chunk_text = match['metadata'].get('chunk_text', 'No chunk text available')
                metadata_field_name = match['metadata'].get('metadata_field_name', 'N/A')
                matches.append({"score": score, "chunk_text": chunk_text, "metadata_field_name": metadata_field_name})
        if matches:
            best_match = matches[0]
            response = best_match['chunk_text']
            save_results_to_file(query, response, best_match['score'], best_match['score'], 0, 0, 0)
            return response
        retrieved_texts = retrieve_similar_texts(query, top_k=2)
        return generate_response(query, retrieved_texts)
    except Exception as e:
        st.error(f"Chyba při vyhledávání a odpovídání: {e}")
        return "Omlouvám se, došlo k chybě při zpracování vašeho dotazu."

# Streamlit UI
st.title("Testovací chatbot Fakulty informatiky a statistiky VŠE v Praze")
st.write("""
Tento chatbot byl vytvořen v rámci diplomové práce, která se zaměřuje na minimalizaci nákladů generativních dialogových systémů pomocí přístupu Retrieval-Augmented Generation (RAG).

🤖 Chatbot je určen k odpovídání na dotazy týkající se informací o studiu na Fakultě informatiky a statistiky VŠE v Praze. 
Jeho znalosti jsou omezeny na předem definovaná témata.

❗ **Chatbot v této demoverzi odpovídá na otázky v těchto oblastech:**

• 🎓 **Studijní programy** – bakalářské, magisterské, doktorské a MBA  
• 📅 **Požadavky na přijetí** – dokumenty, podmínky, termíny přihlášek  
• 📝 **Přijímací řízení** – průběh zkoušek, testy  
• 🌍 **Zahraniční studenti** – jazykové požadavky, nostrifikace, víza  
• 💸 **Finanční záležitosti** – školné, stipendia a další možnosti podpory
""")

query = st.text_input("Zadejte dotaz a ověřte, jak si chatbot poradí! 👇")

if query:
    with st.spinner("Vyhledávání relevantních textů..."):
        st.subheader("Generovaná odpověď:")
        response = retrieve_and_respond(query)
        st.write(response)

# Stahování logů jako TXT
if st.session_state.log:
    st.download_button(
        label="📄 Stáhnout log jako TXT",
        data=io.StringIO(st.session_state.log),
        file_name="chatbot_log.txt",
        mime="text/plain"
    )

if st.session_state.unanswered_log:
    st.download_button(
        label="❓ Stáhnout nezodpovězené dotazy",
        data=io.StringIO(st.session_state.unanswered_log),
        file_name="unanswered_log.txt",
        mime="text/plain"
    )









