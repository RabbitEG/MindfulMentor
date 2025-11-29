import os
from dataclasses import dataclass


@dataclass
class LlmConfig:
    provider: str = os.getenv("LLM_PROVIDER", "mock")
    api_key: str | None = os.getenv("LLM_API_KEY")
    base_url: str | None = os.getenv("LLM_BASE_URL")


def load_config() -> LlmConfig:
    return LlmConfig()
