## LlmGateway 指南

本目录是“大模型网关”，统一对接 OpenAI/DeepSeek/Mock 等提供商。

- 前置知识：
  - LLM（Large Language Model）：大规模语言模型服务。
  - Provider：具体的模型提供商或后端实现（openai/deepseek/mock）。
  - Base URL/API Key：访问第三方 API 的地址和凭证。
  - Usage 统计：返回 prompt/completion/total token 计数，便于计费和监控。
- 环境配置：Python 3.10+；Linux 进入目录后 `python3 -m venv .venv && source .venv/bin/activate && pip install -r Requirements.txt`；配置 `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`（mock 可空）。
- 启动：激活 `.venv` 后可直接 `python App.py`（已内置 `uvicorn.run`，默认 `reload=True`），或使用 `uvicorn App:app --reload --port 8004`。
- 主要任务：
  - `/generate`：输入 `{prompt, params, provider}`，输出 `{text, provider, usage}`。
  - 实现对不同 provider 的分发与错误处理；保留 mock 模式便于离线调试。
  - 记录并返回 usage 统计，方便上层观测。

### Provider 配置
- 默认 `LLM_PROVIDER=tiny-local` 使用超小 `sshleifer/tiny-gpt2`，离线可跑；缺少依赖时自动回退到 `mock`。
- 使用本地其他模型：设置 `LLM_LOCAL_MODEL=<hf model id>`，或请求体中带 `provider: "tiny-local"` + `max_tokens`。
- 走 API（OpenAI/DeepSeek 等兼容接口）：`LLM_PROVIDER=openai`，并配置 `LLM_API_KEY`, `LLM_BASE_URL`（可选），`LLM_API_MODEL`（默认 `gpt-3.5-turbo`）。
- 手动 mock：`LLM_PROVIDER=mock` 或请求体 `provider: "mock"`。
