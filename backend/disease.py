import io
import logging
from PIL import Image

from fastapi import HTTPException, UploadFile
from utils import clean_text, safe_translate

# ==================== GEMINI ====================
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    genai = None
    GENAI_AVAILABLE = False


log = logging.getLogger("agrisakha-disease")


# ==================== GEMINI VISION ====================
async def detect_disease_from_image(image_file: UploadFile) -> str:
    """
    Uses Gemini Vision to identify plant disease from a leaf image.
    Returns disease name or 'Healthy'.
    """

    if not GENAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI vision service is not available."
        )

    if not image_file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed."
        )

    try:
        image_bytes = await image_file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        prompt = (
            "Identify the disease in this plant leaf image. "
            "If the leaf appears healthy, respond with 'Healthy'. "
            "Respond with ONLY the disease name or 'Healthy'."
        )

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await model.generate_content_async([prompt, pil_image])

        disease = (response.text or "").strip()

        if not disease:
            raise HTTPException(
                status_code=500,
                detail="Failed to detect disease."
            )

        log.info(f"Disease detected: {disease}")
        return disease

    except HTTPException:
        raise

    except Exception as e:
        log.error(f"Disease detection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during disease detection."
        )


async def explain_disease(disease: str, lang: str = "en") -> str:
    """
    Uses Gemini to explain disease with Cause, Cure, Prevention.
    """

    if not disease:
        raise HTTPException(
            status_code=400,
            detail="Disease name is required."
        )

    try:
        prompt = (
            f"The detected plant disease is '{disease}'. "
            "Explain it in simple, farmer-friendly language with:\n"
            "Cause:\nCure:\nPrevention:\n"
        )

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await model.generate_content_async(prompt)

        explanation = (response.text or "No explanation available.").strip()
        explanation = clean_text(explanation)
        return safe_translate(explanation, lang)

    except Exception as e:
        log.error(f"Disease explanation failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI explanation service unavailable."
        )
