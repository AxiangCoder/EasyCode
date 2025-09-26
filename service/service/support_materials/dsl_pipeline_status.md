# DSL 转前端流程现状与优先级

## 阶段划分与能力盘点

### Sketch → DSL 阶段
- **已具备能力**
  - `design_tokens.json` 已提供基础颜色 / 字体 / 阴影映射，`SketchConverter` 会尝试对齐到令牌。
  - `SketchConverter._traverse_layer` 完整输出节点树，保留 `frame`、`style`、`layout` 等字段。
  - 资源节点携带 `exportOptions`，后续可用于生成静态资源。
  - 若 LLM 可用，可尝试识别 Flex/Grid 布局，为布局语义化提供初步支撑。
- **待完善事项**
  - 组件语义薄弱：大量 `div/text/img`，缺乏业务组件标识。
  - 布局语义不足：绝对定位为主，缺少栅格、响应式信息。
  - 数据 / 交互缺席：没有接口描述、字段绑定、事件信息。
  - 命名与复用缺失：节点命名沿用 Sketch 默认，无法区分可复用组件。
  - 设计令牌覆盖有限：DSL 中仍混杂大量硬编码值。

### DSL → 前端阶段
- **已具备能力**
  - `converter` 模块已有扩展框架，可挂载新转换逻辑。
  - 现有 `DesignConverterService` 已封装输入校验、任务执行等服务入口，可在此基础上扩展前端生成流程。
- **待完善事项**
  - 缺少 React + Ant Design 渲染器及组件映射表。
  - Tailwind 样式生成未与 React 代码结合。
  - 尚无 Vite + React + TS 项目模板与配置注入流程。
  - 数据接入、事件骨架、质量保障等工程体系尚未搭建。

## 开发优先级规划（单人迭代）

### 阶段 0：准备 & 基线（1 周内）
1. **定义 DSL Schema & 默认值**（Sketch → DSL）
   - 梳理现有 DSL 字段，补充 schema 校验确保字段完整性。
   - 为缺失字段补默认值（如 `layout.type`、`style` 基础属性）。
2. **整理设计令牌与命名/标记规则**（Sketch → DSL）
   - 约定：若用户上传 token 文件，则加载并校验；若未提供，则使用默认 CSS/Tailwind 主题，避免卡住流程。
   - 在有 token 时，可扩展 `design_tokens.json`，覆盖登录页常见颜色/字体/阴影。
   - 制定组件命名与语义标记规范（如命名 `Button@Primary` 或在 metadata 中写入 `semanticType: Button.Primary`），并提供示例模板，保证标记来源统一。

### 阶段 1：MVP（React + Tailwind + Antd，目标 2-3 周）
1. **组件映射规划**（DSL → 前端）
   - 梳理登录页常用组件，基于设计师提供的语义标记整理“语义标记 → Antd 组件/props/依赖”的映射表，存放在可版本化配置（如 `component-map.json`）。
   - 通过 Schema 校验确保 DSL 输入满足映射需求：若 `semanticType` 缺失则直接记录为未覆盖项，并在校验报告中提示设计侧补标（系统自动识别留待后续迭代）。

   **混合标记实施细则**
   - **标记输入**：在 Sketch→DSL 工具中读取设计师标注（命名约定或 metadata），写入 DSL `semanticType` 字段，并保留原始名称。
   - **缺失记录**：对于缺失或冲突标记的节点，先行记录在 `warnings` 列表中，提示设计师补标；此阶段不自动推断类型，只输出占位说明。
   - **校验回路**：导出 DSL 后生成校验报告，列出“缺少标记”“多义冲突”等情况，支持设计师在下一次上传前修复。
   - **渲染器消费**：生成前端代码时，优先使用 `semanticType`；若为空，则生成 `// TODO: confirm component` 注释并降级为基础 `div`，同时在日志中标记需要人工处理。
   - **数据沉淀**：将每次生成过程中的组件使用、未命中原因写入统计文件，为后续引入系统自动识别或扩展组件库提供依据。
