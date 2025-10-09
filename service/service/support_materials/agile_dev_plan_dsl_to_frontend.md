# “DSL 到前端代码”渲染器 - 敏捷开发文档 (V11 - 最终执行版)

本文档为 Sprint 1 的最终执行计划，聚焦于以最快速度打通核心业务流程，并包含了各阶段的测试验证方法和详细的子任务分解。

## 🚀 Sprint 1 核心目标 (Sprint Goal)

**打通“设计稿 -> 可下载的前端项目”的自动化核心流程。**

本次冲刺的唯一目标是实现一个完整的“快乐路径”（Happy Path）：用户上传设计稿，系统能自动完成 DSL 转换和前端代码生成，并最终提供一个可下载、可构建的 React 项目压缩包。所有非此路径上的功能（如进度条优化、Bug修复、架构抽象）都暂时移出，以保证核心价值的快速交付。

--- 

## 🏃 Sprint 1 核心任务列表 (按优先级排序)

我们将按以下顺序，一步步构建起这个核心流程。

### Epic 1: 流程再造与数据模型改造 (P0 - 最高优先级)

*   **用户故事**: 作为系统管理员，我需要将两个独立的任务（DSL生成、前端生成）串联起来，并调整数据模型以支持最终的项目下载。

*   **子任务分解 (Breakdown)**:
    1.  **数据模型迁移**:
        *   **1.1**: 在 `converter/models.py` 的 `ConversionResult` 模型中，删除 `html_output` 和 `html_preview` 字段。
        *   **1.2**: 在同一模型中，新增 `project_download_path = models.CharField(max_length=1024, blank=True, null=True, help_text="生成的前端项目压缩包存储路径")`。
        *   **1.3**: 运行 `python manage.py makemigrations converter` 生成新的数据库迁移文件。
        *   **1.4**: 审查生成的迁移文件，确认其正确反映了字段的增删。
        *   **1.5**: 运行 `python manage.py migrate converter` 应用迁移。
    2.  **序列化器与旧逻辑清理**:
        *   **2.1**: 在 `converter/serializers.py` 中，更新 `ConversionResultSerializer`，从 `fields` 列表中移除 `html_output` 和 `html_preview`，并添加 `project_download_path` (建议设为 `read_only=True`)。
        *   **2.2**: 全局搜索 `html_preview` 和 `generate_html_from_dsl`，定位并删除所有相关的代码，特别是 `DesignConverterService` 中的调用逻辑和 `converter/utils.py` 中的工具函数。
    3.  **前端项目模板搭建**:
        *   **3.1**: 创建目录 `converter/project_templates/vite-react-ts-tailwind`。
        *   **3.2**: 在该目录中，通过 `npm create vite@latest . -- --template react-ts` 初始化一个最小化的 Vite + React + TS 项目。运行前请使用 `nvm use 20` 切换至 Node.js 20，以满足 Vite 7 和 React Router 7 的版本要求。
        *   **3.3**: 根据 TailwindCSS v4 官方文档为 Vite 项目进行配置：安装 `tailwindcss`、`postcss`、`autoprefixer`、`@tailwindcss/vite`，在 `vite.config.ts` 中引入 `tailwindcss()` 插件，并在 `src/index.css` 中保留 `@tailwind base; @tailwind components; @tailwind utilities;` 即可。
        *   **3.4**: 安装并配置路由。运行 `npm install react-router-dom`（需在 Node.js 20 环境下执行），并在 `src/main.tsx` 中使用 `<BrowserRouter>` 包裹根组件，为项目集成路由能力。
        *   **3.5**: 清理 `App.tsx` 中的默认内容，使其成为一个干净的渲染容器或路由出口(Outlet)。
        *   **3.6**: 在模板目录中添加 `.gitignore` 文件，忽略 `node_modules` 和 `dist` 等构建产物，并删除 `node_modules` 目录本身。
    4.  **任务链实现**:
        *   **4.1**: 在 `converter/tasks.py` 中，定义一个空的占位任务 `generate_frontend_project_task(conversion_result_id: str)`。
        *   **4.2**: 在 `convert_design_file_task` 任务的业务逻辑成功执行的末尾，添加对新任务的调用：`generate_frontend_project_task.delay(conversion_result.id)`。

