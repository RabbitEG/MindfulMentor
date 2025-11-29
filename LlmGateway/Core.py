from __future__ import annotations

import textwrap
from Models import GenerateRequest, GenerateResponse
from Config import load_config


def _mock_response(prompt: str) -> str:
    preview = prompt.strip().splitlines()[0][:120]
    return f"(mock) Notional model reply based on: {preview}"


def generate_text(request: GenerateRequest) -> GenerateResponse:
    """
    Placeholder LLM gateway. Extend with real provider calls (OpenAI/DeepSeek).
    """
    config = load_config()
    provider = request.provider or config.provider

    # Future: call provider-specific clients; here we just return a mock echo.
    text = _mock_response(request.prompt)
    usage = {"tokens": len(request.prompt.split()), "provider": provider}
    return GenerateResponse(text=textwrap.shorten(text, width=512, placeholder="..."), provider=provider, usage=usage)
