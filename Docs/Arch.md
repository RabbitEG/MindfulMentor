## 架构概要

MindfulMentor 采用松耦合的多模块拆分，全部可独立服务运行，也可被 Orchestrator 以 import 方式编排：

1) EmotionService：FastAPI 服务，HF 零样本分类（`facebook/bart-large-mnli` 缓存在 `EmotionService/.models/` 或 `EMOTION_MODEL_DIR`），返回标签/强度(1-4)/分布；暴露 `/analyze`，默认端口 8001。
2) PromptEngine：根据情绪强度选择模板与 LLM 参数；强度>3 走 `high_safety`（温度 0.2/最大 256 tokens），否则 `normal`（0.4/320）；模板位于 `PromptEngine/Templates/NormalIntensity.txt|HighIntensity.txt`，暴露 `/prompt`，默认端口 8002。
3) LlmGateway：统一 LLM 调度与 fallback，支持 `mock`、`tiny-local`（HF GPT-2 微型）、`openai-compatible`（OpenAI/DeepSeek 等接口兼容）；读取 `.env` 的 `LLM_*`，失败时自动回落到 mock 并记录 usage，暴露 `/generate`，默认端口 8004。
4) Orchestrator：业务编排层，做安全阻断（关键词：`suicide/violence/weapon`）→ 情绪 → 提示 → LLM，返回统一结构含 traceId/meta/suggestedExercise，并记录 `.logs/orchestrator.log`；暴露 `/chat`，默认端口 8003，开放 CORS 供静态前端调用。
5) 前端：`FrontendDeveloper/` 为 Streamlit 开发态 UI；`FrontendRelease/` 为无需构建的静态单页（`index.html`+`app.js` 等），默认通过 Orchestrator `/chat`。

### 调用链（函数层）
```
Orchestrator.Flows.chat_flow
  -> Safety.is_safe (阻断)
  -> EmotionService.Core.analyze_text
  -> PromptEngine.Core.build_prompt
  -> LlmGateway.Core.generate_text
```

### 配置与运行
- LlmGateway/Config.py 读取：`LLM_PROVIDER/LLM_API_KEY/LLM_BASE_URL/LLM_API_MODEL/LLM_LOCAL_MODEL/LLM_TIMEOUT`，缺失时 StartAll 自动回退到 `tiny-local`。
- EmotionService 可通过 `EMOTION_MODEL_DIR` 指向预下载模型；`EmotionService/download_models.py` 可离线拉取。
- StartAll.sh：清理旧端口/进程，自动创建 `.env`，检查/安装依赖与情绪模型缓存，并按 `FRONTEND_MODE=release|developer` 启动多服务（写日志到 `.logs/`）。默认 `release`（跑 `FrontendRelease/` 静态版）；`-d` 或 `FRONTEND_MODE=developer` 时跑 `FrontendDeveloper/` Streamlit 版。

### 日志与观测
- 目录：所有日志集中在仓库根的 `.logs/`，`StartAll.sh`/`ClearEnv.sh` 启动前会清空旧内容（避免体积无限增长）。
- Orchestrator：`.logs/orchestrator.log`，按请求写入时间戳、traceId、status（ok/blocked/error/exception）、user_text、detail（异常或阻断原因）。
- LlmGateway：`.logs/llm-gateway.log`，记录 provider、usage（token 统计/回退错误），并将 prompt 与回复正文落盘便于对齐生成问题。
- 预留文件：`prompt.log`、`emotion.log`、`frontend.log` 当前仅创建占位（便于后续扩展分别记录模板/情绪/前端访问），默认不写入内容。
- 关联：链路透传 `trace_id`（API 响应 snake_case）/`traceId`（meta camelCase），前端可用来指向两份日志进行问题排查。

### 部署建议
- 开发：同机多端口直接跑（默认 8001/8002/8003/8004/8501）。
- 生产：可将各服务容器化或置于 API Gateway 后；Emotion/Prompt/LLM 可按需求扩缩容；前端静态资源可托管在 CDN。
