from pydantic import BaseModel, Field
from typing import Dict, Optional


class PromptRequest(BaseModel):
    label: str
    intensity: str
    user_text: str = Field(..., description="Raw user text")
    context: Optional[Dict[str, str]] = Field(default_factory=dict)


class PromptResponse(BaseModel):
    prompt: str
    meta: Dict[str, str] = Field(default_factory=dict)
