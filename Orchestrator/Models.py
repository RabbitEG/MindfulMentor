from typing import Dict, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    text: str = Field(..., description="User input text")


class OrchestratorResponse(BaseModel):
    message: str
    trace_id: str
    meta: Dict[str, str] = Field(default_factory=dict)
    emotion: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[Dict[str, str]] = Field(default=None)
