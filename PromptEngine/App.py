from fastapi import FastAPI

from Core import build_prompt
from Models import PromptRequest, PromptResponse

app = FastAPI(title="PromptEngine", version="0.1.0")


@app.post("/prompt", response_model=PromptResponse)
def prompt(request: PromptRequest) -> PromptResponse:
    return build_prompt(request)


@app.get("/health")
def health():
    return {"status": "ok"}
