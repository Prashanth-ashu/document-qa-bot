from pypdf import PdfReader
from docx import Document
import chromadb

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("documents")


def read_pdf(file):
    text = ""

    reader = PdfReader(file)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def read_docx(file):
    doc = Document(file)

    return "\n".join(
        para.text for para in doc.paragraphs
    )


def chunk_text(text, size=1000):
    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])

    return chunks


def ingest_document(uploaded_file):

    filename = uploaded_file.name

    if filename.endswith(".pdf"):
        text = read_pdf(uploaded_file)

    elif filename.endswith(".docx"):
        text = read_docx(uploaded_file)

    else:
        return 0

    chunks = chunk_text(text)

    for idx, chunk in enumerate(chunks):
        try:
            collection.add(
            documents=[chunk],
            ids=[f"{filename}_{idx}"]
            )
        except Exception as e:
            print(e)

    return len(chunks)