import re

def clean_headline(text):
    text = re.sub(r'[\x00-\x1F\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_price(val):
    try:
        return float(val)
    except Exception:
        return None

def parse_news(news_items):
    cleaned = []
    for item in news_items:
        cleaned.append({
            "headline": clean_headline(item.get("headline", "")),
            "timestamp": item.get("timestamp")
        })
    return cleaned

def parse_market_data(market_data):
    return {
        "symbol": market_data.get("symbol"),
        "price": normalize_price(market_data.get("price")),
        "volume": market_data.get("volume"),
        "timestamp": market_data.get("timestamp")
    }

def preprocess_stream(alpaca_data, tradingview_data, news_data):
    return {
        "alpaca": [parse_market_data(d) for d in alpaca_data],
        "tradingview": [parse_market_data(d) for d in tradingview_data],
        "news": parse_news(news_data)
    }
