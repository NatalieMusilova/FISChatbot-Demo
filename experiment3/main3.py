#pip install openai==0.28
#pip install pinecone-client
import openai
from pinecone import Pinecone
import streamlit as st
from datetime import datetime

# Nastavení přístupových klíčů pomocí Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Inicializace Pinecone
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("fischatbot")

def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def save_unanswered_query(query, filename="questions_for_processing3.txt"):
    """Ukládá otázky bez relevantních výsledků do souboru společně s datem."""
    with open(filename, "a", encoding="utf-8") as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Otázka: {query}\nČas: {current_time}\n")
        file.write("\n" + "-" * 50 + "\n\n")

def save_no_results_to_file(query, response="Omlouvám se, ale nejsou k dispozici žádná relevantní data k vašemu dotazu.", filename="outputs3.txt"):
    """Ukládá záznamy bez relevantních výsledků do outputs3.txt."""
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"Původní uživatelský dotaz: {query}\n")
        file.write(f"Vygenerovaná odpověď modelem: {response}\n")
        file.write(f"Verze experimentu: 3a\n") ##--------------------------------------------změnit
        file.write(f"Minimální skóre podobnosti: 0.82\n")  # Pevně nastavené minimální skóre ---------
        file.write(f"Maximální skóre podobnosti: 0.82\n")  # Pevně nastavené maximální skóre ---------
        file.write(f"Spotřeba tokenů: 0\n")  # Žádná spotřeba tokenů
        file.write(f"Spotřeba tokenů - Vstupní (prompt): 0\n")  # Žádná spotřeba tokenů
        file.write(f"Spotřeba tokenů - Výstupní (completion): 0\n")  # Žádná spotřeba tokenů
        file.write("\n" + "-" * 50 + "\n\n")  # Oddělení jednotlivých dotazů

def retrieve_similar_texts(query, top_k=2): 
    try:
        query_embedding = get_embedding(query)

        # Filtr pro vector_id, které začínají na 'text_query'
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={
                "metadata_field_name": {"$eq": "text_query"}
            }
        )

        # Zobrazení celé odpovědi pro ladění
        #st.subheader("Celá odpověď ze služby Pinecone (ladicí výpis):")
        #st.write(result)

        matches = []
        for match in result['matches']:
            score = match['score']
            if score >= 0.81:  # Filtrujeme pouze vektory s minimálním skóre 0,8------------------------zmenit
                chunk_text = match['metadata'].get('chunk_text', 'No chunk text available')
                matches.append({'score': score, 'chunk_text': chunk_text})

        # Pokud nejsou žádné relevantní výsledky, uložíme otázku do souboru
        if not matches:
            save_unanswered_query(query)
            save_no_results_to_file(query)  # Uložíme i do outputs3.txt
        
        return matches
    except Exception as e:
        st.error(f"Chyba při vyhledávání textů: {e}")
        return []


# Funkce pro ukládání výsledků do souboru, včetně generované odpovědi a spotřeby tokenů
def save_results_to_file(query, response, min_score, max_score, token_usage, prompt_tokens, completion_tokens, filename="outputs3.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        # Zápis informací o dotazu a odpovědi
        file.write(f"Původní uživatelský dotaz: {query}\n")
        file.write(f"Vygenerovaná odpověď modelem: {response}\n")
        file.write(f"Verze experimentu: 3a\n")  ###------------------------------------------------------změnit
        file.write(f"Minimální skóre podobnosti: {min_score}\n")
        file.write(f"Maximální skóre podobnosti: {max_score}\n")
        file.write(f"Spotřeba tokenů: {token_usage}\n")
        file.write(f"Spotřeba tokenů - Vstupní (prompt): {prompt_tokens}\n")
        file.write(f"Spotřeba tokenů - Výstupní (completion): {completion_tokens}\n")
        file.write("\n" + "-" * 50 + "\n\n")  # Oddělení jednotlivých dotazů


# Globální proměnná pro uchování historie dotazů a odpovědí
history = []  


# Inicializace historie pomocí session_state
if 'history' not in st.session_state:
    st.session_state.history = []  # Inicializace historie jako prázdného seznamu při prvním běhu

def generate_response(query, retrieved_texts):
    if not retrieved_texts:
        return "Omlouvám se, ale nejsou k dispozici žádná relevantní data k vašemu dotazu."

    # Získání minimálního a maximálního skóre z nalezených textů
    if retrieved_texts:
        min_score = min(match['score'] for match in retrieved_texts)
        max_score = max(match['score'] for match in retrieved_texts)
    else:
        min_score, max_score = None, None

    # Sestavení kontextu z nalezených textů
    context = "\n\n".join([
        f"Text: {match['chunk_text']}"
        for match in retrieved_texts if 'chunk_text' in match
    ])

    # Sestavení historie pomocí seznamu 'messages'
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based solely on provided texts."}
    ]
    messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant specializing in providing information to prospective students of the Faculty of Informatics and Statistics (FIS). "
            "Your responses should be based exclusively on the provided FIS materials. "
        )
    }
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
        prompt_tokens = response['usage']['prompt_tokens']
        completion_tokens = response['usage']['completion_tokens']

        # Uložení relevantních výsledků do souboru
        save_results_to_file(query, answer, min_score, max_score, token_usage, prompt_tokens, completion_tokens)

        return answer
    except Exception as e:
        st.error(f"Chyba při generování odpovědi: {e}")
        return "Omlouvám se, došlo k chybě při generování odpovědi."




