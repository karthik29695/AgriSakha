import re
from deep_translator import GoogleTranslator


# ==================== TEXT CLEANING ====================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\*{1,3}|[_`#]", "", text)
    text = text.replace("\n\n", "\n").strip()
    return re.sub(r"(\n\s*-\s*|\n\s*\*\s*)", "\n• ", text).strip()


# ==================== TRANSLATION ====================
def safe_translate(text: str, target: str) -> str:
    if not text or target.lower() in ("en", "en-in"):
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text) or text
    except Exception:
        return text


# ==================== CHUNKING ====================
def chunk_text(text: str, size: int = 1000, overlap: int = 100) -> list[str]:
    words = text.split()
    out, start = [], 0

    while start < len(words):
        end = min(start + size, len(words))
        out.append(" ".join(words[start:end]))
        start += size - overlap

    return out
