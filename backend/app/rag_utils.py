"""
rag_utils.py — Efficient PDF-based Retrieval Augmented Generation (RAG) helper.
Builds, caches, and queries a FAISS index from large company reports.
"""

import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# ---------- CONFIG ----------
INDEX_PATH = "backend/app/rag_index.faiss"
META_PATH = "backend/app/rag_meta.json"
EMBED_MODEL = "all-MiniLM-L6-v2"
PDF_PATH = os.getenv(
    "RAG_PDF_PATH",
    "/Users/prasunndubey/Desktop/balance-sheet-analyst/backend/app/reliance_consolidated.pdf",
)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# ----------------------------

# Cache
_model_cache = None
_index_cache = None
_meta_cache = None


# ---------- HELPERS ----------
def get_model():
    """Load the embedding model once and cache it."""
    global _model_cache
    if _model_cache is None:
        print("[INFO] Loading embedding model...")
        _model_cache = SentenceTransformer(EMBED_MODEL)
    return _model_cache


def read_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        except Exception:
            continue
    return text


def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_index_from_pdf(pdf_path: str) -> dict:
    """Builds a FAISS index from the PDF and saves it."""
    if not os.path.exists(os.path.dirname(INDEX_PATH)):
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

    print(f"[INFO] Reading PDF: {pdf_path}")
    text = read_pdf_text(pdf_path)
    chunks = chunk_text(text)
    print(f"[INFO] Chunked into {len(chunks)} sections")

    model = get_model()
    embeddings = model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)

    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    return {"status": "built", "chunks": len(chunks)}


def load_index() -> Tuple[faiss.IndexFlatL2, List[str]]:
    """Load FAISS index and metadata from disk."""
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("[WARN] No index found, building new one...")
        build_index_from_pdf(PDF_PATH)

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return index, meta


def ensure_index() -> Tuple[faiss.IndexFlatL2, List[str]]:
    """Ensure index is loaded in memory (cached)."""
    global _index_cache, _meta_cache
    if _index_cache is None or _meta_cache is None:
        _index_cache, _meta_cache = load_index()
    return _index_cache, _meta_cache


# ---------- RAG QUERY ----------
def query_rag(query: str, top_k: int = 5) -> List[str]:
    """Retrieve most relevant chunks for a given query."""
    index, meta = ensure_index()
    model = get_model()

    q_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, top_k)

    retrieved_chunks = [meta[i] for i in I[0] if i < len(meta)]
    print(f"[INFO] Retrieved {len(retrieved_chunks)} chunks for query.")
    return retrieved_chunks
