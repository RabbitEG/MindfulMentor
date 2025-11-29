PromptEngine 负责根据情绪与上下文构建安全的 LLM Prompt，并决定高/常规模式的参数。

## 职责与结构
- `Core.py`：读取模板（`Templates/`），根据 `PromptRequest` 生成 `PromptResponse`，包含 mode、llmParams、meta。
- `Models.py`：定义请求/响应数据结构，约束强度范围等。
- `App.py`：FastAPI 入口，暴露 `/prompt` 与 `/health`。
- `Templates/`：按模式存放提示模板（如 high_intensity/normal）。

## 接口
- `/prompt`：入参 `{label, intensity, user_text, context}`，出参 `{prompt, mode, llmParams, meta}`。
- `/health`：存活探针。

## 后续可改进
- 丰富模板与多语言提示，增加可配置占位符和 A/B 版本。
- 将安全策略与 Prompt 模板联动（如对特定情绪追加更多安全说明）。
- 把 llmParams 做成策略表，便于根据场景自动调整温度/长度。
