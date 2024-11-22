from fetcher import fetch_historic_data
from indicators import calculate_rsi
import pandas as pd
import logging
import colorlog

# Set up color logging
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

logger = logging.getLogger("StockLogger")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

async def check_rsi(stock: str):
    """
    Fetches stock data, calculates RSI for the stock, and returns the results.
    """
    try:
        logger.info("Fetching RSI data for stock: %s", stock)
        
        # Fetch historic data asynchronously
        data = await fetch_historic_data(stock)
        
        # Ensure that historic_data exists
        if 'historic_data' not in data or 'prices' not in data['historic_data']:
            logger.warning("No historical data found for stock: %s", stock)
            return {"error": "No historical data found."}
        
        historic_data = data['historic_data']
        
        # Extract close prices
        close_prices = [
            entry.get("closePrice", {}).get("bid")
            for entry in historic_data.get("prices", [])
            if entry.get("closePrice", {}).get("bid") is not None
        ]

        if not close_prices:
            logger.warning("No valid close prices found for stock: %s", stock)
            return {"error": "No valid close prices found."}

        # Create DataFrame for close prices
        rsi_data_frame = pd.DataFrame(close_prices, columns=["Close"])
        logger.info("Successfully fetched and formatted RSI data for stock: %s", stock)

        # Calculate RSI
        logger.info("Calculating RSI for stock: %s", stock)
        stock_rsi = calculate_rsi(rsi_data_frame)

        # Return the RSI data frame and the calculated RSI
        if stock_rsi is not None:
            logger.info("RSI calculation completed for stock: %s", stock)
            return {"epic_key": data.get("epic_key"), "close_prices": rsi_data_frame, "rsi_value": stock_rsi}
        else:
            logger.warning("RSI calculation failed for stock: %s", stock)
            return {"error": "RSI calculation failed."}
    
    except Exception as e:
        logger.error("An error occurred while processing stock: %s. Error: %s", stock, str(e))
        return {"error": f"An error occurred: {str(e)}"}
