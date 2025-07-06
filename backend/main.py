import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Dict, Any

# Alpaca SDK
from alpaca.trading.client import TradingClient

app = FastAPI()

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory AI action log
ai_action_log: List[Dict[str, Any]] = []

# Dummy trade ideas for demonstration (replace with real logic)
DUMMY_TRADES = [
    {"symbol": "AAPL", "quantity": 10, "action": "buy"},
    {"symbol": "TSLA", "quantity": 5, "action": "sell"}
]

@app.get("/get_trade_ideas")
def get_trade_ideas():
    ai_action_log.append({
        "action": "get_trade_ideas",
        "status": "success",
        "details": "Fetched dummy trade ideas",
        "timestamp": datetime.now().isoformat()
    })
    return {"trades": DUMMY_TRADES}

@app.post("/execute_trades")
async def execute_trades(request: Request):
    payload = await request.json()
    trades = payload.get("trades", [])
    results = []
    for trade in trades:
        # Simulate execution
        results.append({
            "symbol": trade["symbol"],
            "quantity": trade["quantity"],
            "action": trade["action"],
            "status": "executed"
        })
    ai_action_log.append({
        "action": "execute_trades",
        "status": "success",
        "details": f"Executed {len(trades)} trades",
        "timestamp": datetime.now().isoformat()
    })
    return {"results": results}

@app.get("/account_info")
def get_account_info():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    paper = True  # Use paper trading

    try:
        client = TradingClient(api_key, secret_key, paper=paper)
        account = client.get_account()
        equity = float(account.equity)
        last_equity = float(account.last_equity)
        buying_power = float(account.buying_power)
        pnl = equity - last_equity
        return {
            "equity": equity,
            "last_equity": last_equity,
            "buying_power": buying_power,
            "pnl": pnl
        }
    except Exception as e:
        return {
            "equity": 0.0,
            "last_equity": 0.0,
            "buying_power": 0.0,
            "pnl": 0.0,
            "error": str(e)
        }

@app.get("/ai_action_log")
def get_ai_action_log():
    return JSONResponse(content={"log": ai_action_log})