*   **✅ 测试验证方法**:
    1.  **单元测试**: 运行 `manage.py test converter`，确保在模型和序列化器层面，移除旧字段、添加新字段后，所有现有的测试用例依然通过。
    2.  **集成测试 (手动)**: 
        a. 在 Django Admin 后台或通过接口触发一次**旧的**设计转换任务。
        b. 观察 Celery worker 日志，确认 `convert_design_file_task` 成功执行，并在结尾处尝试调用（即使是失败的）`generate_frontend_project_task`。
        c. 检查 `ConversionResult` 数据库记录，确认 `html_output` 和 `html_preview` 字段已不存在，而 `project_download_path` 字段存在且为空。

### Epic 2: 基础前端生成服务 (P1 - 核心实现)

*   **用户故事**: 作为开发者，我需要一个能将包含多个页面的 DSL 渲染成一个带路由的 React 项目，并将其打包。

*   **子任务分解 (Breakdown)**:
    1.  **渲染器框架搭建**:
        *   **1.1**: 创建目录 `converter/frontend_renderer/` 及 `__init__.py` 文件。
        *   **1.2**: 在 `__init__.py` 中定义 `FileArtifact` 数据类和 `render_project(dsl: dict) -> list[FileArtifact]` 的主函数签名。
        *   **1.3**: 创建 `converter/frontend_renderer/renderer.py` 文件，用于存放核心渲染逻辑。
    2.  **多页面渲染与路由生成**:
        *   **2.1**: 在 `renderer.py` 中，实现一个核心的 `_render_node(node: dict) -> str` 递归函数，用于将单个 DSL 节点转换为 TSX 字符串。
        *   **2.2**: 实现一个辅助函数 `_convert_styles(node: dict) -> dict`，将 DSL 样式转换为 React 的内联样式对象。
        *   **2.3**: 在 `render_project` 主函数中，遍历 DSL 根节点的直接子节点（每个子节点代表一个页面）。
        *   **2.4**: 对每个页面节点，调用 `_render_node` 生成其完整的 TSX 组件代码，并创建一个对应的 `FileArtifact`（例如 `src/pages/LoginPage.tsx`）。
        *   **2.5**: 根据页面列表，生成一个 `router.tsx` 文件。此文件负责导入所有页面组件，并使用 `createBrowserRouter` 创建路由配置（例如，`/` 指向第一个页面，`/{pageName}` 指向其他页面）。
        *   **2.6**: 更新 `App.tsx` 的内容，使其渲染 `react-router-dom` 的 `<Outlet />` 组件，作为路由出口。
        *   **2.7**: 将所有生成的页面文件、`router.tsx` 和 `App.tsx` 作为 `FileArtifact` 列表返回。
    3.  **项目生成服务实现**:
        *   **3.1**: 创建 `converter/service/frontend_generation_service.py` 文件并定义 `FrontendGenerationService` 类。
        *   **3.2**: 在类中实现 `generate_project(self, result_id: str)` 方法，该方法包含完整的业务编排逻辑。
        *   **3.3**: **(文件操作)** 在方法内部，使用 `tempfile` 创建一个临时目录，并用 `shutil.copytree` 将项目模板复制进去。
        *   **3.4**: **(渲染与写入)** 调用 `frontend_renderer.render_project()`，遍历返回的 `FileArtifact` 列表，并将每个文件的内容写入到临时目录的对应路径下。
        *   **3.5**: **(打包与存储)** 使用 `shutil.make_archive` 将临时目录打包成 ZIP 文件，并将其移动到 `media` 目录下的一个永久存储位置。
        *   **3.6**: **(数据更新)** 更新 `ConversionResult` 实例的 `project_download_path` 字段，并保存到数据库。
    4.  **异步任务集成**:
        *   **4.1**: 在 `converter/tasks.py` 中，完善 `generate_frontend_project_task` 的函数体。
        *   **4.2**: 在任务内部，实例化 `FrontendGenerationService` 并调用其 `generate_project` 方法。
        *   **4.3**: 添加 `try...except` 异常捕获和日志记录，确保在生成失败时能追踪到错误。

