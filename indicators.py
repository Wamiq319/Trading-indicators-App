import pandas as pd
import logging
import colorlog

# Configure color logging
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(name)s:%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)
logger = logging.getLogger("StockIndicators")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def ensure_dataframe(data) -> pd.DataFrame:
    """Convert data to a pandas DataFrame if it's not already one."""
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, dict):
        return pd.DataFrame(data)
    else:
        logger.error(f"Invalid data type: {type(data)}. Expected dict or DataFrame.")
        raise ValueError("Data must be a pandas DataFrame or a dictionary.")


def calculate_rsi(rsi_data_frame, period: int = 14) -> float:
    logger.debug(f"Data received for RSI calculation..")
    # Ensure 'Close' column exists in the DataFrame
    if 'Close' not in rsi_data_frame.columns:
        logger.error("'Close' column is missing in the DataFrame.")
        return None
    
    # Calculate the delta
    delta = rsi_data_frame['Close'].diff()  # Difference of 'Close' prices
    
    
    # Calculate the gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()  # Gain (positive deltas)
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  # Loss (negative deltas)
    
    # Calculate relative strength (RS) and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Handle if the DataFrame is too short for rolling window
    if len(rsi) < period:
        logger.warning("Not enough data points for RSI calculation.")
        return None
    RSI = rsi.iloc[-1]
    logger.info(f"RSI calculated: {RSI}")
    return RSI


def calculate_macd(data, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
    data = ensure_dataframe(data)  # Ensure data is a DataFrame
    logger.info("Calculating MACD...")

    if 'Close' not in data.columns:
        logger.error("'Close' column is missing in the DataFrame for MACD.")
        return None, None

    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    logger.debug(f"MACD:\n{macd}")
    logger.debug(f"Signal Line:\n{signal}")
    return macd, signal


def calculate_mfi(data, window: int = 14) -> float:
    data = ensure_dataframe(data)  # Ensure data is a DataFrame
    logger.info("Calculating MFI...")

    # Ensure necessary columns exist
    for col in ['High', 'Low', 'Close', 'Volume']:
        if col not in data.columns:
            logger.error(f"'{col}' column is missing in the DataFrame for MFI calculation.")
            return None

    try:
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        money_flow = typical_price * data['Volume']
        pos_flow = money_flow.where(typical_price.diff() > 0).rolling(window).sum()
        neg_flow = money_flow.where(typical_price.diff() < 0).rolling(window).sum()
        
        # Avoid division by zero in MFI calculation
        mfi = 100 - (100 / (1 + (pos_flow / neg_flow)))
        
        if len(mfi) < window:
            logger.warning("Not enough data points for MFI calculation.")
            return None
        
        logger.debug(f"MFI:\n{mfi}")
        return mfi.iloc[-1]
    except Exception as e:
        logger.error(f"Error calculating MFI: {e}")
        return None
