# AI Trading Dashboard Prototype

This project is a prototype for an AI-powered trading dashboard, using Hugging Face for recommendations and the Alpaca Paper Trading API for simulated trading.

## Project Structure

```
ai-trading-dashboard/
│
├── backend/
│   ├── main.py            # FastAPI backend (API handler)
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Example env file for secrets (do NOT commit your real .env)
│
├── frontend/
│   └── index.html         # Dashboard UI
│
└── README.md              # Instructions
```

## Backend Setup

1. Copy `backend/.env.example` to `backend/.env` and fill in your keys:

    ```
    ALPACA_API_KEY=your_alpaca_paper_trading_key
    ALPACA_SECRET_KEY=your_alpaca_paper_trading_secret
    HUGGINGFACE_API_URL=https://api-inference.huggingface.co/models/your-model-id
    HUGGINGFACE_API_KEY=hf_your_key_here
    ```

2. Install Python dependencies:

    ```
    cd backend
    pip install -r requirements.txt
    ```

3. Start the FastAPI backend:

    ```
    uvicorn main:app --reload
    ```

   The backend will be available at `http://localhost:8000`.

## Frontend Setup

1. Open `frontend/index.html` in your browser.
   - For local testing, you can use VSCode Live Server or any static file server.

2. The dashboard will display:
    - TradingView widgets (charts, screener, economic calendar)
    - Buttons to get AI trade recommendations and execute them in Alpaca paper trading

## Usage

1. Click "Get Today’s Trade Ideas" to fetch AI trade suggestions.
2. Click "Execute All Recommended Trades (Paper)" to send those trades to Alpaca paper trading.
3. Results and trade statuses will appear below the buttons.

## Deployment

- Deploy the backend (e.g. [Render](https://render.com/), [Railway](https://railway.app/), [Heroku](https://heroku.com/)).
- Add your environment variables as cloud secrets.
- Update the frontend API URLs if your backend is not on localhost.

## Notes

- Hugging Face model output must return a `trades` array, with each trade having at least `symbol`, `quantity`, and `action` (`buy` or `sell`). Optionally, include `limit_price`.
- All credentials must be kept secret and out of version control.
- This code is a prototype and should be adapted for production use, with error handling, logging, and security enhancements as needed.
