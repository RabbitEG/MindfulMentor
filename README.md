MindfulMentor 是一个“情绪觉察 + 安全回应”的轻量级多模块示例项目。目录拆分为情绪识别、提示组装、LLM 网关、编排层，以及 Streamlit 前端，方便独立运行与组合。

## 快速开始
- Python 3.10+，建议每个子模块各自虚拟环境。
- 启动顺序（可按需局部运行）：
  1) EmotionService：`cd EmotionService && pip install -r Requirements.txt && uvicorn App:app --reload --port 8001`
  2) PromptEngine：`cd PromptEngine && pip install -r Requirements.txt && uvicorn App:app --reload --port 8002`
  3) LlmGateway：`cd LlmGateway && pip install -r Requirements.txt && uvicorn App:app --reload --port 8004`
  4) Orchestrator：`cd Orchestrator && pip install -r Requirements.txt && uvicorn App:app --reload --port 8003`
  5) 前端：`cd FrontEnd && pip install -r Requirements.txt && streamlit run App.py`

## 设计要点
- 强解耦：各模块都能独立作为服务运行，Orchestrator 可通过 import 或 HTTP 方式编排。
- 安全第一：PromptEngine 对高强度情绪使用更温和的提示，Safety 模块做硬规则检测。
- LLM 网关预留多提供商，默认 mock 返回，后续可接入 OpenAI / DeepSeek。

## 主要接口
- EmotionService `/analyze`：文本 → 情绪标签/强度。
- PromptEngine `/prompt`：情绪 + 文本 → 安全 Prompt。
- LlmGateway `/generate`：Prompt → LLM 回复（可切换 provider）。
- Orchestrator `/chat` `/breathing` `/thought-clarify`：统一给前端使用。

更多契约与调用链见 `Docs/Interfaces.md` 与 `Docs/Arch.md`。
