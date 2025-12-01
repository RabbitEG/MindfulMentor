import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
@dataclass
class LlmConfig:
    provider: str
    api_key: str | None
    base_url: str | None
    api_model: str
    local_model: str
    request_timeout: float

_OPENAI_COMPAT_DEFAULT_BASE = "https://api.openai.com/v1"
_OPENAI_COMPAT_DEFAULT_MODEL = "gpt-3.5-turbo"
_LOCAL_DEFAULT_MODEL = "sshleifer/tiny-gpt2"


def load_config() -> LlmConfig:
    provider = os.getenv("LLM_PROVIDER", "tiny-local")
    base_url = os.getenv("LLM_BASE_URL")
    api_model = os.getenv("LLM_API_MODEL")

    normalized = provider.lower()
    if normalized in {"api", "openai", "deepseek"}:
        base_url = base_url or _OPENAI_COMPAT_DEFAULT_BASE
        api_model = api_model or _OPENAI_COMPAT_DEFAULT_MODEL
    else:
        api_model = api_model or _OPENAI_COMPAT_DEFAULT_MODEL

    return LlmConfig(
        provider=provider,
        api_key=os.getenv("LLM_API_KEY"),
        base_url=base_url,
        api_model=api_model,
        local_model=os.getenv("LLM_LOCAL_MODEL", _LOCAL_DEFAULT_MODEL),
        # Unified LLM timeout sourced from .env (fallback 60s to match StartAll template)
        request_timeout=float(os.getenv("LLM_TIMEOUT", "60")),
    )
