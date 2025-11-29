from __future__ import annotations

from Models import GenerateRequest, GenerateResponse
from Config import load_config
from Providers import BaseProvider, MockProvider, ProviderError, get_provider


def generate_text(request: GenerateRequest) -> GenerateResponse:
    """
    Placeholder LLM gateway. Extend with real provider calls (OpenAI/DeepSeek).
    """
    config = load_config()
    provider = request.provider or config.provider

    try:
        client: BaseProvider = get_provider(provider, config)
        text, usage = client.generate(prompt=request.prompt, max_tokens=request.max_tokens)
        resolved_provider = client.name
    except ProviderError as exc:
        # Fall back to mock so the service can still run.
        fallback = MockProvider()
        text, usage = fallback.generate(prompt=request.prompt, max_tokens=request.max_tokens)
        usage.update({"error": str(exc), "fallback_from": provider})
        resolved_provider = fallback.name

    return GenerateResponse(text=text, provider=resolved_provider, usage=usage)
