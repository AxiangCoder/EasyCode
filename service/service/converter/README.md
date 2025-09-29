# `converter` 应用

## 概览 (Overview)

`converter` 是本项目的核心应用，提供了一个功能强大的“设计到代码”转换服务。它能够接收设计文件（目前主要支持 Sketch 导出的 JSON 格式），通过一个可扩展的、由 Celery 驱动的异步处理管道，将其解析并转换为一份结构化的领域特定语言（DSL）产物。

整个流程通过一套完整的 RESTful API 对外提供服务，并集成了大语言模型（LLM）来增强布局分析等核心能力。

## 核心架构 (Core Architecture)

本应用采用分层架构设计，确保了各部分职责清晰、高内聚、低耦合。

1.  **API 层 (`views.py`, `serializers.py`, `urls.py`, `permissions.py`)**
    *   使用 Django Rest Framework (DRF) 构建，为前端或客户端提供标准的 RESTful 接口。
    *   通过 `ViewSet` 暴露对核心资源（转换任务、结果、设计令牌）的 CRUD 操作。
    *   `serializers.py` 负责数据模型的序列化、反序列化及验证。
    *   `permissions.py` 定义了精细的对象级权限，确保用户只能访问自己的数据。

2.  **任务队列层 (`tasks.py`)**
    *   使用 Celery 处理耗时的设计文件转换任务，避免阻塞 API 请求，提升用户体验。
    *   定义了 `convert_design_file_task` 异步任务，作为触发转换流程的入口。
    *   包含一个精巧的 `progress_callback` 机制，用于在转换过程中向数据库实时汇报进度。

3.  **服务层 (`service/`)**
    *   作为业务逻辑的核心，连接了 API 层和底层的解析引擎。
    *   `ConversionTaskService`: 负责管理 `ConversionTask` 的完整生命周期，如状态变更、启动和结束处理。
    *   `DesignConverterService`: 负责编排具体的转换步骤，包括文件验证、加载设计令牌、调用解析器以及保存最终结果。
    *   `LLMClient`: 一个独立的 LLM 服务客户端，封装了对大模型（如 OpenAI、SiliconFlow）的 API 调用、重试及 Token 用量统计逻辑，为上层提供稳定的 AI 能力。

4.  **解析器层 (Parser Layer) (`parsers/`)**
    *   这是整个转换过程的“大脑”，采用可插拔的策略模式设计，为未来支持 Figma, Adobe XD 等多种设计源奠定了基础。
    *   `parsers/base.py` (`BaseParser`): 定义了所有解析器必须遵循的抽象基类接口，包含 `count_nodes` (用于预计算节点总数) 和 `run` (执行转换) 两个核心方法。
    *   `parsers/__init__.py` (`get_parser_class`): 解析器工厂，根据任务的 `source_type` 返回对应的解析器类，实现了动态加载。
    *   `parsers/sketch/converter.py` (`SketchParser`): `BaseParser` 的具体实现，负责深度解析 Sketch JSON 的图层树。其内部保留了核心的递归遍历算法 (`_traverse_layer`)、样式令牌映射 (`_map_styles_to_tokens`) 以及基于规则和 LLM 的混合布局分析策略。

## 关键组件与功能 (Key Components and Functionality)

*   **`models.py`**: 定义了三大核心数据模型：
    *   `DesignTokens`: 用于管理用户上传的设计令牌（Design Tokens）JSON 文件。
    *   `ConversionTask`: 记录每一次转换任务的完整信息。它跟踪任务状态、进度、错误信息和统计数据。通过 `source_type` (如 `sketch`, `figma`) 和 `source_url`、`input_file` 字段，它现在可以灵活支持多种设计源。
*   `ConversionResult`: 与 `ConversionTask` 一对一关联，存储成功的转换产物，包括最终的 `dsl_output`、`token_report`、`llm_usage` 以及生成的前端项目压缩包路径 `project_download_path`。

*   **API 端点 (`views.py`)**:
    *   `/api/v1/converter/tasks/`: 创建、查看、重试或取消转换任务。
    *   `/api/v1/converter/tasks/{id}/progress/`: 轮询获取指定任务的实时进度。
    *   `/api/v1/converter/results/{id}/`: 获取转换成功后的结果。
    *   `/api/v1/converter/results/{id}/download_dsl/`: 下载 DSL 产物文件。
    *   `/api/v1/converter/results/{id}/download_report/`: 下载令牌使用情况报告。
    *   `/api/v1/converter/tokens/`: 管理用户的设计令牌。

*   **异步工作流**:
    1.  用户通过 API `POST /tasks/` 创建一个转换任务。
    2.  `ConversionTaskViewSet` 创建 `ConversionTask` 记录，并立即触发 `convert_design_file_task.delay()`。
    3.  Celery Worker 接收任务，调用 `ConversionTaskService`。
    4.  服务层和解析引擎层协同完成复杂的转换工作。
    5.  `progress_callback` 在此期间不断更新任务进度。
    6.  任务完成后，创建 `ConversionResult` 记录并更新任务状态。

*   **错误处理 (`exceptions.py`)**:
    *   定义了一套完整的自定义异常体系（如 `ValidationError`, `ConversionError`, `TaskNotFoundError`），使得 API 能够返回结构化、可预期的错误信息。

*   **后台管理 (`admin.py`)**:
    *   将所有核心模型都注册到了 Django Admin 后台，方便开发者和管理员进行数据查看、调试和管理。

## 使用流程 (API Flow)

1.  **（可选）上传设计令牌**: `POST /tokens/` 来上传一份 `design_tokens.json` 文件。
2.  **创建转换任务**: `POST /tasks/`，请求体中需包含 `source_type` 字段。当 `source_type` 为 `sketch` 时，附带设计文件 `input_file`；当为 `figma` 时，提供 `source_url`。API 将立即返回一个任务详情，包含任务 ID。
3.  **轮询进度**: `GET /tasks/{id}/` 或 `GET /tasks/{id}/progress/` 来监控任务的 `status` 和 `progress` 字段。
4.  **获取结果**: 任务状态变为 `completed` 后，通过 `GET /results/{id}/` 获取包含 DSL 产物的完整结果。
5.  **下载产物**: 根据需要调用以下端点，下载不同的产物文件：
    *   `GET /results/{id}/download_dsl/`: 下载核心的 DSL JSON 文件。
    *   `GET /results/{id}/download_html/`: 下载用于快速预览的 HTML 文件。
    *   `GET /results/{id}/download_report/`: 下载设计令牌使用情况的分析报告。
