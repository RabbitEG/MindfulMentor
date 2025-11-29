from __future__ import annotations

import textwrap
from typing import Dict, Tuple

import httpx

from Config import LlmConfig


class ProviderError(RuntimeError):
    """Custom error so callers can decide how to fall back."""


class BaseProvider:
    name: str

    def generate(self, prompt: str, max_tokens: int) -> Tuple[str, Dict]:
        raise NotImplementedError


class MockProvider(BaseProvider):
    name = "mock"

    def _mock_response(self, prompt: str) -> str:
        preview = prompt.strip().splitlines()[0][:120]
        return f"(mock) Notional model reply based on: {preview}"

    def generate(self, prompt: str, max_tokens: int) -> Tuple[str, Dict]:
        text = self._mock_response(prompt)
        usage = {"prompt_tokens": len(prompt.split()), "completion_tokens": 0, "total_tokens": len(prompt.split())}
        return textwrap.shorten(text, width=512, placeholder="..."), usage


class TinyLocalProvider(BaseProvider):
    """
    Minimal local model using a tiny GPT-2 checkpoint.

    The goal is to have *something* runnable without API keys. Swap the
    model_id in config for a different local model as needed.
    """

    name = "tiny-local"

    def __init__(self, model_id: str):
        self.model_id = model_id
        self._pipeline = None

    def _lazy_load(self):
        if self._pipeline is not None:
            return
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            import torch  # noqa: F401
        except ImportError as exc:
            raise ProviderError(
                "Local provider requires transformers and torch. "
                "Install them or switch provider to mock/openai."
            ) from exc
        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        model = AutoModelForCausalLM.from_pretrained(self.model_id)
        # keep on CPU for portability
        self._pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)

    def generate(self, prompt: str, max_tokens: int) -> Tuple[str, Dict]:
        self._lazy_load()
        outputs = self._pipeline(
            prompt,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,
            num_return_sequences=1,
            pad_token_id=self._pipeline.tokenizer.eos_token_id,
        )
        generated = outputs[0]["generated_text"]
        completion = generated[len(prompt) :].strip() if generated.startswith(prompt) else generated
        completion = completion or generated
        usage = {
            "model": self.model_id,
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(completion.split()),
            "total_tokens": len(prompt.split()) + len(completion.split()),
        }
        return completion, usage


class OpenAICompatibleProvider(BaseProvider):
    """
    Lightweight OpenAI/DeepSeek compatible client using httpx only.

    This keeps dependencies small while making it easy to point to an API
    backend later (set base_url/api_key/api_model in env).
    """

    name = "openai"

    def __init__(self, api_key: str | None, base_url: str | None, model: str, timeout: float):
        if not api_key:
            raise ProviderError("LLM_API_KEY is required for openai-like provider")
        self.api_key = api_key
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, max_tokens: int) -> Tuple[str, Dict]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ProviderError(f"API provider failed: {exc.response.text}") from exc
        data = resp.json()
        if not data.get("choices"):
            raise ProviderError(f"API provider returned no choices: {data}")
        message = data["choices"][0].get("message", {})
        text = message.get("content") or ""
        usage = data.get("usage", {})
        usage.update({"model": self.model})
        return text, usage


def get_provider(name: str, config: LlmConfig) -> BaseProvider:
    normalized = (name or config.provider or "tiny-local").lower()
    if normalized in {"mock"}:
        return MockProvider()
    if normalized in {"local", "tiny", "tiny-local"}:
        return TinyLocalProvider(model_id=config.local_model)
    if normalized in {"openai", "deepseek", "api"}:
        return OpenAICompatibleProvider(
            api_key=config.api_key, base_url=config.base_url, model=config.api_model, timeout=config.request_timeout
        )
    raise ProviderError(f"Unknown provider '{normalized}'")
