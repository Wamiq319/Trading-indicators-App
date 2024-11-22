from fetcher import fetch_rsi_data
from indicators import calculate_rsi, calculate_macd, calculate_mfi
import pandas as pd


async def check_rsi(Stock):
    """
    Fetches stock data, calculates RSI for each stock, and returns the results.
    """
    RSI_DATA_FRAME = await fetch_rsi_data(Stock, )
    return RSI_DATA_FRAME
