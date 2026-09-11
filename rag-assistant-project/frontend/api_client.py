import os
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

def check_health() -> bool:
    """Check if backend API /health is reachable."""
    try:
        url = f"{API_BASE_URL}/health"
        resp = requests.get(url, timeout=5)
        return resp.status_code == 200 and resp.json().get("status") == "ok"
    except Exception:
        return False

def ask_question(question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
    """Call backend API POST /query with question."""
    url = f"{API_BASE_URL}/query"
    payload = {"question": question}
    if top_k is not None:
        payload["top_k"] = top_k

    response = requests.post(url, json=payload, timeout=60)
    if response.status_code != 200:
        try:
            error_detail = response.json().get("detail", response.text)
        except Exception:
            error_detail = response.text
        raise RuntimeError(f"API Error ({response.status_code}): {error_detail}")

    return response.json()
