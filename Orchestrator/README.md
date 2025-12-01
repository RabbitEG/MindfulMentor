Orchestrator 负责将 EmotionService、PromptEngine、LlmGateway 串成完整的对话/练习流程，对前端暴露统一接口。

## 名词解释
- 编排（Orchestration）：在一个请求内调用多个内部服务并聚合结果。
- TraceId：链路唯一标识，用于日志关联和问题排查。
- 模式（mode）：下游返回的安全等级，`high_safety` 表示情绪强度高时的谨慎回复，`normal` 为常规回复。
- 安全阻断：检测到高风险内容时直接返回安全提示，不再调用下游模型。

## 职责与结构
- `App.py`：FastAPI 入口，注册 `/chat`、`/health`。
- `Flows.py`：封装各业务流程，处理安全校验、traceId 生成、错误包装。
- `Safety.py`：简单的硬规则过滤与阻断提示。
- `Models.py`：定义请求/响应数据模型。

## 接口
- `/chat`：串 Emotion → Prompt → LLM，返回 `{reply, mode, emotion, trace_id, meta}`。
- `/health`：存活探针。

## 后续可改进
- 为异步/超时/熔断添加更健壮的错误恢复与指标上报。
- 增加会话态（历史对话摘要）与用户分级策略。
- 对接集中式配置和可观测性（trace/span/metrics），便于排障。
