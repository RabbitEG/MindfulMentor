# FrontendWeb 设计/实现规范（给 Codex）

一份“模糊但有边界”的前端规范，供 Codex 直接开干。目标：在 `FrontendStreamlit/` 之外新增一个纯静态 Web 前端（例如目录 `FrontendWeb/`），走心理健康 Dashboard 风格，可用 `python -m http.server` 直接跑，无需任何构建链路。

## 技术约束（硬边界）
- 禁止新增 Node.js/npm 构建依赖；不用 webpack/vite 等打包器。
- 技术栈：纯 `HTML + CSS + 原生 JS`，可通过 CDN 引入 Tailwind、图标库、Chart.js 等。
- 目录建议：
  ```
  FrontendWeb/
    index.html
    styles.css      # 若用 Tailwind CDN，这里只补充少量自定义样式
    app.js
    api.js
    ui.js
    config.js       # 统一存放后端 URL/字段名常量
    assets/         # logo / 占位图
  ```
- 启动方式：直接用浏览器打开或 `python -m http.server`；不得要求任何编译/打包步骤。

## 信息架构（页面与模块）
- 顶部栏：项目名 + tagline，右上预留头像/设置位。
- 左侧竖直导航（图标 + 文本，预留项）：Overview、Mindful Chat、History/Logs。
- 主体区分三栏布局：
  - 中部主区：
    - 当前会话：输入框 + 发送 + 回复列表。
    - 情绪分析区：条形图/热力图标签。
  - 右侧栏（可选）：推荐练习/今日小结/小贴士卡片。
- Mindful Chat：
  - 大号文本输入（心理咨询语气提示）。
  - 动作按钮：主 CTA「发送」。
  - 回复区域：卡片呈现，包含正文 + 轻微高亮的“操作建议”段。
  - 同页补充：情绪热力图/条形图（来自后端情绪分数）、历史轮廓（最近会话的情绪标签 + 时间）。
- 单一 Chat 模式：无需模式切换，文案/结构留扩展点即可。

## 交互与行为
- 所有后端调用必须有 loading 状态：按钮禁用 + spinner；完成后恢复。
- 错误提示统一用固定位置的 toast/alert 条（右上或输入区上方），不可用 `alert()`；文案偏中性：“服务暂时不可用，请稍后重试。” 保留用户输入。
- 消息展示：卡片堆叠，用户气泡浅背景靠右，系统卡片白底+阴影靠左；长回复自动滚动到最新。
- 空状态：首次进入主区显示文案，例如 “Describe how you feel today to start a mindful chat.”，避免空白。

## 视觉风格参考
- 主题：心理健康/医疗咨询类 SaaS Dashboard。
- 配色：浅色背景（very light grey/淡渐变）；主色为中度绿色/青色系，用于按钮、重点卡片、图表线条；整体色彩克制。
- 字体：系统无衬线（`-apple-system, system-ui, sans-serif`），层级清晰（标题/副标题/正文）。
- 卡片：12–16px 大圆角，柔和阴影，留足内边距。
- 图表：简洁，避免彩虹色。

## 与后端的抽象协议
- 统一在 `config.js` 存放接口 URL/字段名，便于后续替换。
- 接口形态（字段存在则渲染，不存在则跳过，不做强耦合）：
  - `POST /api/chat`：请求含 `text`，可选 `mode`；返回 `reply`、`emotions`（情绪标签+分数）、`suggestions`（可选）。
  - `GET /api/history`：返回若干最近会话的时间、主情绪标签、模式。
  - `GET /api/stats`：返回情绪热力图/趋势所需的聚合数据。

## 代码组织与可维护性
- 拆分职责：
  - `app.js`：入口、初始化、事件绑定、状态管理。
  - `api.js`：封装 `requestChat`、`fetchHistory`、`fetchStats`（基于 `fetch`），统一错误包装。
  - `ui.js`：DOM 更新与渲染函数（消息渲染、图表渲染、错误/空状态/加载状态）。
  - `styles.css`：集中颜色/间距/阴影等变量；避免零散行内样式；少量自定义覆盖 Tailwind。
- 避免到处拼接字符串：使用模板函数或局部 `innerHTML` 块；保持可读性。
- 保留模式扩展点：如未来扩展其他模式，结构可继续复用，但当前仅实现 Chat。

## 交付给 Codex 的简指令（可直接粘贴）
> 帮我在 `FrontendWeb/` 目录下实现一个纯静态 Web 前端，用于展示 MindfulMentor 的情绪对话功能。  
> 约束：不使用 Node.js 构建工具，不需要 npm/yarn，必须保证 clone 后可直接浏览器打开或 `python -m http.server` 启动。用 HTML + CSS + 原生 JS，可通过 CDN 引入 Tailwind、图标库、Chart.js。整体风格走心理健康/医疗咨询 Dashboard，浅色背景、大圆角卡片、绿色为主色。页面包括左侧导航、顶部栏、中部对话区域、右侧统计/推荐区域。与后端交互通过 `POST /api/chat`、`GET /api/history`、`GET /api/stats` 三个接口，字段存在就渲染、不存在就跳过，接口常量集中放 `config.js`。JS 拆成 `app.js`、`api.js`、`ui.js` 等模块，避免所有逻辑写在一个 `<script>`。需要错误提示、加载状态、空状态。
