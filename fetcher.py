import aiohttp
import logging
import pandas as pd
from typing import Optional, Dict

# Configure default logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
CONFIG = {
    "IG_API_KEY": "18ff83c5017f0707342bf6b2195607fa35b22093",
    "IG_USERNAME": "StevenAPI",
    "IG_PASSWORD": "Password123",
    "BASE_URL": "https://demo-api.ig.com/gateway/deal",
}


# Authentication Function
async def authenticate() -> Optional[Dict[str, str]]:
    """
    Authenticates with the IG API and returns headers with tokens for subsequent requests.
    Adds a default API version key in headers (version 1).
    """
    url = f"{CONFIG['BASE_URL']}/session"
    headers = {
        "X-IG-API-KEY": CONFIG["IG_API_KEY"],
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Version": "1",
    }
    payload = {
        "identifier": CONFIG["IG_USERNAME"],
        "password": CONFIG["IG_PASSWORD"],
    }

    try:
        logger.info("Authenticating with IG API...")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload,
                                    headers=headers) as response:
                response.raise_for_status(
                )  # This will raise for 4xx/5xx responses
                client_token = response.headers.get("CST")
                security_token = response.headers.get("X-SECURITY-TOKEN")

                if not client_token or not security_token:
                    logger.error("Missing tokens in authentication response.")
                    return None

                logger.info("Authentication successful.")
                return {
                    "X-IG-API-KEY": CONFIG["IG_API_KEY"],
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "CST": client_token,
                    "X-SECURITY-TOKEN": security_token,
                    "API_VERSION": "1",  # Default API version is 1
                }
    except aiohttp.ClientResponseError as e:
        logger.error(f"Request failed during authentication: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
    return None


# Fetch RSI Data
async def fetch_rsi_data(
    stock_name: str,
    resolution: str = "SECOND",
    page_size: int = 22,
    page_number: int = 1,
    max_results: int = 22,
) -> Optional[Dict[str, str]]:
    """
    Fetches historical stock data for the given stock_name.
    You can override the API version here if needed.
    """
    auth_headers = await authenticate()
    if not auth_headers:
        return {"error": "Unable to authenticate, please try again later."}

    market_data = await search_stock_in_market(stock_name, auth_headers)
    if not market_data:
        return {"error": f"Unable to fetch market data for {stock_name}"}

    epics = [market["epic"] for market in market_data.get("markets", [])]
    if not epics:
        logger.error(f"No epic key found for stock symbol: {stock_name}.")
        return {"error": "No epic key found for the provided stock symbol."}

    try:
        epic_key = epics[0]
        url = (
            f"{CONFIG['BASE_URL']}/prices/{epic_key}?resolution={resolution}"
            f"&max={max_results}&pageSize={page_size}&pageNumber={page_number}"
        )

        logger.info(
            f"Fetching market history for {stock_name} (epic: {epic_key})...")

        # Optional: You can override the API version here if needed
        auth_headers["Version"] = "3"  # Change to version 3 if needed

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=auth_headers) as response:
                response.raise_for_status()
                data = await response.json()

                # Extracting close prices
                close_prices = []

                # Loop through the list of prices
                for entry in data.get('prices',
                                      []):  # Access 'prices' key in the data
                    close_price = entry.get(
                        'closePrice')  # Get 'closePrice' for each entry

                    if close_price and isinstance(
                            close_price, dict
                    ):  # Check if 'closePrice' is a valid dictionary
                        bid = close_price.get(
                            'bid')  # Get 'bid' from 'closePrice'

                        if bid is not None:  # Only add to the list if 'bid' is not None
                            close_prices.append(bid)

                if not close_prices:
                    return {"error": "No valid close prices found."}

                # Ensure close_prices is a list of numbers (integers or floats)
                rsi_data_frame = pd.DataFrame(close_prices, columns=['Close'])

                # Make sure the DataFrame is correctly formatted and return it
                return rsi_data_frame
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error fetching RSI data: {e}")
        return {
            "error":
            f"You are not authorized to fetch market price data for {stock_name}"
        }
    except Exception as e:
        logger.error(f"Unexpected error during RSI data fetch: {e}")
        return {
            "error":
            "Can't get historic price data for now. Please try again later."
        }


# Search Stock in Market
async def search_stock_in_market(
        stock_name: str, auth_headers: Dict[str,
                                            str]) -> Optional[Dict[str, str]]:
    """
    Searches for the epic key of a stock symbol in the IG API.
    """
    url = f"{CONFIG['BASE_URL']}/markets?searchTerm={stock_name}"
    try:
        logger.info(f"Searching for stock {stock_name} in market...")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=auth_headers) as response:
                response.raise_for_status()
                data = await response.json()

                if not data.get("markets"):
                    logger.warning(
                        f"No markets found for stock symbol: {stock_name}")
                    return None

                logger.info(f"Stock {stock_name} found with market data.")
                return data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error searching for stock {stock_name}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during stock search: {e}")
    return None
