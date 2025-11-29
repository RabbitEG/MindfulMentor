## Orchestrator 指南

本目录是“编排层”，负责把 Emotion → Prompt → LLM 这条链路串起来，对前端暴露统一接口。

- 前置知识：
  - FastAPI：用来提供 `/chat` 等 HTTP 入口。
  - 服务编排：在一个请求内调用多个内部服务并聚合结果。
  - 安全策略：基础词典/正则过滤，防止高风险输入继续下游。
  - traceId：用来链路追踪的唯一标识，便于日志关联。
- 环境配置：Python 3.10+；Linux 进入目录后 `python3 -m venv .venv && source .venv/bin/activate && pip install -r Requirements.txt`；确保 Emotion/PromptEngine/LlmGateway 可达（同机端口或本地 import）。
- 启动：激活 `.venv` 后可直接 `python App.py`（已内置 `uvicorn.run`，默认 `reload=True`），或使用 `uvicorn App:app --reload --port 8003`。
- 主要任务：
  - `/chat`：输入 `{text}`，输出 `{reply, emotion, mode, suggestedExercise, traceId}`。
  - `/breathing`：返回结构化的呼吸练习步骤；`/thought-clarify`：提供梳理事实/情绪/需求的辅助文本。
  - 调用链中处理错误并包装为 `{error:{code,detail}}`，保证上层接口稳定。