####################
def retrieve_and_respond(query, top_k=1):
    """
    Pokusí se najít jeden embedding s filtrem pro `text_response` a minimálním skóre 0.90.
    Pokud takový embedding existuje, uloží data do souboru a vrátí chunk_text jako odpověď.
    Pokud ne, provede sekundární vyhledávání a generování odpovědi.
    """
    try:
        # Vytvoření embeddingu pro dotaz
        query_embedding = get_embedding(query)

        # Primární dotaz pro hledání embeddingu s filtrem "text_response"
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={
                "metadata_field_name": {"$eq": "text_response"}
            }
        )

        # Zpracování výsledků
        matches = []
        for match in result.get('matches', []):
            score = match['score']
            if score >= 0.90:  # Minimální skóre 0.90-----------------------------------------------zmenit
                chunk_text = match['metadata'].get('chunk_text', 'No chunk text available')
                metadata_field_name = match['metadata'].get('metadata_field_name', 'N/A')
                matches.append({
                    "score": score,
                    "chunk_text": chunk_text,
                    "metadata_field_name": metadata_field_name
                })

        # Zobrazení nalezených textů
        #st.subheader("Nalezené texty:")
        #for i, match in enumerate(matches, 1):
            #st.write(f"{i}. Skóre: {match['score']}, Text: {match['chunk_text']}, Metadata: {match['metadata_field_name']}")

        # Pokud je nalezen alespoň jeden relevantní výsledek
        if matches:
            best_match = matches[0]
            response = best_match['chunk_text']

            # Uložení výsledků do souboru
            save_results_to_file(
                query=query,
                response=response,
                min_score=best_match['score'],
                max_score=best_match['score'],
                token_usage=0,  # Žádná spotřeba tokenů při přímé odpovědi
                prompt_tokens=0,
                completion_tokens=0
            )

            return response

        # Pokud nebyly nalezeny relevantní výsledky, přechází k sekundárnímu vyhledávání
        retrieved_texts = retrieve_similar_texts(query, top_k=2)

        # Zobrazení nalezených textů ze sekundárního vyhledávání
        #st.subheader("Sekundárně nalezené texty:")
        #for i, match in enumerate(retrieved_texts, 1):
            #st.write(f"{i}. Skóre: {match['score']}, Text: {match['chunk_text']}")

        # Generování odpovědi pomocí sekundárního vyhledávání
        return generate_response(query, retrieved_texts)

    except Exception as e:
        st.error(f"Chyba při vyhledávání a odpovídání: {e}")
        return "Omlouvám se, došlo k chybě při zpracování vašeho dotazu."



####################


# Streamlit aplikace
st.title("Testovací RAGbot")
st.write("Experimentální Verze 3a") ##############------------------------------------------ změnit

# Vstup uživatele
query = st.text_input("Zadejte svůj dotaz:")


if query:
    with st.spinner("Vyhledávání relevantních textů..."):
        # Nový přístup s prioritním vyhledáním konkrétního embeddingu
        st.subheader("Generovaná odpověď:")
        response = retrieve_and_respond(query)  # Použijeme novou funkci
        st.write(response)
        
        # Zobrazení nalezených textů
        #st.subheader("Nalezené texty:")
        #for i, text in enumerate(retrieved_texts, 1):
            #st.write(f"{i}. Skóre: {text['score']}, Text: {text['chunk_text']}")        

        










