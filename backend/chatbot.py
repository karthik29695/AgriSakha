from gemini_client import call_gemini_with_rotation
from utils import clean_text, safe_translate, chunk_text

import logging
import threading
from typing import List

import numpy as np
import faiss
import fitz  # PyMuPDF
import io
from PIL import Image
from fastapi import HTTPException, UploadFile

# ==================== OCR ====================
try:
    import pytesseract
    HAVE_TESS = True
except Exception:
    HAVE_TESS = False

# ==================== LOCAL EMBEDDINGS ====================
try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBED_AVAILABLE = True
except Exception:
    SentenceTransformer = None
    LOCAL_EMBED_AVAILABLE = False

log = logging.getLogger("agrisakha-chatbot")

# ==================== EMBEDDINGS ====================
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"
local_embedder = None

if LOCAL_EMBED_AVAILABLE:
    try:
        local_embedder = SentenceTransformer(LOCAL_EMBED_MODEL)
    except Exception as e:
        log.error(f"Failed to load local embedding model: {e}")
        LOCAL_EMBED_AVAILABLE = False

# ==================== FAISS STATE ====================
index_lock = threading.Lock()
index = None
DIM = None
chunks: List[str] = []


# ==================== FAISS HELPERS ====================
def init_faiss(dim: int):
    global index, DIM
    with index_lock:
        index = faiss.IndexFlatL2(dim)
        DIM = dim


def add_embeddings(embeddings: np.ndarray, texts: List[str]):
    global index, chunks
    if embeddings is None or not texts:
        return

    _, d = embeddings.shape
    with index_lock:
        if index is None or d != DIM:
            init_faiss(d)
        index.add(embeddings.astype("float32"))
        chunks.extend(texts)


def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype="float32")

    if not local_embedder:
        raise HTTPException(503, "Local embedding model not available.")

    return np.asarray(
        local_embedder.encode(texts, convert_to_numpy=True),
        dtype="float32"
    )


# ==================== DOCUMENT EXTRACTION ====================
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    parts = []

    for page in doc:
        text = (page.get_text("text") or "").strip()

        # OCR fallback for scanned PDFs
        if not text and HAVE_TESS:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img, lang="eng")

        if text:
            parts.append(text)

    doc.close()
    return "\n\n".join(parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    if not HAVE_TESS:
        raise HTTPException(503, "OCR service not available.")

    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return pytesseract.image_to_string(image, lang="eng")


# ==================== DOCUMENT PROCESSING ====================
async def process_document(file: UploadFile) -> dict:
    """
    Processes PDF or Image documents for RAG.
    """

    content_type = file.content_type or ""
    data = await file.read()

    if content_type == "application/pdf":
        text = extract_text_from_pdf(data)

    elif content_type.startswith("image/"):
        text = extract_text_from_image(data)

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload PDF or image."
        )

    if not text.strip():
        raise HTTPException(400, "Could not extract text from document.")

    chunks_list = chunk_text(text)
    embeddings = embed_texts(chunks_list)
    add_embeddings(embeddings, chunks_list)

    log.info(f"Indexed {len(chunks_list)} chunks from {file.filename}")

    return {
        "filename": file.filename,
        "chunks_indexed": len(chunks_list),
        "source": "pdf" if content_type == "application/pdf" else "image_ocr"
    }


# ==================== CHAT ====================
async def chat_with_context(message: str, lang: str = "en") -> str:
    if not message:
        raise HTTPException(400, "Message cannot be empty.")

    system_prompt = (
        "You are a friendly AI assistant for farmers. "
        "You help with crops, government policies, and market insights. "
        "Answer clearly and concisely."
    )

    context = ""
    if index and index.ntotal > 0:
        q_emb = embed_texts([message])
        _, I = index.search(q_emb, k=min(5, index.ntotal))
        retrieved = [chunks[i] for i in I[0] if 0 <= i < len(chunks)]
        context = "\n\n".join(retrieved)

    if context:
        prompt = (
            f"{system_prompt}\n\n"
            f"Use the following context to answer:\n"
            f"---\n{context}\n---\n\n"
            f"Question: {message}"
        )
    else:
        prompt = f"{system_prompt}\n\nQuestion: {message}"

    try:
        resp = await call_gemini_with_rotation(prompt, model_name="gemini-2.5-flash")
        answer = clean_text(resp.text if resp else "")
        return safe_translate(answer, lang)

    except Exception as e:
        log.error(f"Chatbot error: {e}")
        raise HTTPException(503, "AI service unavailable.")