2. **React 渲染器实现（可扩展架构）**（DSL → 前端）
   - **模块划分（Python 实现）**：
     - `frontend_renderer/__init__.py`：对外 `render_project(dsl, options)` 入口。
     - `context.py`：维护组件映射、输出路径、统计信息、样式方案等运行上下文；接口保持通用，后续可注入 Vue/其它框架渲染器。
     - `component_map.py`：存放“语义标记 → Antd 组件/props/依赖”映射，可用 JSON/YAML 加载。
     - `page_renderer.py`：负责页面级渲染（生成 TSX 字符串、汇总导入、挂载路由）。
     - `component_renderer.py`：递归处理节点，产出组件 TSX。
     - `style_mapper.py`：DSL 样式 → Tailwind 类名 / 自定义 CSS。
     - `template_writer.py`：复制 Vite 模板、更新入口文件、写入最终内容。
     - 以上模块建议放于 `converter/frontend_renderer/`，与现有 `sketch_converter`、`tailwind_converter.py` 同级，方便统一调用。
   - **插件化策略**：
     - 抽象 `RendererRegistry`，允许注册不同框架渲染器；阶段一实现 `react`，保留 `vue` 等占位，方便扩展。
     - 组件映射表分层：基础语义层（通用属性）与框架实现层（Antd/Element/MUI），通过配置选择具体实现。
     - 渲染流水线提供 hook（`before_render_node`、`after_render_page` 等），便于未来插件接入。
   - **生成方式**：
     - 使用 `jinja2` 模板生成 TSX、配置文件；模板中通过变量渲染 props、事件、导入列表。
     - 若需修改现有 TSX 文件的 import/路由，可使用 `libcst` 或先设置占位符（如 `// @@AUTO_ROUTES@@`）再由 Python 替换。
   - **渲染流程**：
     1. `render_project` 解析 DSL → 构建上下文 → 调用 `page_renderer.render(page)` 返回 `FileArtifact` 列表。
     2. `component_renderer.render_node(node)` 根据 `semanticType` 查映射，渲染组件模板；未识别则写入降级 div + TODO 注释。
     3. props 处理集中在 `prop_builder.py`，将 DSL 属性拆解为 `attrs`、`className`、`style`、`dataBinding` 等结构供模板使用。
     4. 子节点递归，结果列表传回父节点；Tailwind 类名由 `style_mapper` 转换，无法覆盖的写入 `ctx.custom_styles`。
   - **导入与依赖管理**：
     - 映射表需声明组件依赖（如 `import { Button } from 'antd'`），渲染时向上下文推送，最终在页面模板中统一去重写入。
     - 统一在模板生成阶段引入 `antd/dist/reset.css`、Tailwind 入口等必需依赖。
   - **输出与格式化**：
     - 所有文件先写入内存（`FileArtifact(path, content)`），模板写入后再统一输出到磁盘。
     - 生成完成后由 Python 调用 `npm install`、`npm run lint`、`npm run build`，并执行 `npx prettier --write` 做格式化。
     - 写入 `report.json`/`README`，记录生成参数、未识别组件、Tailwind 自定义样式等信息。
    - **实现步骤（分层修改指南）**：
      1. **核心渲染引擎层（新建）**：在 `converter/` 下创建 `frontend_renderer/` 包，实现上述模块与接口。
      2. **Service 层**：在 `converter/service/frontend_generation_service.py` 中新增 `generate_frontend_project` 方法，调用渲染器并封装打包、报告逻辑；负责加载模板路径、Tailwind 配置、组件映射等基础配置。
      3. **View 层**：在 `converter/views.py` 增加接口（或更新现有视图），调用 Service，处理用户请求/返回结果（成功时返回下载链接或任务 ID，失败时返回错误信息与日志路径）。
      4. **任务/集成层（可选）**：如需异步执行，在 `converter/tasks.py` 中新增 Celery 任务；CLI 场景可添加 `management/commands`。
      5. **错误处理与回滚**：Service 层需在失败时清理半成品目录/压缩包，并将异常转换为易读的业务错误，记录日志。
      6. **日志与测试**：统一使用 Django logging 记录关键节点；新增渲染器单测、Service 集成测、View API 测，确保输出稳定。
