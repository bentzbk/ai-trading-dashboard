import os
import requests
import threading
import time
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

# In-memory trade log and P&L
trade_log = []
overall_pl = 0.0

def alpaca_headers():
    return {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
        "Content-Type": "application/json"
    }

def calculate_pl():
    # Simple P/L calculation: sum realized P/L on closed trades
    pl = 0.0
    for entry in trade_log:
        # Update this logic with your actual trade result structure
        if 'response' in entry and isinstance(entry['response'], dict):
            filled_qty = float(entry['response'].get('filled_qty', 0))
            filled_avg_price = float(entry['response'].get('filled_avg_price', 0))
            side = entry['trade'].get('action', 'buy')
            if side == 'sell':
                pl += filled_qty * filled_avg_price
            elif side == 'buy':
                pl -= filled_qty * filled_avg_price
    return pl

@app.get("/api/recommendations")
def get_recommendations():
    # 1. Get Alpaca account and positions
    account_url = f"{ALPACA_API_BASE}/v2/account"
    positions_url = f"{ALPACA_API_BASE}/v2/positions"
    account_data = requests.get(account_url, headers=alpaca_headers()).json()
    positions_data = requests.get(positions_url, headers=alpaca_headers()).json()

    # 2. Market data (Alpaca data API v2 for quotes)
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
    return {"results": _execute_and_log_trades(trades)}

def _execute_and_log_trades(trades):
    results = []
    orders_url = f"{ALPACA_API_BASE}/v2/orders"
    global trade_log, overall_pl
    for trade in trades:
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
        entry = {
            "trade": trade,
            "status": resp.status_code,
            "response": resp.json()
        }
        trade_log.append(entry)
        results.append(entry)
    overall_pl = calculate_pl()
    return results

@app.get("/api/trade_log")
def get_trade_log():
    return trade_log

@app.get("/api/pl")
def get_pl():
    global overall_pl
    # Always recalculate in case trades were added outside background
    overall_pl = calculate_pl()
    return {"pl": overall_pl}

def background_trader():
    while True:
        print("Auto-trader: fetching recommendations and executing trades...")
        try:
            recs = get_recommendations()
            trades = recs.get('recommendations', {}).get('trades', [])
            if trades:
                _execute_and_log_trades(trades)
        except Exception as e:
            print("Auto-trader error:", e)
        time.sleep(900)  # 15 mins

@app.on_event("startup")
def start_background_trader():
    t = threading.Thread(target=background_trader, daemon=True)
    t.start()
