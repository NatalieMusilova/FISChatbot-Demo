#pip install openai==0.28
#pip install pinecone-client
import pinecone
import openai
from pinecone import Pinecone
import streamlit as st



# Nastavení přístupových klíčů pomocí Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]


pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("fischatbot")


def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']


def retrieve_similar_texts(query, top_k=5):
    # Převod dotazu na vektor
    query_embedding = get_embedding(query)

    # Vyhledávání podobných vektorů v Pinecone
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Výpis pouze požadovaných položek: score, chunk_index, source a query
    print(f"Query: {query}")
    for match in result['matches']:
        score = match['score']
        chunk_index = match['metadata'].get('chunk_index', 'No chunk index available')
        source = match['metadata'].get('source', 'No source available')
        print(f"Score: {score}, Chunk Index: {chunk_index}, Source: {source}")
        
    return result['matches']

# Funkce pro generování odpovědi
def generate_response(query, retrieved_texts):
    context = " ".join(retrieved_texts)
    prompt = f"{context}\n\nOtázka: {query}\nOdpověď:"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response['choices'][0]['text'].strip()

# Streamlit aplikace
st.title("Retrieval-Augmented Generation (RAG) Chatbot")
st.write("Zadejte svůj dotaz a chatbot vám poskytne odpověď na základě relevantních textů.")

# Vstup uživatele
query = st.text_input("Zadejte svůj dotaz:")

if query:
    with st.spinner("Vyhledávání relevantních textů..."):
        # Vyhledání podobných textů
        retrieved_texts = retrieve_similar_texts(query, top_k=5)
        
        # Zobrazení nalezených textů
        st.subheader("Nalezené texty:")
        for i, text in enumerate(retrieved_texts, 1):
            st.write(f"{i}. {text}")

        # Generování odpovědi
        st.subheader("Generovaná odpověď:")
        response = generate_response(query, retrieved_texts)
        st.write(response)


#query = "Informace o přijímacím řízení na univerzitě"
#results = retrieve_similar_texts(query, top_k=5)

