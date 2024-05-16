import json
import os
import streamlit as st
from openai import OpenAI
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from fpdf import FPDF

API_KEYS_FILE = "api_keys.json"
COMMENTS_FILE = "comments.json"
CHAT_HISTORY_FILE = "chat_history.json"

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file)

def build_vector_store(texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform(texts).toarray()
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index, vectorizer

def query_vector_store(index, vectorizer, query, texts, k=5):
    query_vector = vectorizer.transform([query]).toarray()
    distances, indices = index.search(query_vector, k)
    return [texts[i] for i in indices[0]]

def query_comments_with_llm(api_key, query, comments):
    index, vectorizer = build_vector_store(comments)
    relevant_comments = query_vector_store(index, vectorizer, query, comments)
    client = OpenAI(base_url="http://localhost:1234/v1", api_key=api_key)
    completion = client.chat.completions.create(
        model="microsoft/Phi-3-mini-4k-instruct-gguf",
        messages=[
            {"role": "system", "content": "Use the provided comments to answer the query."},
            {"role": "user", "content": f"Comments: {relevant_comments}\n\nQuery: {query}"}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

def fetch_models_from_lm_studio(api_key):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key=api_key)
    models = client.models.list()
    return [model.id for model in models.data]

def save_chat_history_as_pdf(chat_history, file_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for chat in chat_history:
        pdf.multi_cell(0, 10, f"Q: {chat['query']}\nA: {chat['response']}\n\n")
    pdf.output(file_path)

def chat_interface_feature():
    api_keys = load_json(API_KEYS_FILE)
    comments_data = load_json(COMMENTS_FILE)
    chat_history = load_json(CHAT_HISTORY_FILE)

    st.header("Chat Interface")
    api_key_name = st.selectbox("Select an API Key for LLM", options=list(api_keys.keys()))
    api_key = api_keys.get(api_key_name, "")

    if api_key:
        models = fetch_models_from_lm_studio(api_key)
        model_name = st.selectbox("Select a Model", options=models)

    st.header("Load Comments")
    selected_comments_ref = st.selectbox("Select Comments Reference", options=list(comments_data.keys()))

    if st.button("Load Comments"):
        if selected_comments_ref:
            loaded_comments = comments_data[selected_comments_ref]
            st.success(f"Loaded comments for '{selected_comments_ref}'")
            st.text_area("Loaded Comments", value="\n".join(loaded_comments), height=300)

    st.header("Chat with Comments")
    if selected_comments_ref:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = {}

        if selected_comments_ref not in st.session_state["chat_history"]:
            st.session_state["chat_history"][selected_comments_ref] = []

        query = st.text_input("Enter your query")
        if st.button("Send"):
            if query:
                loaded_comments = comments_data[selected_comments_ref]
                response = query_comments_with_llm(api_key, query, loaded_comments)
                st.session_state["chat_history"][selected_comments_ref].append({"query": query, "response": response})
                save_json(CHAT_HISTORY_FILE, st.session_state["chat_history"])

        st.header("Chat History")
        if selected_comments_ref in st.session_state["chat_history"]:
            for chat in st.session_state["chat_history"][selected_comments_ref]:
                st.markdown(f'<div style="background-color: #e8f4f8; padding: 10px; margin: 10px 0;"><b>Q:</b> {chat["query"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0;">A: {chat["response"]}</div>', unsafe_allow_html=True)

            if st.button("Download Chat History as PDF"):
                file_path = f"{selected_comments_ref}_chat_history.pdf"
                save_chat_history_as_pdf(st.session_state["chat_history"][selected_comments_ref], file_path)
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=file_path,
                        mime="application/pdf"
                    )
