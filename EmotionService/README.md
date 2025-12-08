EmotionService 负责将用户文本映射为情绪标签、强度与得分分布，为后续提示组装和安全策略提供信号。

## 名词解释
- 情绪标签：预设的类别，如 anxious（焦虑）、angry（愤怒）、sad（悲伤）、tired（疲惫）、neutral（中性）。
- 强度（intensity）：1-4 的离散等级，按模型置信度估计情绪强烈程度；≥4 触发下游高安全提示。
- 得分分布（scores）：每个情绪标签的置信度字典，便于前端绘图或后续逻辑。

## 职责与结构
- `Core.py`：从本地缓存加载 HF 零样本分类模型（默认 `facebook/bart-large-mnli`，路径由 `EMOTION_MODEL_DIR` 或 `.models/` 提供），`analyze_text` 会返回主情绪 + 置信度分布，并按阈值(≥0.82→4，≥0.66→3，≥0.33→2，否则 1)映射强度。
- `Models.py`：定义 `EmotionRequest/EmotionResponse/EmotionResult`，约束强度范围 1-4。
- `App.py`：FastAPI 入口，暴露 `/analyze` 与 `/health`，用于 HTTP 调用或本地启动。
- `download_models.py`：预下载模型到 `.models/`，或自定义 `EMOTION_MODEL_DIR` 以复用离线模型。

## 接口
- `/analyze`：入参 `{text}`，返回 `{emotion, intensity (1-4), scores}`。
- `/health`：存活探针。

## 后续可改进
- 支持多语言与领域自适应（切换或微调模型）。
- 增加规则/轻量模型作为快速回退，避免模型缺失时直接报错。
- 对长文本做截断/摘要预处理，减少模型负载；并加入简单缓存。
