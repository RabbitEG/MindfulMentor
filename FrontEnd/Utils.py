import requests
from Config import ORCHESTRATOR_BASE


def call_orchestrator(endpoint: str, payload: dict) -> dict:
    """Send a JSON payload to the orchestrator and normalize errors for the UI."""
    url = f"{ORCHESTRATOR_BASE}{endpoint}"
    # Disable proxy for localhost/internal service calls to avoid 502 Bad Gateway
    proxies = {
        "http": None,
        "https": None,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10, proxies=proxies)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.Timeout:
        return {
            "error": {"code": "timeout", "detail": "Orchestrator did not respond in time."},
            "meta": {"endpoint": endpoint},
        }
    except requests.exceptions.RequestException as exc:
        return {
            "error": {"code": "network_error", "detail": str(exc)},
            "meta": {"endpoint": endpoint},
        }
    except ValueError:
        return {
            "error": {"code": "bad_json", "detail": "Response could not be decoded."},
            "meta": {"endpoint": endpoint},
        }

    if data.get("error"):
        return data

    data.setdefault("meta", {}).update({"endpoint": endpoint})
    return data
