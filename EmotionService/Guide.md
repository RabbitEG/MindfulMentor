## EmotionService 指南

本目录是“情绪识别”微服务，负责把用户文本转成情绪标签、强度和各情绪得分。

- 前置知识：
  - FastAPI：Python 的轻量 Web 框架，用于暴露 HTTP 接口。
  - Pydantic：用来定义请求/响应数据模型并做校验。
  - 情绪识别：将文本映射为情绪类别（如 anxious/angry）并给出强度和得分分布。
- 环境配置：Python 3.10+；Linux 进入目录后 `python3 -m venv .venv && source .venv/bin/activate && pip install -r Requirements.txt`。
- 启动：激活 `.venv` 后可直接 `python App.py`（文件内已内置 `uvicorn.run`，默认 `reload=True`），或继续使用 `uvicorn App:app --reload --port 8001`。
- 主要任务：
  - 维护 `/analyze`：输入 `{text}`，输出 `{emotion, intensity, scores}`。
  - 实现或替换情绪识别算法（目前可用规则/占位，后续可接 HF 模型或本地模型）。
  - 确保健康检查 `/health` 可用，方便上游探活。
