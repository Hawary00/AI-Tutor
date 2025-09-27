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
FAISS_PATH.mkdir(exist_ok=True)

# Load FAISS if exists
def load_faiss(embeddings):
    if os.path.exists(FAISS_PATH):
        return FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    return None

# Helper to process PDFs
def process_pdf(file, vector_store, embeddings, session_id=None):
    """
    Processes a PDF file and updates the FAISS vector store.

    Args:
        file: uploaded PDF file
        vector_store: FAISS vector store for the current session (or None)
        embeddings: embedding model

    Returns:
        vector_store: updated FAISS vector store
    """
    reader = PdfReader(file.name)
    text = "".join([page.extract_text() or "" for page in reader.pages])

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.create_documents([text])

    if vector_store is None:
        vector_store = FAISS.from_documents(docs, embeddings)
    else:
        vector_store.add_documents(docs)

    # Save session-specific FAISS index (optional: can be session-local folder)
    # vector_store.save_local(FAISS_PATH)
    # Save vector store to user-specific path
    if session_id:
        user_faiss_path = FAISS_PATH / session_id
        user_faiss_path.mkdir(exist_ok=True)
        vector_store.save_local(user_faiss_path)
    else:
        vector_store.save_local(FAISS_PATH)
    return vector_store
