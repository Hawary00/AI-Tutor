# PDF processing + FAISS logic
import os
from pathlib import Path
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


# Get project root (parent of "src")
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Store FAISS index at project root
FAISS_PATH = PROJECT_ROOT / "faiss_index"


# Load FAISS if exists
def load_faiss(embeddings):
    if os.path.exists(FAISS_PATH):
        return FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

# Helper to process PDFs
def process_pdf(file, vector_store, embeddings):
    reader = PdfReader(file.name)
    text = "".join([page.extract_text() or "" for page in reader.pages])

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.create_documents([text])

    if vector_store is None:
        vector_store = FAISS.from_documents(docs, embeddings)
    else:
        vector_store.add_documents(docs)

    vector_store.save_local(FAISS_PATH)
    return vector_store
