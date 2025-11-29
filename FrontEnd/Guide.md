## FrontEnd 指南

本目录是可运行的 Streamlit 前端，负责把编排层的能力展示为网页。

- 前置知识：
  - Streamlit：快速搭建数据应用的 Python 库。
  - HTTP 请求：用 `requests` 调 Orchestrator 接口。
  - Plotly：用于可视化情绪得分或分布。
- 环境配置：Python 3.10+；Linux 进入目录后 `python3 -m venv .venv && source .venv/bin/activate && pip install -r Requirements.txt`；在 `Config.py` 配置 Orchestrator 地址；运行 `streamlit run App.py`。
- 主要任务：
  - 组织聊天面板、情绪图表、练习卡片等 UI。
  - 调用 `/chat` `/breathing` `/thought-clarify`，展示 `reply/emotion/mode/suggestedExercise`。
  - 确保前端字段与接口契约一致，必要时在 UI 端做基础错误提示。
