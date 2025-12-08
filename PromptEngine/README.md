PromptEngine 负责根据情绪与上下文构建安全的 LLM Prompt，并决定高/常规模式的参数。

## 名词解释
- Prompt：发给大模型的指令文本，通常包含角色设定、语气、回复格式和限制条件。
- 模板（Template）：带占位符的 Prompt 样板，根据情绪/强度等变量动态填充。
- 模式（mode）：`high_safety` 表示更温和、受限的提示；`normal` 为常规提示。
- LLM 参数（llmParams）：调用大模型时的超参，如 `temperature`、`max_tokens`。

## 职责与结构
- `Core.py`：读取 `Templates/NormalIntensity.txt` 或 `HighIntensity.txt`，强度 >3 时进入 `high_safety` 并使用更保守的 `DEFAULT_LLM_PARAMS`（温度 0.2 / 最大 256 tokens），否则走 `normal`（温度 0.4 / 最大 320 tokens）；会把 `context`/`emotion`/`intensity` 填充到模板并返回 `PromptResponse`（含模式、LLM 参数与模板名 meta）。
- `Models.py`：定义 `PromptRequest/PromptResponse`，强度限制 1-4，llmParams 为 camelCase 键。
- `App.py`：FastAPI 入口，暴露 `/prompt` 与 `/health`，方便 HTTP 方式复用。
- `Templates/`：按模式存放提示模板，当前模板强调“同语言回应”“同伴口吻”，可增删占位符以携带更多上下文。

## 接口
- `/prompt`：入参 `{label, intensity, user_text, context}`，出参 `{prompt, mode, llmParams, meta}`。
- `/health`：存活探针。

## 后续可改进
- 丰富模板与多语言提示，增加可配置占位符和 A/B 版本。
- 将安全策略与 Prompt 模板联动（如对特定情绪追加更多安全说明）。
- 把 llmParams 做成策略表，便于根据场景自动调整温度/长度。
