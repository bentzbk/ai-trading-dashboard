import os
from datetime import datetime, timedelta

from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Load credentials from environment variables
ALPACA_API_KEY = os.getenv("ALPACAAPIKEY")
ALPACA_SECRET_KEY = os.getenv("ALPACASECRETKEY")

def fetch_historical_data(symbols=["AAPL"], start=None, end=None):
    """
    Fetch historical daily bar data for given symbols from Alpaca.
    """
    client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
    if not start:
        start = datetime.now() - timedelta(days=365)
    if not end:
        end = datetime.now()
    request = StockBarsRequest(
        symbol_or_symbols=symbols,
        start=start,
        end=end,
        timeframe=TimeFrame.Day
    )
    bars = client.get_stock_bars(request)
    return bars

def fetch_live_data(symbols=["AAPL"]):
    """
    Fetch the most recent daily bar for given symbols from Alpaca.
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return fetch_historical_data(symbols, start=yesterday, end=today)