*   **✅ 测试验证方法**:
    1.  **单元测试**: 为 `frontend_renderer` 编写单元测试，提供一个包含多个页面节点的 DSL 输入，断言 `render_project` 函数返回的 `FileArtifact` 列表中包含了所有预期的页面文件和 `router.tsx`。
    2.  **服务层测试**: 为 `FrontendGenerationService.generate_project` 编写测试，模拟调用并验证它是否正确地创建了一个 ZIP 压缩包，并且该压缩包的路径被成功写入了 `ConversionResult` 模型的 `project_download_path` 字段。
    3.  **端到端测试 (手动)**: 
        a. 触发一次完整的设计转换任务。
        b. 监控 Celery 日志，确认 `convert_design_file_task` 和 `generate_frontend_project_task` 均已成功执行。
        c. **手动解压并构建项目**：解压生成的 ZIP 文件，进入项目目录，依次执行 `npm install` 和 `npm run build`，确保项目可以无错误地成功构建。
        d. **手动运行和验证**：运行 `npm run dev`，访问浏览器，确认可以通过不同的 URL（如 `/` 和 `/page2`）访问到 DSL 中定义的多个不同页面。

--- 

## 🚀 Sprint 2 核心目标 (Sprint Goal)

**完善 Happy Path 产物的交付质量与可追溯性，确保所有可下载产物具备标准化结构与可观测状态。**

本次冲刺聚焦于补齐核心流程的质量防线：
*   生成记录不再出现空值，所有字段保持可解析状态；
*   进度上报包含阶段信息，用户能实时理解任务所处环节；
*   产物（DSL、前端代码）统一归档并提供标准命名，方便核验与二次使用。

--- 

## 🏃 Sprint 2 核心任务列表 (按优先级排序)

### Epic 3: 产物质量与交付保障 (P0 - 最高优先级)

#### Story 1: 修复 `ConversionTask` 空值问题（Bug 修复）
*   **背景 / 目标**: `ConversionTask` 的 `handled_nodes`、`hidden_nodes` 字段为数值类型，当前可能写入 `null`。目标是让这两个字段始终落成非空的数值（默认 `0`），确保后续流程无需判空即可处理。
*   **子任务分解 (Breakdown)**:
    1.  盘点模型定义、序列化器和任务逻辑中的默认值与赋值流程，明确空值出现的触发路径。
    2.  设计迁移方案，为相关字段设置默认值 `0`，并同步更新模型、序列化器与 Django Admin 展示。
    3.  调整任务与服务层写入逻辑，确保在创建或更新 `ConversionTask` 时填充非空数值。
    4.  手工触发一次完整的 DSL 转换流程，检查日志与数据库记录，确认字段稳定写入 `0`（且无 `null`）。
*   **验证方式**:
    *   手动核查任务执行日志与数据库字段值，确保字段写入为 `0`，无 `null` 记录。
*   **交付成果**:
    *   数据库层、序列化层已统一默认值为 `0`，历史数据按需回填完成。

#### Story 2: 进度条与阶段信息优化（进度条优化）
*   **背景 / 目标**: 现有进度反馈缺乏阶段区分。目标是引入“DSL 转换”“前端生成”两个阶段（70% / 30%），并向外暴露 `phase` 与进度值，使用户明确任务当前所处环节。
*   **子任务分解 (Breakdown)**:
    1.  梳理当前进度上报与存储流程，确认字段来源、API 输出结构以及前端读取方式。
    2.  在 DSL 转换与前端生成任务中，按 70% / 30% 更新进度数值，并写入对应 `phase` 标识。
    3.  更新相关序列化器、视图响应与文档说明，确保 `phase` 字段对外一致。
    4.  手工跑通任务链，观察进度数值与 `phase` 变化是否符合预期。
