import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from market import fetch_market_prices


async def main():
    print("Testing market service...\n")

    state = "Telangana"
    district = "Hyderabad"

    try:
        print("1️⃣ Fetching all commodities:")
        result = await fetch_market_prices(state, district)
        print(result)
        print("\n")

        print("2️⃣ Fetching specific commodity (Rice):")
        result = await fetch_market_prices(state, district, commodity="Rice")
        print(result)
        print("\n")

    except Exception as e:
        print("❌ Error occurred:")
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
