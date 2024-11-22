from datetime import datetime, timedelta
import aiohttp
import logging
import colorlog
import pandas as pd
from typing import Optional, Dict

# Configure color logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
))
logger = logging.getLogger("IGLogger")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Configuration constants
CONFIG = {
    "IG_API_KEY": "18ff83c5017f0707342bf6b2195607fa35b22093",
    "IG_USERNAME": "StevenAPI",
    "IG_PASSWORD": "Password123",
    "BASE_URL": "https://demo-api.ig.com/gateway/deal",
}

# Authentication Function
async def authenticate() -> Optional[Dict[str, str]]:
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
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                client_token = response.headers.get("CST")
                security_token = response.headers.get("X-SECURITY-TOKEN")

                if not client_token or not security_token:
                    logger.error("Missing tokens in authentication response.", exc_info=False)
                    return None

                logger.info("Authentication successful.")
                return {
                    "X-IG-API-KEY": CONFIG["IG_API_KEY"],
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "CST": client_token,
                    "X-SECURITY-TOKEN": security_token,
                    "API_VERSION": "1",
                }
    except aiohttp.ClientResponseError as e:
        logger.error(f"Request failed during authentication: {e}", exc_info=False)
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}", exc_info=False)
    return None

# Fetch RSI Data for the last 5 minutes
async def fetch_historic_data(
    stock_name: str,
    resolution: str = "SECOND",
    page_size: int = 60,
    page_number: int = 1,
    max_results: int = 60,
) -> Optional[Dict[str, str]]:
    auth_headers = await authenticate()
    if not auth_headers:
        return {"error": "Unable to authenticate, please try again later."}

    market_data = await search_stock_in_market(stock_name, auth_headers)
    if not market_data:
        return {"error": f"Unable to fetch market data for {stock_name}"}

    epics = [market["epic"] for market in market_data.get("markets", [])]
    if not epics:
        logger.error(f"No epic key found for stock symbol: {stock_name}.", exc_info=False)
        return {"error": "No epic key found for the provided stock symbol."}

    try:
        epic_key = epics[0]
        
        # Calculate time range for the last 5 minutes
        current_time = datetime.utcnow()
        from_time = (current_time - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
        to_time = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        url = (
            f"{CONFIG['BASE_URL']}/prices/{epic_key}?resolution={resolution}"
            f"&from={from_time}&to={to_time}&max={max_results}&pageSize={page_size}&pageNumber={page_number}"
        )

        logger.info(f"Fetching market history for {stock_name} (epic: {epic_key})...")

        auth_headers["Version"] = "3"  # Change to version 3 if needed

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=auth_headers) as response:
                response.raise_for_status()
                historic_data = await response.json()
                return {"historic_data": historic_data, "epic_key": epic_key}
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error fetching historic data: {e}", exc_info=False)
        return {"error": f"Unable to fetch historical market data for {stock_name}"}
    except Exception as e:
        logger.error(f"Unexpected error during historic data fetch: {e}", exc_info=False)
        return {"error": "Can't get historic price data for now. Please try again later."}

# Search Stock in Market
async def search_stock_in_market(
    stock_name: str, auth_headers: Dict[str, str]
) -> Optional[Dict[str, str]]:
    url = f"{CONFIG['BASE_URL']}/markets?searchTerm={stock_name}"
    try:
        logger.info(f"Searching for stock {stock_name} in market...")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=auth_headers) as response:
                response.raise_for_status()
                data = await response.json()

                if not data.get("markets"):
                    logger.warning(f"No markets found for stock symbol: {stock_name}", exc_info=False)
                    return None

                logger.info(f"Stock {stock_name} found with market data.")
                return data
    except aiohttp.ClientResponseError as e:
        logger.error(f"Error searching for stock {stock_name}: {e}", exc_info=False)
    except Exception as e:
        logger.error(f"Unexpected error during stock search: {e}", exc_info=False)
    return None
