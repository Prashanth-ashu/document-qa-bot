import streamlit as st
import chromadb
import google.generativeai as genai
import os

from ingest import ingest_document
from dotenv import load_dotenv
import os

load_dotenv()



api_key = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

client = chromadb.PersistentClient(path="./db")

collection = client.get_or_create_collection(
    "documents"
)

st.title("📚 Document Q&A Bot")

uploaded_file = st.file_uploader(
    "Upload PDF or DOCX",
    type=["pdf", "docx"]
)

if uploaded_file:

    count = ingest_document(uploaded_file)

    st.success(
        f"{count} chunks indexed successfully"
    )

question = st.text_input(
    "Ask a Question"
)

if st.button("Get Answer"):

    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    context = "\n".join(
        results["documents"][0]
    )

    prompt = f"""
You are a document assistant.

Use ONLY the context below.

Context:
{context}

Question:
{question}

If answer not found,
say:
'I cannot find the answer in the provided documents.'
"""

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    response = model.generate_content(
        prompt
    )

    st.write(response.text)

    st.subheader("Sources")

    for doc in results["documents"][0]:
        st.write(doc[:200])