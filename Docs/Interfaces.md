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
  ```

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
    "llmParams": { "temperature": 0.2, "maxTokens": 512 },
    "meta": { "template": "HighIntensity|NormalIntensity" }
  }
  ```

### 3) LlmGateway `/generate`
- **Method**: POST
- **Request**:
  ```json
  {
    "prompt": "string",
    "params": { "temperature": 0.2, "maxTokens": 512 },
    "provider": "openai|deepseek|mock"
  }
  ```
- **Response**:
  ```json
  {
    "text": "string",
    "provider": "openai|deepseek|mock",
    "usage": {
      "promptTokens": 0,
      "completionTokens": 0,
      "totalTokens": 0
    }
  }
  ```

### 4) Orchestrator `/chat`
- **Method**: POST
- **Request**:
  ```json
  { "text": "string" }
  ```
- **Response**:
  ```json
  {
    "reply": "string",
    "emotion": { "emotion": "...", "intensity": 1, "scores": { "...": 0.0 } },
    "mode": "high_safety|normal",
    "suggestedExercise": "grounding|thought_log|null",
    "traceId": "string"
  }
  ```

### 约定
- 错误统一：
  ```json
  { "error": { "code": "string", "detail": "string" } }
  ```
