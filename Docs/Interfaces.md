## MindfulMentor 接口契约（新版）

面向当前工程结构的 JSON 契约说明。

### 1) EmotionService `/analyze`
- **Method**: POST
- **Request**:
  ```json
  { "text": "string" }
  ```
- **Response**:
  ```json
  {
    "emotion": {
      "emotion": "anxious|angry|sad|tired|neutral",
      "intensity": 1,
      "scores": {
        "anxious": 0.0,
        "angry": 0.0,
        "sad": 0.0,
        "tired": 0.0,
        "neutral": 0.0
      }
    }
  }
  ```
  - 说明：`intensity` 为 1-4；置信度 ≥0.82→4，≥0.66→3，≥0.33→2，否则 1。

### 2) PromptEngine `/prompt`
- **Method**: POST
- **Request**:
  ```json
  {
    "text": "string",
    "emotion": "anxious|angry|sad|tired|neutral",
    "intensity": 1,
    "context": { "traceId": "string" }
  }
  ```
- **Response**:
  ```json
  {
    "prompt": "string",
    "mode": "high_safety|normal",
    "llmParams": { "temperature": 0.2, "maxTokens": 256 },
    "meta": { "template": "HighIntensity.txt|NormalIntensity.txt" }
  }
  ```
  - 说明：`intensity` >3 触发 `high_safety`；默认 llmParams 为 high_safety `{temperature:0.2,maxTokens:256}`，normal `{temperature:0.4,maxTokens:320}`。

### 3) LlmGateway `/generate`
- **Method**: POST
- **Request**:
  ```json
  {
    "prompt": "string",
    "provider": "tiny-local|openai|api|mock",
    "max_tokens": 512,
    "api_key": "string (optional)",
    "base_url": "string (optional)",
    "api_model": "string (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "text": "string",
    "provider": "openai-compatible|tiny-local|mock",
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0,
      "model": "string",
      "error": "fallback error if any",
      "fallback_from": "string"
    }
  }
  ```
  - 说明：当上游 provider 失败会 fallback 到 mock，并在 usage 中追加 `error` 与 `fallback_from`。

### 4) Orchestrator `/chat`
- **Method**: POST
- **Request**:
  ```json
  { "text": "string" }
  ```
- **Response**:
  ```json
  {
    "message": "string",
    "reply": "string",
    "emotion": { "label": "...", "intensity": 1, "score": 0.0, "scores": { "...": 0.0 } },
    "mode": "high_safety|normal",
    "suggestedExercise": "grounding|thought_log|null",
    "trace_id": "string",
    "meta": {
      "flow": "chat",
      "traceId": "string",
      "template": "HighIntensity.txt|NormalIntensity.txt",
      "llmParams": { "temperature": 0.2, "maxTokens": 256 },
      "llm_provider": "openai-compatible|tiny-local|mock",
      "usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 }
    }
  }
  ```
  - 说明：命中安全阻断时 `emotion` 为空，`mode` 强制为 `high_safety`，`meta.safety="blocked"`，`suggestedExercise` 不返回。

### 约定
- 错误统一：
  ```json
  { "error": { "code": "string", "detail": "string" } }
  ```
