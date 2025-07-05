import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alpaca config
ALPACA_API_BASE = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Hugging Face config
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def alpaca_headers():
    return {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
        "Content-Type": "application/json"
    }

@app.get("/api/recommendations")
def get_recommendations():
    # 1. Get Alpaca account and positions
    account_url = f"{ALPACA_API_BASE}/v2/account"
    positions_url = f"{ALPACA_API_BASE}/v2/positions"
    account_data = requests.get(account_url, headers=alpaca_headers()).json()
    positions_data = requests.get(positions_url, headers=alpaca_headers()).json()

    # 2. Market data (Alpaca data API v2 for quotes)
    # For demo, let's use a fixed list of symbols
    symbols = ["AAPL", "MSFT", "GOOG"]
    market_data = {}
    for symbol in symbols:
        quote_url = f"{ALPACA_API_BASE}/v2/stocks/{symbol}/quotes/latest"
        resp = requests.get(quote_url, headers=alpaca_headers())
        market_data[symbol] = resp.json()

    # 3. Feed to Hugging Face AI model
    payload = {
        "inputs": {
            "account": account_data,
            "positions": positions_data,
            "market": market_data
        }
    }
    hf_headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    hf_response = requests.post(HUGGINGFACE_API_URL, headers=hf_headers, json=payload)
    recommendations = hf_response.json()

    return {
        "recommendations": recommendations,
        "account": account_data,
        "positions": positions_data,
        "market": market_data
    }

@app.post("/api/execute_trades")
async def execute_trades(request: Request):
    body = await request.json()
    trades = body.get("trades", [])
    results = []
    orders_url = f"{ALPACA_API_BASE}/v2/orders"
    for trade in trades:
        # You might need to adapt keys to your Hugging Face output
        order = {
            "symbol": trade['symbol'],
            "qty": trade['quantity'],
            "side": trade['action'].lower(),  # 'buy' or 'sell'
            "type": "limit" if 'limit_price' in trade else "market",
            "time_in_force": "day"
        }
        if 'limit_price' in trade:
            order["limit_price"] = trade["limit_price"]
        resp = requests.post(orders_url, headers=alpaca_headers(), json=order)
        results.append({
            "trade": trade,
            "status": resp.status_code,
            "response": resp.json()
        })
    return {"results": results}
