## 架构概要

MindfulMentor 采用松耦合的多模块拆分：

1) EmotionService：负责基础情绪识别，可用 HF 模型或规则；对外暴露 `/analyze`。
2) PromptEngine：根据情绪强度选择模板，输出安全 Prompt；对外 `/prompt` 或被 Orchestrator 直接 import。
3) LlmGateway：封装 LLM 调用（OpenAI/DeepSeek/Mock），统一 `/generate`。
4) Orchestrator：编排 Emotion → Prompt → LLM，提供 `/chat` `/breathing` `/thought-clarify`。
5) FrontEnd：Streamlit UI，统一调用 Orchestrator。

### 调用链（本地 import 路径）
```
Orchestrator.Flows.chat_flow
  -> EmotionService.Core.analyze_text
  -> PromptEngine.Core.build_prompt
  -> LlmGateway.Core.generate_text
```

### 配置与拓展
- LlmGateway/Config.py 读取环境变量：`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_BASE_URL`。
- 前端通过 `FrontEnd/Config.py` 配置 Orchestrator 地址。
- Safety 模块提供硬规则检测，可扩展词典/正则。

### 部署建议
- 开发期：同机多端口；生产可 Docker 化或使用 API 网关汇聚。
- 日志与跟踪：保留 `trace_id` 透传，便于观测。
