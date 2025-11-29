from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    text: str = Field(..., description="User input text")


class OrchestratorResponse(BaseModel):
    message: str = Field(..., description="Primary message shown to the user")
    trace_id: str = Field(..., description="Trace identifier for request correlation")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the flow")
    emotion: Optional[Dict[str, Any]] = Field(default=None, description="Normalized emotion payload")
    mode: Optional[str] = Field(default=None, description="high_safety | normal")
    suggested_exercise: Optional[str] = Field(
        default=None, alias="suggestedExercise", description="Recommended exercise based on emotion"
    )
    reply: Optional[str] = Field(default=None, description="Alias for message to match interface guide")
    error: Optional[Dict[str, str]] = Field(default=None, description="{code, detail} if something went wrong")

    class Config:
        allow_population_by_field_name = True
