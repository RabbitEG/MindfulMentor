## PromptEngine 指南

本目录是“提示生成器”，根据情绪信息组装安全的 LLM 输入文本（prompt）。

- 前置知识：
  - Prompt：发送给大模型的指令文本。
  - 模板渲染：把情绪、强度等变量填入预设模板（Normal/HighIntensity）。
  - 安全模式（mode）：high_safety 用更温和、限制性的提示；normal 为常规提示。
  - FastAPI/Pydantic：框架与数据校验基础。
- 环境配置：Python 3.10+；`pip install -r Requirements.txt`；启动 `uvicorn App:app --reload --port 8002`。
- 主要任务：
  - `/prompt`：输入 `{text, emotion, intensity, context}`，输出 `{prompt, mode, llmParams, meta}`。
  - 维护模板文件，确保高强度情绪使用更安全的措辞。
  - 设置合适的 LLM 参数（llmParams，如 temperature、maxTokens）并透传给下游。
