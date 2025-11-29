from fastapi import FastAPI

from .Flows import breathing_flow, chat_flow, thought_clarify_flow
from .Models import ChatRequest, OrchestratorResponse

app = FastAPI(title="Orchestrator", version="0.1.0")


@app.post("/chat", response_model=OrchestratorResponse)
def chat(request: ChatRequest) -> OrchestratorResponse:
    result = chat_flow(request.text)
    return OrchestratorResponse(**result)


@app.post("/breathing", response_model=OrchestratorResponse)
def breathing(request: ChatRequest) -> OrchestratorResponse:
    result = breathing_flow(request.text)
    return OrchestratorResponse(**result)


@app.post("/thought-clarify", response_model=OrchestratorResponse)
def thought_clarify(request: ChatRequest) -> OrchestratorResponse:
    result = thought_clarify_flow(request.text)
    return OrchestratorResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("Orchestrator.App:app", host="0.0.0.0", port=8003, reload=True)
