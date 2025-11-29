from fastapi import FastAPI

from .Core import generate_text
from .Models import GenerateRequest, GenerateResponse

app = FastAPI(title="LlmGateway", version="0.1.0")


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    return generate_text(request)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("LlmGateway.App:app", host="0.0.0.0", port=8004, reload=True)
