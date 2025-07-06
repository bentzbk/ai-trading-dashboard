import os
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from typing import List, Dict, Any
from jose import JWTError, jwt
import pyotp

# Alpaca SDK
from alpaca.trading.client import TradingClient

# --- CONFIGURATION ---
SECRET_KEY = "super-secret-key"  # Change for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

USERNAME = "bentzi"
PASSWORD = "Yaffo2021"  # Set your password here
TOTP_SECRET = "JBSWY3DPEHPK3PXP"  # Generate your own base32 secret for authenticator app

app = FastAPI()

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory AI action log
ai_action_log: List[Dict[str, Any]] = []

# Dummy trade ideas for demonstration (replace with real logic)
DUMMY_TRADES = [
    {"symbol": "AAPL", "quantity": 10, "action": "buy"},
    {"symbol": "TSLA", "quantity": 5, "action": "sell"}
]

def authenticate_user(username: str, password: str, otp: str):
    if username != USERNAME or password != PASSWORD:
        return False
    totp = pyotp.TOTP(TOTP_SECRET)
    return totp.verify(otp)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != USERNAME:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    otp: str = Form(...)
):
    if not authenticate_user(username, password, otp):
        raise HTTPException(status_code=400, detail="Incorrect username, password, or OTP code")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
