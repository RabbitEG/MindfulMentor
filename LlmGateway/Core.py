from __future__ import annotations

import datetime
from pathlib import Path

from .Models import GenerateRequest, GenerateResponse
from .Config import load_config
from .Providers import BaseProvider, MockProvider, ProviderError, get_provider

LOG_FILE = Path(__file__).resolve().parent.parent / ".logs" / "llm-gateway.log"


def _append_log(prompt: str, reply: str, provider: str, usage: dict | None):
    """
    Append prompt/response exchanges to the gateway log for debugging.
    """
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write("\n--- LLM Exchange @ " + timestamp + " ---\n")
            f.write(f"provider: {provider}\n")
            if usage:
                f.write(f"usage: {usage}\n")
            f.write("prompt:\n")
            f.write(prompt + "\n")
            f.write("reply:\n")
            f.write(reply + "\n")
    except Exception:
        # logging must never break the flow
        pass


def generate_text(request: GenerateRequest) -> GenerateResponse:
    """
    Placeholder LLM gateway. Extend with real provider calls (OpenAI/DeepSeek).
    """
    config = load_config()
    provider = request.provider or config.provider

    try:
        # client: BaseProvider = get_provider(provider, config)
        client: BaseProvider = get_provider(
            provider,
            config,
            api_key=request.api_key,
            base_url=request.base_url,
            api_model=request.api_model,
        )
        text, usage = client.generate(prompt=request.prompt, max_tokens=request.max_tokens)
        resolved_provider = client.name
    except ProviderError as exc:
        # Fall back to mock so the service can still run.
        fallback = MockProvider()
        text, usage = fallback.generate(prompt=request.prompt, max_tokens=request.max_tokens)
        usage.update({"error": str(exc), "fallback_from": provider})
        resolved_provider = fallback.name

    _append_log(request.prompt, text, resolved_provider, usage)
    return GenerateResponse(text=text, provider=resolved_provider, usage=usage)
