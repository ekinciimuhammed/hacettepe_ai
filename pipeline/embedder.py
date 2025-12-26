import requests
import time
from config import OLLAMA_BASE_URL, EMBEDDING_MODEL, MAX_RETRIES, RETRY_DELAY

def get_embedding(text):
    """
    Generates embedding for the given text using Ollama.
    Implements retry logic with backoff.
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except requests.exceptions.RequestException as e:
            print(f"Embedding attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed to generate embedding for chunk: {text[:30]}...")
                return None
