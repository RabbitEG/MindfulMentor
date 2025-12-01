from typing import Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = Field(default=None, description="tiny-local|openai|api|mock (openai-compatible)")
    max_tokens: int = Field(default=256, ge=1, le=2048)
    api_key: Optional[str] = Field(
        default=None,
        description="Override API key for openai-compatible providers so mature hosted models can be called without restarting the service.",
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Override base URL (e.g. https://api.openai.com/v1 or a self-hosted OpenAI-compatible gateway).",
    )
    api_model: Optional[str] = Field(default=None, description="Override model name for the provider call.")


class GenerateResponse(BaseModel):
    text: str
    provider: str
    usage: Optional[dict] = Field(default_factory=dict)
