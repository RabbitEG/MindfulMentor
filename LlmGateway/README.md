LlmGateway 是统一的大模型网关，屏蔽不同 provider（OpenAI 兼容接口 / 自定义 / mock / 本地 tiny 模型）的差异并返回 usage 统计。

## 名词解释
- Provider：具体的大模型服务提供方或实现（OpenAI 兼容 / 自定义 base_url / 本地模型 / mock）。
- Base URL/API Key：访问第三方 API 的地址和凭证，部分 provider 可为空（mock、本地）。
- Usage：调用返回的 token 统计，字段通常包含 `prompt_tokens`、`completion_tokens`、`total_tokens`。
- Fallback：当前 provider 失败时自动切换到 mock，保证调用不致崩溃。

## 职责与结构
- `Core.py`：读取配置，选择 provider，失败时自动 fallback 到 `MockProvider` 并把错误写入 usage；会把 prompt/回复/usage 记录到 `.logs/llm-gateway.log`。
- `Providers.py`：实现三类 Provider
  - `MockProvider`：无依赖快速回包；token 计数基于分词数量。
  - `TinyLocalProvider`：使用 HF `sshleifer/tiny-gpt2`（可被 `LLM_LOCAL_MODEL` 覆盖）在 CPU 生成，需安装 transformers/torch。
  - `OpenAICompatibleProvider`：纯 httpx 客户端，通过 `LLM_API_KEY/LLM_BASE_URL/LLM_API_MODEL/LLM_TIMEOUT` 或请求覆盖参数调用 `/chat/completions`。
- `Config.py`：读取环境变量（`LLM_PROVIDER/LLM_API_KEY/LLM_BASE_URL/LLM_API_MODEL/LLM_LOCAL_MODEL/LLM_TIMEOUT`），对 `openai|deepseek|api` 等 provider 自动补默认 base/model。
- `Models.py`：定义 `GenerateRequest/GenerateResponse`，请求支持传入 max_tokens、provider 覆盖、临时 API key/base/model 覆盖。
- `App.py`：FastAPI 入口，暴露 `/generate` 与 `/health`。

## 接口
- `/generate`：入参 `{prompt, provider?, max_tokens?}`，出参 `{text, provider, usage}`。
- `/health`：存活探针。

## 后续可改进
- 增加重试/熔断与更细粒度的错误码，方便上游观测。
- 支持流式输出、工具调用或 function calling。
- Provider 增补：本地大模型后端、量化模型、更多 OpenAI 兼容实现。
