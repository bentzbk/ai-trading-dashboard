import os
import requests

# Load Hugging Face Inference API credentials from environment variables
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACEAPIURL")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACEAPIKEY")

def query_huggingface_model(payload):
    """
    Query the Hugging Face model with the given payload.
    """
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