*   **验证方式**:
    *   手动触发任务并查看 API 返回值及日志，确认进度与阶段同步。
*   **交付成果**:
    *   API 响应中新增 `phase` 字段，进度值符合 70% / 30% 阶段划分；用户可在界面看到阶段切换。

#### Story 3: DSL 文件归档输出（DSL 文件归档输出）
*   **背景 / 目标**: 需要将原始 DSL 文件归档到 `media/conversion_out/{{task_id}}`，确保每次转换都有对应的 DSL 记录，便于追溯与验收。
*   **子任务分解 (Breakdown)**:
    1.  确认归档目录结构、权限及清理策略，避免与现有文件冲突。
    2.  在 DSL 转换成功后，将原始 DSL 文件写入归档目录，并评估历史数据回填策略（如需）。
    3.  更新模型或相关记录，保存归档路径，确保异步任务链可访问该信息。
    4.  手工检查归档目录与文件内容，确认写入成功且文件可读。
*   **验证方式**:
    *   手动核对 `media/conversion_out/{{task_id}}` 下的 DSL 文件存在且内容完整。
*   **交付成果**:
    *   `media/conversion_out/{{task_id}}` 目录固定生成 `dsl.json`（或等效命名），后续验收可直接使用。

#### Story 4: 统一前端压缩包命名（前端压缩包统一命名）
*   **背景 / 目标**: 生成的前端项目需统一命名为 `code.zip` 并与 DSL 文件同目录，保证所有下载产物具备一致路径与命名，便于验收与自动化处理。
*   **子任务分解 (Breakdown)**:
    1.  在前端生成服务中固定输出 `media/conversion_out/{{task_id}}/code.zip`，并同步更新 `project_download_path` 字段写入逻辑。
    2.  检查依赖该路径的 API、下载流程和前端逻辑，确保路径变更后正常。
    3.  明确重复生成时的覆盖策略，记录必要的日志信息。
    4.  手工解压 `code.zip`，确认目录结构与内容符合预期。
*   **验证方式**:
    *   手动下载并解压 `code.zip`，确认与 DSL 定义一致。
*   **交付成果**:
    *   `project_download_path` 固定为 `media/conversion_out/{{task_id}}/code.zip`，文档与前端说明同步更新。

--- 

## 📋 依赖与风险
*   数据迁移涉及历史 `ConversionTask` 记录，需在部署前评估并备份相关数据。
*   进度字段新增 `phase` 后，需同步通知前端与使用方，避免旧客户端解析失败。
*   `media/conversion_out/{{task_id}}` 目录权限需在部署前确认，避免归档写入失败。
*   前端压缩包覆盖策略需与运营或验收流程对齐，防止重复执行导致历史产物丢失。

--- 

## 🚀 Sprint 3 核心目标 (Sprint Goal)

**完成 P0 核心功能开发，实现模板样式基础完善、根元素样式完善和自定义属性注入，确保生成的前端项目具备完整的样式基础和调试能力。**

本次冲刺专注于核心渲染功能的完善：
*   集成 CSS Reset 样式，确保跨浏览器一致性
*   为根元素添加宽高 100% 属性，确保页面占满整个视口
*   为生成的 DOM 元素添加自定义属性，便于调试和元素识别

--- 

## 🏃 Sprint 3 核心任务列表 (按优先级排序)

### Epic 4: P0 核心功能完善 (P0 - 最高优先级)

