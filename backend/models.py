from typing import Optional
from datetime import date

from pydantic import BaseModel, Field


# ==================== CHAT ====================
class ChatRequest(BaseModel):
    message: str
    lang: str = "en"


class ChatResponse(BaseModel):
    reply: str


# ==================== TTS ====================
class TTSRequest(BaseModel):
    text: str
    lang: str = "en"


# ==================== SPEECH TO TEXT ====================
class STTResponse(BaseModel):
    text: str
    language: str


# ==================== CROPS ====================
class AddCropRequest(BaseModel):
    crop_name: str
    sowing_date: date
    variety: Optional[str] = None
    area_acres: Optional[float] = Field(None, gt=0)


# ==================== WEATHER ====================
class WeatherResponse(BaseModel):
    temperature: int
    condition: str
    description: str
    city: Optional[str]


# ==================== MARKET ====================
class MarketRecord(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: Optional[str]
    arrival_date: str
    min_price: Optional[str]
    max_price: Optional[str]
    modal_price: int


class MarketResponse(BaseModel):
    count: int
    records: list[MarketRecord]
    source: str
