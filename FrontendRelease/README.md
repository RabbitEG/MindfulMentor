# FrontendRelease

静态前端成品（无需构建），与开发态的 `FrontendDeveloper/` 分离。

## 运行静态 UI
1) 从仓库根目录：
```bash
cd FrontendRelease
python -m http.server 8501
```
2) 打开 http://127.0.0.1:8501

### 切换发布版 / 开发版 UI
- 默认启动发布版静态 UI。
- 启动开发版（Streamlit）：`./scripts/StartAll.sh -d` 或 `FRONTEND_MODE=developer ./scripts/StartAll.sh`
- 强制使用发布版：`./scripts/StartAll.sh -r`

## 配置与请求
- `config.js` 集中配置 API：`apiBaseUrl` 默认指向编排层 `http://127.0.0.1:8003`，端点为 `/chat`、`/history`、`/stats`（后两者可由后端补充或走 mock）。
- `mockResponses` 为 `true` 时完全本地 mock；为 `false` 时若调用失败可由 `fallbackToMockOnError` 启用降级。
- 请求超时、mock 延迟、Toast 时长等都在 `config.js` 中可调。

## 目录与角色
- `index.html`：单页骨架与区块布局（Hero、聊天卡片、历史/情绪分布、练习提示）。
- `styles.css`：轻量 SaaS/心理健康风格样式，含卡片、导航、提示条与图表区域。
- `config.js`：API 入口、超时、mock 开关与默认模式配置。
- `api.js`：封装 fetch + 超时控制，提供 `requestChat`/`fetchHistory`/`fetchStats`，含 mock 数据与失败回退逻辑。
- `ui.js`：DOM 渲染器（消息列表、情绪折线/热力图、提示条、历史列表），包含 Chart.js 绘制逻辑与交互折叠。
- `app.js`：入口文件，维护会话 state，绑定表单/导航/折叠交互，调用 API 并将结果标准化为 UI 可用的情绪/建议数据。
