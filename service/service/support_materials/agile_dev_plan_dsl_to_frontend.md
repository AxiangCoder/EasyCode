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

### Epic 3: API 接口打通 (P2 - 完成闭环)

*   **用户故事**: 作为前端用户，我需要一个 API 端点来下载已生成的项目压缩包。
    1.  **Task**: **创建下载接口**。在 `converter/views.py` 的 `ConversionResultViewSet` 中，添加一个新的 `@action`（例如 `download_project`），它根据 `project_download_path` 字段提供文件下载功能。

*   **✅ 测试验证方法**:
    1.  **API 接口测试**: 使用 Postman 或编写 Django REST Framework 的 API 测试用例，请求新的 `download_project` 端点。
    2.  **验证**: 
        a. 确认接口返回的 HTTP 状态码为 `200 OK`。
        b. 确认返回的 `Content-Type` 是 `application/zip`。
        c. 确认下载的文件可以被正常解压，且内容与 Epic 2 中生成的文件完全一致。

--- 

## 📦 产品待办列表 (Product Backlog)

以下所有任务均已移出 Sprint 1，将在核心流程打通后，根据优先级进入后续的迭代计划。

### 高优先级待办 (High-Priority Backlog)
*   **Bug 修复**: 修复 `ConversionTask` 模型中 `handled_nodes` 和 `hidden_nodes` 可能为 `null` 的问题。
*   **进度条优化**: 实现两阶段（DSL生成 80%，前端生成 20%）进度计算，并在 API 中增加 `phase` 字段。
*   **高级样式引擎**: 实现一个真正的 `TailwindEngine`，将内联样式转换升级为 Tailwind CSS 类名，并处理 `tailwind.config.js` 的生成。

### 架构与功能扩展 (Future Features & Architecture)
*   **架构抽象**: 引入 `FrameworkRenderer`, `StyleEngine`, `ComponentProvider` 等抽象基类，为支持 Vue、SCSS 等技术栈奠定基础。
*   **组件提供器**: 实现 `AntdComponentProvider`，支持将语义节点映射为 Ant Design 组件。
*   **项目在线预览与编辑**: 开发在线服务，允许用户实时预览、修改和调试生成的项目。
*   **数据与事件绑定**: 在 DSL 中定义数据绑定规范，并实现状态管理与事件函数的骨架生成。
*   **测试与质量保障**: 为代码生成器编写完整的单元/集成测试，并在生成的项目中包含测试模板。