import os
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import httpx
from fastapi import HTTPException

# Logger Setup
log = logging.getLogger("agrisakha-market")

# ==================== CONFIG ====================
DATA_GOV_API_URL = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")


def get_mock_market_data(
    state: str,
    district: str,
    commodity: Optional[str] = None
) -> List[Dict]:
    """
    Generates mock market data if the live API fails or returns empty.
    """
    log.warning(f"Using mock market data for {state}, {district}.")
    today = datetime.now()

    mock_records = [
        {
            "state": state,
            "district": district,
            "market": "Gaddiannaram",
            "commodity": "Tomato",
            "variety": "Local",
            "arrival_date": (today - timedelta(days=1)).strftime("%d/%m/%Y"),
            "min_price": "2200",
            "max_price": "2500",
            "modal_price": 2400,
            "source": "mock_data",
        },
        {
            "state": state,
            "district": district,
            "market": "Bowenpally",
            "commodity": "Onion",
            "variety": "Red",
            "arrival_date": (today - timedelta(days=1)).strftime("%d/%m/%Y"),
            "min_price": "1800",
            "max_price": "2100",
            "modal_price": 1950,
            "source": "mock_data",
        },
        {
            "state": state,
            "district": district,
            "market": "Gaddiannaram",
            "commodity": "Rice",
            "variety": "Sona Masoori",
            "arrival_date": today.strftime("%d/%m/%Y"),
            "min_price": "3800",
            "max_price": "4200",
            "modal_price": 4000,
            "source": "mock_data",
        },
        {
            "state": state,
            "district": district,
            "market": "Kothapet",
            "commodity": "Brinjal",
            "variety": "Local",
            "arrival_date": today.strftime("%d/%m/%Y"),
            "min_price": "1500",
            "max_price": "1800",
            "modal_price": 1650,
            "source": "mock_data",
        },
    ]

    if commodity:
        return [
            rec
            for rec in mock_records
            if rec["commodity"].lower() == commodity.lower()
        ]

    return mock_records


async def fetch_market_prices(
    state: str,
    district: str,
    commodity: Optional[str] = None
) -> Dict:
    """
    Fetches market prices from data.gov.in.
    Falls back to mock data if the API is not configured, fails, or returns empty.
    """

    if not DATA_GOV_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Market price service is not configured. Set DATA_GOV_API_KEY."
        )

    # Format inputs to title case
    state = state.title()
    district = district.title()

    log.info(
        f"Fetching market prices: State={state}, District={district}, Commodity={commodity}"
    )

    # Build parameters
    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": "100",
    }

    # Add filters (data.gov.in API syntax)
    filters = {
        "State": state,
        "District": district,
    }

    if commodity:
        filters["Commodity"] = commodity.title()

    for key, value in filters.items():
        params[f"filters[{key}]"] = value

    log.info(f"API URL: {DATA_GOV_API_URL}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                DATA_GOV_API_URL,
                params=params,
                timeout=30.0,
            )

            log.info(f"Full request URL: {response.url}")

            if response.status_code != 200:
                log.error(f"API Error {response.status_code}: {response.text[:500]}")
                mock_records = get_mock_market_data(state, district, commodity)
                return {
                    "count": len(mock_records),
                    "records": mock_records,
                    "source": "mock_data_fallback_error",
                    "error": f"HTTP {response.status_code}",
                }

            try:
                data = response.json()
            except Exception as json_error:
                log.error(f"JSON parsing error: {json_error}")
                mock_records = get_mock_market_data(state, district, commodity)
                return {
                    "count": len(mock_records),
                    "records": mock_records,
                    "source": "mock_data_json_error",
                }

            log.info(f"API Response keys: {data.keys()}")
            log.info(f"Records count in response: {len(data.get('records', []))}")

            records = data.get("records", [])

            if not records:
                log.warning("API returned 0 records. Using mock data.")
                mock_records = get_mock_market_data(state, district, commodity)
                return {
                    "count": len(mock_records),
                    "records": mock_records,
                    "source": "mock_data_empty",
                }

            processed_records = []

            for idx, rec in enumerate(records):
                try:
                    processed = {
                        "state": rec.get("state") or rec.get("State"),
                        "district": rec.get("district") or rec.get("District"),
                        "market": rec.get("market") or rec.get("Market"),
                        "commodity": rec.get("commodity") or rec.get("Commodity"),
                        "variety": rec.get("variety") or rec.get("Variety"),
                        "arrival_date": rec.get("arrival_date") or rec.get("Arrival_Date"),
                    }

                    # Handle different possible price field names
                    min_price = (
                        rec.get("min_price") or
                        rec.get("Min_x0020_Price") or
                        rec.get("Min Price") or
                        rec.get("min_x0020_price") or
                        "0"
                    )

                    max_price = (
                        rec.get("max_price") or
                        rec.get("Max_x0020_Price") or
                        rec.get("Max Price") or
                        rec.get("max_x0020_price") or
                        "0"
                    )

                    modal_price = (
                        rec.get("modal_price") or
                        rec.get("Modal_x0020_Price") or
                        rec.get("Modal Price") or
                        rec.get("modal_x0020_price") or
                        "0"
                    )

                    processed["min_price"] = str(min_price)
                    processed["max_price"] = str(max_price)

                    try:
                        processed["modal_price"] = int(float(str(modal_price).replace(",", "")))
                    except (ValueError, TypeError):
                        processed["modal_price"] = 0

                    if processed["arrival_date"]:
                        try:
                            datetime.strptime(processed["arrival_date"], "%d/%m/%Y")
                            processed_records.append(processed)
                        except ValueError:
                            try:
                                parsed_date = datetime.strptime(processed["arrival_date"], "%Y-%m-%d")
                                processed["arrival_date"] = parsed_date.strftime("%d/%m/%Y")
                                processed_records.append(processed)
                            except ValueError:
                                log.warning(f"Invalid date format in record {idx}: {processed['arrival_date']}")
                    else:
                        log.warning(f"Missing arrival_date in record {idx}")

                except (ValueError, TypeError, KeyError) as e:
                    log.warning(f"Skipping invalid record {idx}: {e}")
                    continue

            # Sort by date (newest first)
            if processed_records:
                processed_records.sort(
                    key=lambda x: datetime.strptime(x["arrival_date"], "%d/%m/%Y"),
                    reverse=True,
                )

            log.info(f"Successfully processed {len(processed_records)} records")

            return {
                "count": len(processed_records),
                "records": processed_records,
                "source": "live_data",
            }

        except httpx.TimeoutException as e:
            log.error(f"API Timeout: {e}. Using mock data.")
            mock_records = get_mock_market_data(state, district, commodity)
            return {
                "count": len(mock_records),
                "records": mock_records,
                "source": "mock_data_timeout",
            }

        except httpx.RequestError as e:
            log.error(f"Request Error: {e}. Using mock data.")
            mock_records = get_mock_market_data(state, district, commodity)
            return {
                "count": len(mock_records),
                "records": mock_records,
                "source": "mock_data_request_error",
            }

        except Exception as e:
            log.error(f"Unexpected error: {e}", exc_info=True)
            mock_records = get_mock_market_data(state, district, commodity)
            return {
                "count": len(mock_records),
                "records": mock_records,
                "source": "mock_data_fatal_error",
            }
