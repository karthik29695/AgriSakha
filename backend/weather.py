import os
import logging
import httpx
from fastapi import HTTPException

# ==================== LOGGER ====================
log = logging.getLogger("agrisakha-weather")

# ==================== CONFIG ====================
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


# ==================== ADVISORY LOGIC ====================
def generate_farming_advisory(weather_data: dict) -> dict:
    """
    Generate farming advisory and extreme weather warnings
    based on current weather conditions.
    """

    temp = weather_data.get("temperature")
    condition = weather_data.get("condition", "").lower()
    wind_speed = weather_data.get("wind_speed", 0)

    advisories = []
    warnings = []

    # ---------- TEMPERATURE BASED ----------
    if temp is not None:
        if temp >= 40:
            warnings.append(
                "🚨 Heatwave warning: Extremely high temperatures detected. "
                "Avoid outdoor farm activities during daytime."
            )
            advisories.append(
                "Provide frequent irrigation and shade for crops. Mulching is recommended."
            )

        elif 35 <= temp < 40:
            advisories.append(
                "High temperature alert: Irrigate crops early morning or late evening to reduce evaporation."
            )

        elif temp <= 5:
            warnings.append(
                "🚨 Cold wave warning: Very low temperatures detected."
            )
            advisories.append(
                "Protect crops from frost using coverings or light irrigation at night."
            )

        elif 5 < temp <= 10:
            advisories.append(
                "Low temperature alert: Monitor crops for cold stress."
            )

    # ---------- WEATHER CONDITION BASED ----------
    if "rain" in condition:
        advisories.append(
            "Rainfall expected. Ensure proper field drainage and avoid pesticide spraying."
        )

    if "storm" in condition or "thunder" in condition:
        warnings.append(
            "🚨 Thunderstorm warning: Strong winds and lightning expected."
        )
        advisories.append(
            "Secure farm structures and avoid field work during storms."
        )

    if "cyclone" in condition:
        warnings.append(
            "🚨 Cyclone alert: Severe weather conditions expected."
        )
        advisories.append(
            "Harvest mature crops early and secure irrigation equipment."
        )

    if "fog" in condition or "mist" in condition:
        advisories.append(
            "Foggy conditions expected. Monitor crops for fungal diseases."
        )

    if "clear" in condition and not advisories:
        advisories.append(
            "Weather conditions are suitable for regular farming activities."
        )

    # ---------- WIND BASED ----------
    if wind_speed >= 10:
        warnings.append(
            "🚨 High wind warning: Wind speeds are high."
        )
        advisories.append(
            "Avoid spraying pesticides or fertilizers during strong winds."
        )

    # ---------- FALLBACK ----------
    if not advisories:
        advisories.append(
            "Monitor weather conditions regularly and plan farming activities accordingly."
        )

    return {
        "farming_advisory": " ".join(advisories),
        "extreme_warnings": warnings
    }


# ==================== WEATHER FETCH ====================
async def fetch_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather information using OpenWeatherMap API
    and generate farming advisories.
    """

    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Weather service is not configured. Set OPENWEATHER_API_KEY."
        )

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                OPENWEATHER_API_URL,
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            weather_info = {
                "temperature": round(data["main"]["temp"]),
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"].title(),
                "city": data.get("name"),
                "wind_speed": data.get("wind", {}).get("speed", 0)
            }

            advisory_data = generate_farming_advisory(weather_info)

            return {
                **weather_info,
                **advisory_data
            }

        except httpx.HTTPStatusError as e:
            log.error(
                f"OpenWeatherMap API error: "
                f"{e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch weather data."
            )

        except Exception as e:
            log.error(f"Unexpected error fetching weather: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while fetching weather."
            )
