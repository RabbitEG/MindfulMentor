import os
from dataclasses import dataclass


@dataclass
class LlmConfig:
    provider: str = os.getenv("LLM_PROVIDER", "tiny-local")
    api_key: str | None = os.getenv("LLM_API_KEY")
    base_url: str | None = os.getenv("LLM_BASE_URL")
    api_model: str = os.getenv("LLM_API_MODEL", "gpt-3.5-turbo")
    local_model: str = os.getenv("LLM_LOCAL_MODEL", "sshleifer/tiny-gpt2")
    request_timeout: float = float(os.getenv("LLM_TIMEOUT", "30"))


def load_config() -> LlmConfig:
    return LlmConfig()
