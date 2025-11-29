from pydantic import BaseModel, Field


class EmotionRequest(BaseModel):
    text: str = Field(..., description="User input text to analyze")


class EmotionResult(BaseModel):
    label: str = Field(..., description="Coarse sentiment label")
    intensity: str = Field(..., description="low|medium|high")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for dominant label")
    dominant_emotions: list[str] = Field(default_factory=list, description="Top emotions detected")


class EmotionResponse(BaseModel):
    emotion: EmotionResult
