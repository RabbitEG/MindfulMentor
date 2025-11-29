# MindfulMentor 进展报告

更新时间：自动生成于当前仓库状态（未额外改动代码）。

## 总体概况
- 架构按 Docs/Arch.md 所述已成型：EmotionService → PromptEngine → LlmGateway → Orchestrator → FrontEnd，全链路在同一代码库内以本地 import 方式串联（未写 HTTP 调用版本）。
- 每个子目录均附有独立 Guide.md 说明安装与启动，顶层 README.md 给出了启动顺序和虚拟环境做法。
- 接口契约与调用链文档已在 Docs 目录，但与部分实现有轻微字段差异（见“已知差异/风险”）。

## EmotionService（情绪识别）
- 状态：功能已完成，FastAPI 入口 `/analyze` 返回 EmotionResponse（emotion/intensity/scores）。
- 技术实现：Core.py 使用 HuggingFace `facebook/bart-large-mnli` 零样本分类器；`_scores_to_intensity` 将最大得分映射到 1-3 强度。
- 依赖与运行：需要 transformers + 大模型权重，首次运行会自动下载（较耗时/耗存储）；Requirements.txt 已列依赖。
- 输出结构：Models.EmotionResult 包含 emotion（anxious/angry/sad/tired/neutral）、intensity（1-3）、scores（全标签概率）。

## PromptEngine（提示生成）
- 状态：核心逻辑完成，FastAPI 入口 `/prompt` 对外；Orchestrator 直接 import 使用。
- 技术实现：Core.build_prompt 基于情绪强度选择模板（Templates/NormalIntensity.txt 或 HighIntensity.txt），并拼装 context、LLM 参数（normal/high_safety 两档）。
- 输入/输出：PromptRequest(text/emotion/intensity/context) → PromptResponse(prompt/mode/llmParams/meta)；默认 llmParams 在 Core.py 定义。
- 其他：模板内容已写好安全语气；强度值做了 1-3 归一化，错误类型会回落到强度 1。

## LlmGateway（大模型网关）
- 状态：基础可用，FastAPI 入口 `/generate`；Orchestrator 直接 import Core.generate_text。
- Provider 支持：Mock（默认兜底）、TinyLocal（sshleifer/tiny-gpt2，纯 CPU）、OpenAI 兼容 HTTP 客户端；可通过环境变量配置 provider/api_key/base_url/api_model/local_model。
- 容错：Core.generate_text 捕获 ProviderError 时自动降级到 MockProvider，并在 usage 中记录错误信息。
- 请求/响应：Models.GenerateRequest 包含 prompt/provider/max_tokens；GenerateResponse 返回 text/provider/usage。

## Orchestrator（编排层）
- 状态：已实现主要三个流，FastAPI 入口 `/chat` `/breathing` `/thought-clarify` `/health`。
- 业务逻辑：Flows.chat_flow 先做空文本校验与 Safety.hard stop（blocklist: suicide/violence/weapon），再调用 EmotionService.analyze_text → PromptEngine.build_prompt → LlmGateway.generate_text，按情绪强度决定 mode/suggestedExercise；breathing_flow 和 thought_clarify_flow 提供固定脚本。
- 数据模型：OrchestratorResponse 含 message/reply(trace)/mode/emotion/meta/suggestedExercise/error 等，支持别名透传。

## FrontEnd（Streamlit）
- 状态：可运行的 UI 已完成；App.py 组合多个组件（聊天输入、响应卡片、情绪图、练习卡、历史记录），默认调用本地 Orchestrator（Config.ORCHESTRATOR_BASE = http://localhost:8003）。
- 交互：支持切换 chat/breathing/thought-clarify 三个流，展示 trace_id、emotion、meta 等；History 记录最近 8 次调用。
- 风格：深色渐变背景、Space Grotesk 字体、自定义按钮/表单样式。

## 文档
- Docs/Arch.md 描述架构与调用链；Docs/Interfaces.md 给出接口契约；各子目录有 Guide.md；顶层 README.md 提供快速启动。

## 已知差异/风险
- 接口字段不完全一致：Docs/Interfaces.md 中 LlmGateway 请求包含 `params`，实现的 Models/GenerateRequest 使用 `max_tokens`；OrchestratorResponse 实际返回 `message`/`reply`/`trace_id`，文档示例用 `reply`/`traceId`。前端已按当前实现适配。
- 运行重量级依赖：EmotionService 依赖 BART 大模型，冷启动会下载权重且计算成本高；TinyLocal provider 需要 transformers/torch，如果未安装会触发降级到 mock。
- 缺少自动化测试与容器化脚本，目前需手动启动各服务；日志与监控仅有基础 trace_id，未接入可观测性组件。

## 下一步建议
- 对齐接口契约与实现（更新 Interfaces.md 或调整 Models），避免前后端字段漂移。
- 为 EmotionService/LlmGateway 增加轻量或离线模型选项，或在 README 标明首次运行的资源需求。
- 编排层增加异常日志、超时与重试策略；前端提示可区分 mock/真实 provider。
- 补充最小化的 e2e 流程测试脚本或 docker-compose 以方便启动与验证。