#### Story 1: 模板样式基础完善
*   **目标**: 在项目模板中集成 CSS Reset 样式，确保跨浏览器一致性。
*   **子任务分解 (Breakdown)**:
    1.  在 `converter/project_templates/vite-react-ts-tailwind/src/` 目录下创建 `reset.css` 文件。
    2.  在 `src/index.css` 中引入 `@import './reset.css';`。
    3.  确保生成的代码在构建时正确加载 reset 样式。
*   **验证方式**:
    *   生成项目后检查 `src/index.css` 包含 reset 导入，且浏览器开发者工具中能看到 reset 样式生效。
*   **交付成果**:
    *   项目模板包含完整的 CSS Reset 样式，确保跨浏览器一致性。

#### Story 2: 根元素样式完善
*   **目标**: 为生成的根元素添加宽高 100% 属性，确保页面占满整个视口。
*   **子任务分解 (Breakdown)**:
    1.  在 `FrontendRenderer._render_node()` 中，为根节点（页面级别）自动添加 `width: '100%', height: '100%'` 样式。
    2.  确保根元素的样式优先级高于其他样式规则。
    3.  处理可能的样式冲突，确保根元素样式生效。
*   **验证方式**:
    *   生成项目后检查根元素包含 `width: 100%, height: 100%` 样式，且页面占满整个视口。
*   **交付成果**:
    *   所有生成的页面根元素都具备正确的宽高样式，确保页面占满视口。

#### Story 3: 自定义属性注入
*   **目标**: 为生成的 DOM 元素添加自定义属性，便于调试和元素识别。
*   **子任务分解 (Breakdown)**:
    1.  在 `FrontendRenderer._render_node()` 中，为每个生成的 div 元素添加 `data-converted-id` 属性。
    2.  属性值优先使用节点的 `do_objectID`，如不存在则使用 `name` 字段。
    3.  确保属性值经过适当的转义处理，避免特殊字符导致的问题。
*   **验证方式**:
    *   生成项目后检查页面源码，确认所有 div 元素都包含正确的 `data-dsl-id` 属性。
*   **交付成果**:
    *   所有生成的 DOM 元素都包含调试属性，便于开发和调试。

--- 

## 📦 产品待办列表 (Product Backlog)

### P0 - 核心功能完善 (Core Features)

*   **Bug-003: `src` 目录缺少路径别名**:
    *   **目标**: 修复前端模板配置中缺少路径别名的问题，支持模块引用使用统一的路径别名。
    *   **任务**:
        *   在前端模板的 `vite.config.ts` 中配置路径别名，支持 `@/` 和 `src/` 别名。
        *   更新 `tsconfig.json` 中的路径映射配置。
        *   确保生成的代码可以使用路径别名进行模块引用。
    *   **验证**: 生成项目后检查模块引用可以使用 `@/` 或 `src/` 别名，且编译无错误。
    *   **交付成果**: 前端模板支持统一的路径别名，提高代码可维护性。

### P1 - 功能增强 (Feature Enhancements)

*   **Bug-001: 未考虑嵌套路由**:
    *   **目标**: 修复路由生成逻辑，支持嵌套路由配置。
    *   **任务**:
        *   分析当前路由生成逻辑，识别嵌套路由支持缺失的原因。
        *   更新 `FrontendRenderer` 中的路由生成逻辑，支持嵌套路由结构。
        *   确保生成的 `router.tsx` 能正确处理嵌套路由配置。
    *   **验证**: 使用包含嵌套路由的 DSL 生成项目，确认路由配置正确且页面能正常访问。
    *   **交付成果**: 路由生成器支持嵌套路由配置，满足复杂页面结构需求。
*   **API 下载接口完善**:
    *   **目标**: 为前端用户提供可下载已生成项目压缩包的 API 端点。
    *   **任务**: 在 `converter/views.py` 的 `ConversionResultViewSet` 中添加新的 `@action`（例如 `download_project`），根据 `project_download_path` 提供压缩包下载能力。
    *   **验证**: 使用 Postman 或 Django REST Framework 测试用例请求该端点，确认返回 `200 OK`、`Content-Type` 为 `application/zip`，且下载文件可以成功解压并与 Epic 2 生成的内容一致。

