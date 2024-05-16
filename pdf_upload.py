import json
import os
import fitz  # PyMuPDF
import streamlit as st
from openai import OpenAI
from fpdf import FPDF

API_KEYS_FILE = "api_keys.json"
PDF_DATA_FILE = "pdf_data.json"
PDF_CHAT_HISTORY_FILE = "pdf_chat_history.json"

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

def query_comments_with_llm(api_key, query, comments):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key=api_key)
    completion = client.chat.completions.create(
        model="microsoft/Phi-3-mini-4k-instruct-gguf",
        messages=[
            {"role": "system", "content": "Use the provided comments to answer the query."},
            {"role": "user", "content": f"Comments: {comments}\n\nQuery: {query}"}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text.split('\n')

def save_chat_history_as_pdf(chat_history, file_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for chat in chat_history:
        pdf.multi_cell(0, 10, f"Q: {chat['query']}\nA: {chat['response']}\n\n")
    pdf.output(file_path)

def pdf_upload_feature():
    api_keys = load_json(API_KEYS_FILE)
    pdf_data = load_json(PDF_DATA_FILE)
    pdf_chat_history = load_json(PDF_CHAT_HISTORY_FILE)

    st.header("Upload and Query PDF")
    api_key_name = st.selectbox("Select an API Key", options=list(api_keys.keys()))
    api_key = api_keys.get(api_key_name, "")

    uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
    pdf_ref_name = st.text_input("Enter Reference Name for this PDF")

    if st.button("Save PDF"):
        if uploaded_pdf and pdf_ref_name:
            pdf_path = f"pdfs/{pdf_ref_name}.pdf"
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.getbuffer())

            pdf_text = extract_text_from_pdf(pdf_path)
            pdf_data[pdf_ref_name] = pdf_text
            save_json(PDF_DATA_FILE, pdf_data)
            st.success(f"PDF '{pdf_ref_name}' saved")

    st.header("Load PDF")
    selected_pdf_ref = st.selectbox("Select PDF Reference", options=list(pdf_data.keys()))

    if st.button("Load PDF"):
        if selected_pdf_ref:
            loaded_pdf_text = pdf_data[selected_pdf_ref]
            st.success(f"Loaded PDF '{selected_pdf_ref}'")
            st.text_area("Loaded PDF Text", value="\n".join(loaded_pdf_text), height=300)

    st.header("Chat with PDF")
    if selected_pdf_ref:
        if "pdf_chat_history" not in st.session_state:
            st.session_state["pdf_chat_history"] = {}

        if selected_pdf_ref not in st.session_state["pdf_chat_history"]:
            st.session_state["pdf_chat_history"][selected_pdf_ref] = []

        query = st.text_input("Enter your query")
        if st.button("Send"):
            if query:
                loaded_pdf_text = pdf_data[selected_pdf_ref]
                response = query_comments_with_llm(api_key, query, loaded_pdf_text)
                st.session_state["pdf_chat_history"][selected_pdf_ref].append({"query": query, "response": response})
                save_json(PDF_CHAT_HISTORY_FILE, st.session_state["pdf_chat_history"])

        st.header("Chat History")
        if selected_pdf_ref in st.session_state["pdf_chat_history"]:
            for chat in st.session_state["pdf_chat_history"][selected_pdf_ref]:
                st.markdown(f'<div style="background-color: #e8f4f8; padding: 10px; margin: 10px 0;"><b>Q:</b> {chat["query"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0;">A: {chat["response"]}</div>', unsafe_allow_html=True)

            if st.button("Download Chat History as PDF"):
                file_path = f"{selected_pdf_ref}_chat_history.pdf"
                save_chat_history_as_pdf(st.session_state["pdf_chat_history"][selected_pdf_ref], file_path)
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=file_path,
                        mime="application/pdf"
                    )

        if st.button("Delete Chat History"):
            del st.session_state["pdf_chat_history"][selected_pdf_ref]
            save_json(PDF_CHAT_HISTORY_FILE, st.session_state["pdf_chat_history"])
            st.success(f"Deleted chat history for '{selected_pdf_ref}'")
