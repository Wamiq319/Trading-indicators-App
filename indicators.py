import pandas as pd


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> float:
  delta = data['Close'].diff()
  gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
  rs = gain / loss
  rsi = 100 - (100 / (1 + rs))
  return rsi.iloc[-1]


def calculate_macd(data: pd.DataFrame,
                   short_window: int = 12,
                   long_window: int = 26,
                   signal_window: int = 9):
  short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
  long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
  macd = short_ema - long_ema
  signal = macd.ewm(span=signal_window, adjust=False).mean()
  return macd, signal


def calculate_mfi(data: pd.DataFrame, window: int = 14) -> float:
  typical_price = (data['High'] + data['Low'] + data['Close']) / 3
  money_flow = typical_price * data['Volume']
  pos_flow = money_flow.where(typical_price.diff() > 0).rolling(window).sum()
  neg_flow = money_flow.where(typical_price.diff() < 0).rolling(window).sum()
  mfi = 100 - (100 / (1 + (pos_flow / neg_flow)))
  return mfi.iloc[-1]
