from typing import Optional
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = Field(default=None, description="tiny-local|openai|deepseek|mock")
    max_tokens: int = Field(default=256, ge=1, le=2048)


class GenerateResponse(BaseModel):
    text: str
    provider: str
    usage: Optional[dict] = Field(default_factory=dict)