*   **设备类型判断与响应式处理**:
    *   **目标**: 在代码生成阶段根据 DSL 数据判断目标设备类型（移动端/PC端），并应用相应的样式策略。
    *   **任务**:
        *   在 `FrontendRenderer` 中新增 `_detect_device_type(dsl: dict) -> str` 方法，基于 DSL 根节点或页面尺寸判断设备类型。
        *   根据设备类型调整生成的样式策略（如移动端优先使用 flex 布局，PC 端支持绝对定位）。
        *   在生成的 `App.tsx` 或页面组件中添加设备类型相关的 CSS 类或样式。
    *   **验证**: 分别生成移动端和 PC 端项目，检查样式策略差异是否符合预期。

*   **高级样式引擎**:
    *   **目标**: 实现一个真正的 `TailwindEngine`，将内联样式转换升级为 Tailwind CSS 类名，并处理 `tailwind.config.js` 的生成。
    *   **任务**:
        *   创建 `TailwindEngine` 类，实现样式到 Tailwind 类名的映射逻辑。
        *   生成 `tailwind.config.js` 配置文件，包含项目特定的设计令牌。
        *   优化生成的代码，减少内联样式，提高可维护性。
    *   **验证**: 生成项目后检查是否使用了 Tailwind 类名而非内联样式，且构建正常。

*   **压缩包解压与验收**:
    *   **目标**: 解压 `code.zip` 前先确认任务编号，解压后核对页面与 `dsl.json` 节点定义的一致性。
    *   **任务**:
        *   实现解压前的任务编号验证逻辑。
        *   开发页面与 DSL 节点的一致性检查工具。
        *   记录并修复发现的不一致问题。
    *   **验证**: 自动化验收流程能准确识别并报告不一致问题。

### P2 - 架构与功能扩展 (Architecture & Future Features)
*   **架构抽象**:
    *   **目标**: 引入 `FrameworkRenderer`, `StyleEngine`, `ComponentProvider` 等抽象基类，为支持 Vue、SCSS 等技术栈奠定基础。
    *   **任务**:
        *   设计并实现抽象基类体系。
        *   重构现有代码以使用新的抽象层。
        *   为 Vue、SCSS 等技术栈创建具体实现。
    *   **验证**: 新架构支持多技术栈，且现有功能不受影响。

*   **组件提供器**:
    *   **目标**: 实现 `AntdComponentProvider`，支持将语义节点映射为 Ant Design 组件。
    *   **任务**:
        *   创建组件映射规则和配置。
        *   实现语义节点到 Ant Design 组件的转换逻辑。
        *   生成包含 Ant Design 依赖的项目模板。
    *   **验证**: 生成的页面使用 Ant Design 组件，且样式和交互正常。

*   **项目在线预览与编辑**:
    *   **目标**: 开发在线服务，允许用户实时预览、修改和调试生成的项目。
    *   **任务**:
        *   设计在线预览架构。
        *   实现代码编辑和实时预览功能。
        *   集成调试工具和错误提示。
    *   **验证**: 用户可以在线编辑代码并实时看到效果。

*   **数据与事件绑定**:
    *   **目标**: 在 DSL 中定义数据绑定规范，并实现状态管理与事件函数的骨架生成。
    *   **任务**:
        *   设计 DSL 中的数据绑定语法。
        *   实现状态管理代码生成。
        *   生成事件处理函数骨架。
    *   **验证**: 生成的项目包含完整的状态管理和事件处理逻辑。

*   **测试与质量保障**:
    *   **目标**: 为代码生成器编写完整的单元/集成测试，并在生成的项目中包含测试模板。
    *   **任务**:
        *   为所有核心功能编写单元测试。
        *   实现集成测试套件。
        *   在生成的项目中包含测试模板和配置。
    *   **验证**: 测试覆盖率达到 90% 以上，生成的项目包含可运行的测试。