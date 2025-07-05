from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve static files (JS, CSS, etc.) under /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at the root
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join("static", "index.html"))
