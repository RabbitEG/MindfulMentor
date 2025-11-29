LlmGateway 是统一的大模型网关，屏蔽不同 provider（OpenAI/DeepSeek/mock/本地 tiny 模型）的差异并返回 usage 统计。

## 名词解释
- Provider：具体的大模型服务提供方或实现（OpenAI/DeepSeek/本地模型/mock）。
- Base URL/API Key：访问第三方 API 的地址和凭证，部分 provider 可为空（mock、本地）。
- Usage：调用返回的 token 统计，字段通常包含 `prompt_tokens`、`completion_tokens`、`total_tokens`。
- Fallback：当前 provider 失败时自动切换到 mock，保证调用不致崩溃。

## 职责与结构
- `Core.py`：加载配置，选择 provider，处理回退逻辑（失败时自动 fallback 到 mock）。
- `Providers.py`：实现 Mock、TinyLocal（HF GPT-2 小模型）、OpenAI 兼容客户端。
- `Config.py`：读取环境变量（`LLM_PROVIDER/LLM_API_KEY/LLM_BASE_URL/LLM_API_MODEL/LLM_LOCAL_MODEL/LLM_TIMEOUT`）。
- `Models.py`：定义 `GenerateRequest/GenerateResponse`。
- `App.py`：FastAPI 入口，暴露 `/generate` 与 `/health`。

## 接口
- `/generate`：入参 `{prompt, provider?, max_tokens?}`，出参 `{text, provider, usage}`。
- `/health`：存活探针。

## 后续可改进
- 增加重试/熔断与更细粒度的错误码，方便上游观测。
- 支持流式输出、工具调用或 function calling。
- Provider 增补：本地大模型后端、量化模型、更多 OpenAI 兼容实现。
