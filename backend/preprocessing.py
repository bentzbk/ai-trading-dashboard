import re
import datetime
import requests

def clean_headline(text):
    # Basic cleaning: remove non-printable chars, excessive whitespace
    text = re.sub(r'[\x00-\x1F\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_price(val):
    try:
        return float(val)
    except Exception:
        return None

def parse_news(news_items):
    # Expects a list of dicts with at least 'headline' and 'timestamp'
    cleaned = []
    for item in news_items:
        cleaned.append({
            "headline": clean_headline(item.get("headline", "")),
            "timestamp": item.get("timestamp")
        })
    return cleaned

def parse_market_data(market_data):
    # Expects dict with keys like 'symbol', 'price', 'volume', etc.
    return {
        "symbol": market_data.get("symbol"),
        "price": normalize_price(market_data.get("price")),
        "volume": market_data.get("volume"),
        "timestamp": market_data.get("timestamp")
    }

def preprocess_stream(alpaca_data, tradingview_data, news_data):
    """
    - alpaca_data: list of dicts from Alpaca (bars, quotes, etc.)
    - tradingview_data: list of dicts from TradingView (e.g., signals, indicators)
    - news_data: list of dicts from MarketWatch, Yahoo Finance, etc.
    Returns a dict ready for model inference.
    """
    processed = {
        "alpaca": [parse_market_data(d) for d in alpaca_data],
        "tradingview": [parse_market_data(d) for d in tradingview_data],
        "news": parse_news(news_data)
    }
    return processed
