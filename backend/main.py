import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

# ==================== LOAD ENV ====================
load_dotenv()

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("agrisakha-main")

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="AgriSakha – AI-Powered Agricultural Assistant",
    version="1.0.0",
    description=(
        "AI assistant for farmers with chat, disease detection, "
        "weather, market prices, and voice support."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== IMPORT MODULES ====================
from models import (
    ChatRequest,
    TTSRequest,
)

from chatbot import (
    chat_with_context,
    process_document,
)

from disease import (
    detect_disease_from_image,
    explain_disease,
)

from weather import fetch_weather
from market import fetch_market_prices
from tts import text_to_speech, speech_to_text


# ==================== ROOT ====================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AgriSakha backend is running"
    }


# ==================== HEALTH CHECK ====================
@app.get("/status")
def status():
    return {
        "gemini_configured": bool(os.getenv("GEMINI_API_KEYS")),
        "weather_api_configured": bool(os.getenv("OPENWEATHER_API_KEY")),
        "market_api_configured": bool(os.getenv("DATA_GOV_API_KEY")),
        "services": [
            "chatbot",
            "disease-detection",
            "weather",
            "market",
            "tts",
            "stt",
        ],
    }


# ==================== CHATBOT ====================
@app.post("/chat")
async def chat(req: ChatRequest):
    reply = await chat_with_context(req.message, req.lang)
    return {"reply": reply}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    return await process_document(file)


# ==================== DISEASE DETECTION ====================
@app.post("/detect")
async def detect_disease(
    file: UploadFile = File(...),
    lang: str = Query("en")
):
    disease = await detect_disease_from_image(file)
    explanation = await explain_disease(disease, lang)

    return {
        "disease": disease,
        "explanation": explanation,
    }


# ==================== WEATHER ====================
@app.get("/weather")
async def weather(lat: float, lon: float):
    return await fetch_weather(lat, lon)


# ==================== MARKET ====================
@app.get("/market-prices")
async def market_prices(
    state: str,
    district: str,
    commodity: str | None = None
):
    return await fetch_market_prices(state, district, commodity)


# ==================== TEXT TO SPEECH ====================
@app.post("/tts")
async def tts(req: TTSRequest):
    return await text_to_speech(req.text, req.lang)


# ==================== SPEECH TO TEXT ====================
@app.post("/stt")
async def stt(
    audio: UploadFile = File(...),
    lang: str = Query("en-IN")
):
    return await speech_to_text(audio, lang)


# ==================== RUN ====================
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 5000))
    log.info(f"Starting AgriSakha backend on http://0.0.0.0:{port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
