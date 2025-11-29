from fastapi import FastAPI

from Core import analyze_text
from Models import EmotionRequest, EmotionResponse

app = FastAPI(title="EmotionService", version="0.1.0")


@app.post("/analyze", response_model=EmotionResponse)
def analyze(request: EmotionRequest) -> EmotionResponse:
    result = analyze_text(request.text)
    return EmotionResponse(emotion=result)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("App:app", host="0.0.0.0", port=8001, reload=True)
