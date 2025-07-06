import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from data_fetcher import fetch_historical_data, fetch_live_data
from preprocessing import preprocess_stream
from trade_logic import recommend_trades
from datetime import datetime

app = FastAPI()

# Dynamically resolve static directory path and print debug info
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
print(f"STATIC DIR: {static_dir} EXISTS: {os.path.exists(static_dir)}")  # Debug print

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.post("/train-data")
async def get_train_data(request: Request):
    data = await request.json()
    symbols = data.get("symbols", ["AAPL"])
    start = data.get("start", "2023-01-01")
    end = data.get("end", "2024-01-01")
    bars = fetch_historical_data(
        symbols,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end)
    )
    return {"bars": {s: [b.dict() for b in bars[s]] for s in bars}}

@app.post("/recommend-trades")
async def recommend_trades_endpoint(request: Request):
    data = await request.json()
    alpaca_data = data.get("alpaca_data", [])
    tradingview_data = data.get("tradingview_data", [])
    news_data = data.get("news_data", [])
    processed = preprocess_stream(alpaca_data, tradingview_data, news_data)
    recommendations = recommend_trades(processed)
    return recommendations

@app.get("/live-data")
async def get_live_data(symbols: str = "AAPL"):
    symbol_list = [s.strip() for s in symbols.split(",")]
    bars = fetch_live_data(symbol_list)
    return {"bars": {s: [b.dict() for b in bars[s]] for s in bars}}
