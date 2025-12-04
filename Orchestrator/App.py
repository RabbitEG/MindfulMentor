from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .Flows import chat_flow
from .Models import ChatRequest, OrchestratorResponse

app = FastAPI(title="Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Frontend may be opened via WSL IP (e.g., 172.x.x.x) or localhost; allow all.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=OrchestratorResponse)
def chat(request: ChatRequest) -> OrchestratorResponse:
    result = chat_flow(request.text)
    return OrchestratorResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("Orchestrator.App:app", host="0.0.0.0", port=8003, reload=True)
