from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

@app.get("/")
def read_root():
    return FileResponse(os.path.join("static", "index.html"))

app.mount("/static", StaticFiles(directory="static"), name="static")
