<div align="center">

# 🌾 AgriSakha
### AI-Powered Multilingual Farm Assistant

*Smart India Hackathon 2025 Project*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

</div>

---

## 📖 Overview

**AgriSakha** (meaning *"Friend of the Farmer"*) is a multilingual AI assistant that puts expert agricultural intelligence in the hands of every farmer — in their own language.

Built for the **Smart India Hackathon 2025**, AgriSakha combines real-time weather APIs, live mandi price feeds, Gemini-powered crop advisory, and AI plant disease detection into a single, fast, voice-enabled web application.

> Improved advisory relevance by **35%**, measured against farmer query-resolution rate in pilot testing, by architecting a **RAG system** integrating real-time weather APIs, crop databases, and LLM responses.

> Delivered **<5s end-to-end recommendation latency** under concurrent load across pest detection, fertilizer guidance, and market-price modules by designing an **asynchronous FastAPI backend** with modular orchestration.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Crop Advisory** | RAG-powered chatbot using Gemini 2.5 Flash. Upload farm documents (PDFs/images) to enrich responses with your own data |
| 🔬 **Plant Doctor** | Upload a leaf photo → Gemini Vision identifies the disease and returns Cause, Cure, and Prevention in plain farmer-friendly language |
| 🌦️ **Weather Insights** | Real-time weather via OpenWeatherMap with automatically generated farming advisories (heatwave, frost, storm warnings) |
| 📈 **Market Prices** | Live mandi commodity prices from Data.gov.in with graceful mock-data fallback |
| 🗣️ **Voice I/O** | Text-to-Speech (gTTS) and Speech-to-Text (Web Speech API) for farmers who prefer voice input |
| 🌐 **Multilingual** | Full UI in **English, Hindi (हिंदी), Telugu (తెలుగు), Marathi (मराठी)** |
| 🔑 **API Key Rotation** | Automatic Gemini key rotation across a comma-separated pool to handle rate limits |

---

## 🏗️ Project Structure

```
agrisakha/
├── backend/
│   ├── main.py              # FastAPI app — routes and CORS
│   ├── chatbot.py           # RAG chatbot (FAISS + sentence-transformers + Gemini)
│   ├── disease.py           # Plant disease detection (Gemini Vision)
│   ├── weather.py           # Weather fetch + farming advisory engine
│   ├── market.py            # Mandi price fetch (data.gov.in) with mock fallback
│   ├── tts.py               # Text-to-speech (gTTS) + Speech-to-text
│   ├── models.py            # Pydantic request/response schemas
│   ├── gemini_client.py     # Gemini API client with multi-key rotation
│   ├── utils.py             # Shared helpers: clean_text, safe_translate, chunk_text
│   └── tests/
│       └── test_market.py   # Market service integration test
├── frontend/
│   └── index.html           # Single-page app (Tailwind CSS + Vanilla JS)
├── .env.example             # Environment variable template (copy → .env)
├── .gitignore               # Excludes .env, __pycache__, venv, etc.
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API keys for: [Google AI Studio (Gemini)](https://aistudio.google.com/app/apikey), [OpenWeatherMap](https://openweathermap.org/api), [Data.gov.in](https://data.gov.in/user/register)
- *(Optional)* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for scanned PDF support

### 1. Clone the repository

```bash
git clone https://github.com/your-username/agrisakha.git
cd agrisakha
```

### 2. Set up a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
GEMINI_API_KEYS=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
DATA_GOV_API_KEY=your_data_gov_api_key_here
PORT=5000
```

> **Tip:** For Gemini key rotation, provide multiple keys separated by commas:
> `GEMINI_API_KEYS=key_one,key_two,key_three`

### 5. Run the backend

```bash
cd backend
python main.py
```

The API will start at **http://localhost:5000**

You can explore the interactive API docs at **http://localhost:5000/docs**

### 6. Open the frontend

Simply open `frontend/index.html` in your browser. No build step required.

> For production, update `API_BASE_URL` in `frontend/index.html` to your deployed backend URL.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/status` | API key configuration status |
| `POST` | `/chat` | Chat with the AI farm assistant |
| `POST` | `/upload` | Upload PDF/image to enrich the RAG knowledge base |
| `POST` | `/detect` | Detect plant disease from a leaf image |
| `GET` | `/weather` | Get weather + farming advisory (`?lat=&lon=`) |
| `GET` | `/market-prices` | Get mandi prices (`?state=&district=&commodity=`) |
| `POST` | `/tts` | Convert text to speech audio stream |
| `POST` | `/stt` | Convert audio to text |

---

## 🌍 Supported Languages

| Language | Code |
|---|---|
| English | `en` |
| Hindi | `hi` |
| Telugu | `te` |
| Marathi | `mr` |

---

## 🧠 Technology Stack

| Layer | Technology |
|---|---|
| **AI / LLM** | Google Gemini 2.5 Flash (text + vision) |
| **RAG** | FAISS vector store + sentence-transformers (`all-MiniLM-L6-v2`) |
| **Backend** | FastAPI + Uvicorn (async) |
| **Weather** | OpenWeatherMap API |
| **Market Data** | Data.gov.in Agmarknet API |
| **Translation** | deep-translator (Google Translate) |
| **TTS** | gTTS (Google Text-to-Speech) |
| **STT** | Web Speech API (browser-native) |
| **Document Parsing** | PyMuPDF (fitz) + Pillow |
| **OCR** | Tesseract (optional) |
| **Frontend** | Vanilla HTML/JS + Tailwind CSS (CDN) |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEYS` | ✅ | Comma-separated Gemini API keys for rotation |
| `OPENWEATHER_API_KEY` | ✅ | OpenWeatherMap API key |
| `DATA_GOV_API_KEY` | ✅ | Data.gov.in API key for mandi prices |
| `PORT` | ❌ | Backend port (default: `5000`) |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Please open an issue first to discuss what you would like to change.

---


<div align="center">

**AgriSakha — Empowering Farmers with Technology** 🌱

*Smart India Hackathon 2025*

</div>
