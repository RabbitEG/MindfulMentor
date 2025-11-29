import requests
from Config import ORCHESTRATOR_BASE


def call_orchestrator(endpoint: str, payload: dict) -> dict:
    url = f"{ORCHESTRATOR_BASE}{endpoint}"
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