3. **Tailwind 样式融合（多方案就绪）**（DSL → 前端）
   - 抽象 `StyleEngine` 接口，阶段一实现 `TailwindEngine`；接口统一输出 `{ classNames, customStyles, dependencies }`，便于后续扩展 `ScssEngine`、`LessEngine`。
   - `TailwindEngine` 负责将 DSL 样式转换为 Tailwind 类名，未命中时写入 `custom.css`，并生成 `tailwind.config.js`、`postcss.config.js`、`src/styles/tailwind.css`。
   - 在上下文中记录设计令牌与主题映射，输出为 Tailwind 主题配置；未来切换样式方案时可直接复用。
   - 样式引擎与渲染器解耦，调用端只需根据配置选择样式方案，确保新增样式栈时对核心逻辑影响最小。
4. **项目模板与注入**（DSL → 前端）
   - 准备 Vite + React + TS 空模板，包含 `src/pages`, `src/components`, `src/services`, `src/styles`。
   - 渲染器生成文件后注入模板，并用 AST/模板引擎更新 `App.tsx`、`router.tsx`、`main.tsx`。
   - Service 层（`converter/service/frontend_generation_service.py`）负责调用渲染器、处理打包、输出报告；HTTP 接口放在 `converter/views.py`（调用 Service，保持瘦身），必要时可在 `converter/tasks.py` 中封装异步任务。
5. **事件骨架占位**（DSL → 前端）
   - 为 DSL 中的事件生成 `handleEvent('eventId')`，在 `src/actions/index.ts` 中输出日志占位。
6. **产物校验与打包**（DSL → 前端）
   - 自动执行 `npm install`, `npm run lint`, `npm run build`，记录结果。
   - 打包为 zip，并包含 README（依赖安装、命令、DSL 限制说明）与 DSL → 前端映射说明。

### 阶段 2：强化迭代（MVP 之后按需推进）
1. **组件语义补强**（Sketch → DSL）
   - 在 Sketch → DSL 转换中引入组件识别规则（基于命名/符号 ID）。
2. **布局语义与响应式**（Sketch → DSL + DSL → 前端）
   - 在 DSL 中加入 Flex/Grid 标记；前端渲染时支持栅格布局。
3. **系统识别组件增强**（Sketch → DSL + DSL → 前端）
   - 基于阶段一沉淀的 `warnings` 和统计数据，引入结构/命名规则和模型，自动生成 `detectedType`、`confidence`，实现真正的混合模式。
4. **数据接入落地**（DSL → 前端）
   - 根据 DSL 描述生成服务层与数据 Hook，支持接口域名 `.env` 配置、错误处理、Loading 状态等完整流程。
5. **事件系统实现**（DSL → 前端）
   - 逐步实现登录、跳转、弹窗等核心动作。
6. **质量保障扩展**（DSL → 前端）
   - 加入 Vitest/Playwright 模板、CI 配置；生成后自动运行 `lint`/`build`。
7. **多技术栈扩展**（DSL → 前端）
   - 在 MVP 稳定后，新增 Vue 渲染器、其他组件库适配、SCSS/Less 支持。
8. **统一错误处理与日志**（全链路）
   - 在渲染器、Service、View 层建立标准异常体系与结构化日志，失败时自动回滚并输出可读报告。
9. **测试覆盖体系**（全链路）
   - 构建渲染器单测、Service 集成测、API 测以及生成项目的快照/构建验证，纳入 CI。
10. **组件映射配置化**（DSL → 前端）
    - 将语义组件映射抽离为可版本化配置（JSON/YAML），支持多组件库共存与热更新。

### 阶段 3：长期优化（按优先级穿插）
- **自动化差异分析**：输出 Sketch vs DSL 差异报告，保障设计一致性。
- **插件机制设计**：提供 `beforeRender`、`afterRender` 等扩展点，支持企业自定义组件或逻辑。
- **可视化/CLI 工具**：实现用户上传、选项配置、在线预览、下载的一体化体验。

## 执行提醒
- 单人开发建议以“先打通链路、再逐步补全”的顺序推进，阶段 1 完成后即可提供价值，再在阶段 2/3 逐步增强体验与覆盖面。
- 每阶段结束回顾 DSL 输出与前端产物，及时调整 schema、模板与映射规则，确保两侧持续对齐。

