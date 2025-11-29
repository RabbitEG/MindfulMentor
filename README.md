MindfulMentor 是一个“情绪觉察 + 安全回应”的轻量级多模块示例项目。目录拆分为：情绪识别（EmotionService）、提示组装（PromptEngine）、LLM 网关（LlmGateway）、编排层（Orchestrator）、Streamlit 前端（FrontEnd）。

## 快速开始
- 前置：Python 3.10+，建议保持网络可下载依赖与模型。
- 首次需要创建虚拟环境（StartAll 会自动激活但不会新建）：
  ```bash
  cd path/to/MindfulMentor
  python3 -m venv .venv
  ```
- 运行前激活虚拟环境，终端前缀应看到 `(.venv)`：
  ```bash
  source .venv/bin/activate
  ```
- 一键启动（包含依赖安装与端口准备）：
  ```bash
  cd path/to/MindfulMentor
  ./scripts/StartAll.sh
  ```
  启动成功后浏览器访问 `http://127.0.0.1:8501`。
- 每次跑完后建议清理环境与端口：
  ```bash
  ./scripts/ClearEnv.sh
  ```
  日志位于 `.logs/`。

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

## 协作 / 提交须知
- 仓库：https://github.com/RabbitEG/MindfulMentor
- 提交前先拉取主分支并解决冲突：`git pull --rebase`
- 避免在主分支直接开发，建议自建分支并通过 PR 合并；提交信息保持简洁明了。
- 提交前跑一遍 `./scripts/StartAll.sh` 确保依赖可装、服务可起，必要时附带关键日志说明。
- 推送前清理临时文件与敏感信息（如本地模型路径、API Key 等）。
