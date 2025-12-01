from typing import Dict, Optional

from pydantic import BaseModel, Field, conint


class PromptRequest(BaseModel):
    """
    Request payload for building a prompt.
    """

    text: str = Field(..., description="Raw user text")
    emotion: str = Field(..., description="anxious|angry|sad|tired|neutral")
    intensity: conint(ge=1, le=4) = Field(
        ..., description="Discrete intensity level 1-4; >3 means high intensity"
    )
    context: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Optional metadata to surface inside prompt"
    )


class PromptResponse(BaseModel):
    prompt: str
    mode: str = Field(..., description="high_safety|normal")
    llmParams: Dict[str, float] = Field(
        default_factory=dict, description="LLM generation parameters (camelCase keys)"
    )
    meta: Dict[str, str] = Field(default_factory=dict)
