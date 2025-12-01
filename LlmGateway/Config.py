import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
@dataclass
class LlmConfig:
    # provider: str = os.getenv("LLM_PROVIDER", "tiny-local")
    # api_key: str | None = os.getenv("LLM_API_KEY")
    # base_url: str | None = os.getenv("LLM_BASE_URL")
    # api_model: str = os.getenv("LLM_API_MODEL", "gpt-3.5-turbo")
    # local_model: str = os.getenv("LLM_LOCAL_MODEL", "sshleifer/tiny-gpt2")
    # request_timeout: float = float(os.getenv("LLM_TIMEOUT", "30"))
    provider: str
    api_key: str | None
    base_url: str | None
    api_model: str
    local_model: str
    request_timeout: float

# def load_config() -> LlmConfig:
#     return LlmConfig()
_DEEPSEEK_DEFAULT_BASE = "https://api.deepseek.com/v1"
_DEEPSEEK_DEFAULT_MODEL = "deepseek-r1"
_OPENAI_DEFAULT_MODEL = "gpt-3.5-turbo"


def load_config() -> LlmConfig:
    provider = os.getenv("LLM_PROVIDER", "tiny-local")
    base_url = os.getenv("LLM_BASE_URL")
    api_model = os.getenv("LLM_API_MODEL")

    normalized = provider.lower()
    if normalized == "deepseek":
        base_url = base_url or _DEEPSEEK_DEFAULT_BASE
        api_model = api_model or _DEEPSEEK_DEFAULT_MODEL
    else:
        api_model = api_model or _OPENAI_DEFAULT_MODEL

    return LlmConfig(
        provider=provider,
        api_key=os.getenv("LLM_API_KEY"),
        base_url=base_url,
        api_model=api_model,
        local_model=os.getenv("LLM_LOCAL_MODEL", "sshleifer/tiny-gpt2"),
        request_timeout=float(os.getenv("LLM_TIMEOUT", "30")),
    )