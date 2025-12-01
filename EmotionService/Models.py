from pydantic import BaseModel, Field


class EmotionRequest(BaseModel):
    text: str = Field(..., description="User input text to analyze")


class EmotionResult(BaseModel):
    emotion: str = Field(..., description="anxious|angry|sad|tired|neutral")
    intensity: int = Field(..., ge=1, le=4, description="Discrete intensity level 1-4")
    scores: dict[str, float] = Field(default_factory=dict, description="Per-emotion probability scores")


class EmotionResponse(BaseModel):
    emotion: EmotionResult
