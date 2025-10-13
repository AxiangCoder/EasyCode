# `converter` 应用

## 概览 (Overview)

`converter` 是本项目的核心应用，提供了一个功能强大的"设计到代码"转换服务。它能够接收设计文件（目前主要支持 Sketch 导出的 JSON 格式），通过一个可扩展的、由 Celery 驱动的异步处理管道，将其解析并转换为一份结构化的领域特定语言（DSL）产物，最终生成可运行的前端项目。

整个流程通过一套完整的 RESTful API 对外提供服务，并集成了大语言模型（LLM）来增强布局分析等核心能力。

## DSL 生成过程详解

### 1. 整体转换流程

DSL 生成过程分为以下几个关键阶段：

1. **预处理阶段**：解析 Sketch JSON 文件，建立符号映射关系
2. **布局分析阶段**：使用混合专家-仲裁策略分析图层布局
3. **样式映射阶段**：将设计样式映射到设计令牌
4. **DSL 构建阶段**：递归遍历图层树，构建结构化 DSL

### 2. 核心转换引擎

#### 2.1 SketchParser 核心方法

- **`count_nodes()`**: 预计算节点总数，用于进度跟踪
- **`run()`**: 执行完整的转换流程
- **`_preprocess_symbols()`**: 预处理 Symbol 实例，建立 ID 到名称的映射
- **`_find_main_artboard()`**: 找到主要画板作为转换起点
- **`_traverse_layer()`**: 递归遍历图层树，构建 DSL 结构
- **`_map_styles_to_tokens()`**: 将图层样式映射到设计令牌

#### 2.2 布局分析策略

采用"混合专家-仲裁"模式，结合两种分析引擎：

1. **几何规则引擎** (`_analyze_with_rules`): 基于精确的数学计算，识别对齐的行列布局
2. **语义分析引擎** (`_analyze_with_llm`): 基于 LLM 的语义理解，识别功能内聚的组件
3. **仲裁机制** (`_resolve_conflicts`): 解决冲突，选择最优布局方案

### 3. DSL 结构详解

DSL 是一个树状结构，每个节点包含以下核心字段：

#### 3.1 基础字段

- **`type`**: 节点类型，如 `"page"`, `"div"`, `"text"`, `"img"` 等
- **`name`**: 图层名称，来自 Sketch 原始数据
- **`do_objectID`**: Sketch 对象的唯一标识符
- **`children`**: 子节点数组，形成树状结构

#### 3.2 样式字段 (`style`)

- **`width/height`**: 节点尺寸
- **`backgroundColor`**: 背景色（可能映射到设计令牌）
- **`textColor`**: 文本颜色
- **`font`**: 字体样式（可能映射到设计令牌）
- **`borderRadius`**: 圆角半径
- **`opacity`**: 透明度
- **`borderWidth/borderColor`**: 边框样式

#### 3.3 布局字段 (`layout`)

- **`type`**: 布局类型
  - `"absolute"`: 绝对定位
  - `"flex"`: 弹性布局
  - `"grid"`: 网格布局
- **`direction`**: 布局方向（仅 flex 布局）
  - `"row"`: 水平排列
  - `"column"`: 垂直排列
- **`position`**: 定位方式
  - `"absolute"`: 绝对定位
  - `"relative"`: 相对定位
- **`top/left/right/bottom`**: 定位坐标
- **`gap`**: 子元素间距
- **`alignItems`**: 交叉轴对齐方式
- **`justifyContent`**: 主轴对齐方式
- **`padding`**: 内边距对象

#### 3.4 特殊字段

- **`content`**: 内容对象（主要用于文本节点）
  - `text`: 文本内容
- **`group_identifier`**: 虚拟组标识符（由布局分析生成）
- **`exportOptions`**: 导出选项（图片节点）

### 4. 布局分析详解

#### 4.1 混合专家-仲裁策略

该策略的核心思想是"并行咨询，统一仲裁"：

1. **并行分析**：几何规则引擎和 LLM 语义引擎同时分析图层
2. **几何校验**：对 LLM 结果进行几何合理性校验
3. **冲突解决**：仲裁机制解决不同引擎的冲突建议
4. **属性计算**：Python 精确计算布局属性（gap、对齐等）

#### 4.2 虚拟组机制

当多个图层被识别为一个布局组时，系统会创建"虚拟组"：

- 虚拟组包含 `group_identifier` 字段
- 子元素的坐标会相对于虚拟组进行调整
- 虚拟组本身具有完整的布局属性

#### 4.3 布局类型识别

- **Flex 布局**：识别为行或列排列的元素组
- **Grid 布局**：识别为网格排列的元素组
- **绝对布局**：无法归类的元素使用绝对定位

## 代码生成过程详解

### 1. 前端项目生成流程

代码生成过程将 DSL 转换为可运行的 React + TypeScript 项目：

1. **DSL 解析**：解析 DSL 结构，提取页面信息
2. **组件生成**：为每个页面生成 React 组件
3. **路由配置**：生成 React Router 配置
4. **项目打包**：基于 Vite 模板生成完整项目

### 2. FrontendRenderer 核心功能

#### 2.1 文件生成

- **页面组件**：为每个 DSL 页面生成对应的 React 组件文件
- **路由配置**：生成 `router.tsx` 文件，配置页面路由
- **应用入口**：生成 `App.tsx` 文件作为应用入口

#### 2.2 组件渲染

- **节点转换**：将 DSL 节点转换为 JSX 元素
- **样式转换**：将 DSL 样式转换为 React 内联样式
- **布局处理**：处理 flex、grid、absolute 等布局类型

### 3. 样式转换详解

#### 3.1 样式映射

- **驼峰命名**：将 CSS 属性名转换为驼峰命名
- **单位处理**：为数值添加 `px` 单位
- **布局属性**：将 DSL 布局属性转换为 CSS 样式

#### 3.2 布局转换

- **Flex 布局**：`display: flex`, `flexDirection`, `gap` 等
- **Grid 布局**：`display: grid`（基础实现）
- **绝对定位**：`position: absolute`, `top/left` 等

### 4. 项目模板结构

基于 Vite + React + TypeScript + Tailwind CSS 模板，生成完整的项目结构：

```
conversion_out/{task_id}/
├── code/                    # 生成的前端项目
│   ├── src/
│   │   ├── pages/           # 生成的页面组件
│   │   │   ├── ListPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── Page.tsx
│   │   ├── App.tsx         # 应用入口
│   │   ├── router.tsx      # 路由配置
│   │   ├── main.tsx        # 应用启动
│   │   ├── index.css       # 样式文件
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共资源
│   ├── package.json        # 项目依赖
│   ├── vite.config.ts      # Vite 配置
│   ├── tsconfig.json       # TypeScript 配置
│   └── README.md           # 项目说明
├── code.zip               # 项目压缩包
└── dsl.json              # DSL 输出文件
```

#### 4.1 生成的页面组件示例

每个页面组件都是完整的 React 组件，包含：

```tsx
import { FC } from 'react'

const ListPage: FC = () => (
  <div data-converted-id="02C3973E-BDCA-422F-B50F-F41F41AEF540" 
       style={{ backgroundColor: '#FFFFFF', width: '100%', height: '100%' }}>
    <div data-converted-id="692a01ec-92a8-4956-8394-bd313a487efb" 
         data-group-identifier="Virtual Group - flex" 
         style={{ width: '332px', height: '42px', display: 'flex', flexDirection: 'row', gap: '16px' }}>
      {/* 子组件内容 */}
    </div>
  </div>
)

export default ListPage
```

#### 4.2 路由配置示例

自动生成的路由配置支持多页面导航：

```tsx
import { createBrowserRouter, Navigate } from 'react-router-dom'
import ListPage from './pages/ListPage'
import LoginPage from './pages/LoginPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to='/ListPage' replace />,
  },
  {
    element: <ListPage />,
    path: '/ListPage',
  },
  {
    element: <LoginPage />,
    path: '/LoginPage',
  },
])
```

## 核心架构 (Core Architecture)

本应用采用分层架构设计，确保了各部分职责清晰、高内聚、低耦合。

### 1. API 层 (`views.py`, `serializers.py`, `urls.py`, `permissions.py`)

- **功能**：使用 Django Rest Framework (DRF) 构建，为前端或客户端提供标准的 RESTful 接口
- **核心组件**：
  - `ConversionTaskViewSet`: 管理转换任务的 CRUD 操作
  - `ConversionResultViewSet`: 管理转换结果的查看和下载
  - `DesignTokensViewSet`: 管理设计令牌的上传和管理
- **权限控制**：通过 `permissions.py` 实现对象级权限，确保用户只能访问自己的数据
- **数据验证**：通过 `serializers.py` 进行数据序列化、反序列化及验证

### 2. 任务队列层 (`tasks.py`)

- **功能**：使用 Celery 处理耗时的设计文件转换任务，避免阻塞 API 请求
- **核心任务**：
  - `convert_design_file_task`: 异步转换任务入口
  - `progress_callback`: 实时进度汇报机制
- **优势**：提升用户体验，支持长时间运行的转换任务

### 3. 服务层 (`service/`)

#### 3.1 ConversionTaskService
- **职责**：管理 `ConversionTask` 的完整生命周期
- **功能**：状态变更、启动和结束处理、进度跟踪

#### 3.2 DesignConverterService
- **职责**：编排具体的转换步骤
- **功能**：
  - 文件验证和加载
  - 设计令牌加载
  - 解析器调用
  - 结果保存

#### 3.3 LLMClient
- **职责**：封装大语言模型服务
- **功能**：
  - API 调用封装
  - 重试机制
  - Token 用量统计
  - 错误处理

#### 3.4 FrontendGenerationService
- **职责**：将 DSL 转换为前端项目
- **功能**：
  - 基于模板生成项目结构
  - 渲染 React 组件
  - 生成路由配置
  - 项目打包

### 4. 解析器层 (`parsers/`)

#### 4.1 基础架构
- **设计模式**：可插拔的策略模式
- **扩展性**：支持多种设计源（Sketch、Figma、Adobe XD 等）
- **接口定义**：`BaseParser` 抽象基类

#### 4.2 SketchParser 核心功能
- **`count_nodes()`**: 预计算节点总数，用于进度跟踪
- **`run()`**: 执行完整的转换流程
- **`_preprocess_symbols()`**: 预处理 Symbol 实例
- **`_traverse_layer()`**: 递归遍历图层树
- **`_map_styles_to_tokens()`**: 样式到令牌的映射

### 5. 布局策略层 (`layout_strategies/`)

#### 5.1 混合专家-仲裁策略
- **几何规则引擎**：基于数学计算的精确布局识别
- **语义分析引擎**：基于 LLM 的语义理解
- **仲裁机制**：解决冲突，选择最优方案

#### 5.2 布局类型支持
- **Flex 布局**：行/列排列的弹性布局
- **Grid 布局**：网格布局
- **绝对布局**：精确坐标定位

### 6. 前端渲染层 (`frontend_renderer/`)

#### 6.1 FrontendRenderer
- **职责**：将 DSL 渲染为 React 组件
- **功能**：
  - 节点到 JSX 的转换
  - 样式到内联样式的转换
  - 布局属性的处理

#### 6.2 文件生成
- **页面组件**：为每个 DSL 页面生成 React 组件
- **路由配置**：生成 React Router 配置
- **应用入口**：生成应用启动文件

#### 6.3 生成文件的特点

- **数据属性**：每个元素都包含 `data-converted-id` 属性，用于追踪原始设计元素
- **虚拟组标识**：布局分析生成的虚拟组包含 `data-group-identifier` 属性
- **内联样式**：所有样式都以内联方式应用，确保像素级还原
- **类型安全**：使用 TypeScript 确保类型安全
- **固定尺寸**：当前版本生成固定尺寸的布局，暂不支持响应式适配

## 关键组件与功能 (Key Components and Functionality)

### 1. 数据模型 (`models.py`)

#### 1.1 DesignTokens
- **用途**：管理用户上传的设计令牌（Design Tokens）JSON 文件
- **字段**：
  - `name`: 令牌配置名称
  - `file`: 设计令牌 JSON 文件
- **功能**：为转换过程提供设计系统支持

#### 1.2 ConversionTask
- **用途**：记录每一次转换任务的完整信息
- **核心字段**：
  - `source_type`: 设计源类型（sketch、figma）
  - `source_url`: 设计源 URL（Figma 链接）
  - `input_file`: 输入的设计文件（Sketch 文件）
  - `design_tokens`: 关联的设计令牌
  - `status`: 任务状态（pending、processing、completed、failed）
  - `phase`: 任务阶段（pending、dsl_conversion、frontend_generation、completed）
  - `progress`: 转换进度（0-100）
  - `input_nodes`: 输入的总节点数
  - `handled_nodes`: 已处理的节点数
  - `hidden_nodes`: 隐藏的节点数
- **功能**：跟踪任务状态、进度、错误信息和统计数据

#### 1.3 ConversionResult
- **用途**：存储转换成功后的产物
- **核心字段**：
  - `dsl_output`: DSL 输出结果
  - `token_report`: 令牌使用报告
  - `llm_usage`: LLM token 用量汇总
  - `project_download_path`: 生成的前端项目压缩包路径
- **功能**：与 `ConversionTask` 一对一关联，存储转换产物

### 2. API 端点 (`views.py`)

#### 2.1 转换任务管理
- **`POST /api/v1/converter/tasks/`**: 创建转换任务
- **`GET /api/v1/converter/tasks/{id}/`**: 查看任务详情
- **`GET /api/v1/converter/tasks/{id}/progress/`**: 获取实时进度
- **`POST /api/v1/converter/tasks/{id}/retry/`**: 重试失败的任务
- **`POST /api/v1/converter/tasks/{id}/cancel/`**: 取消任务

#### 2.2 转换结果管理
- **`GET /api/v1/converter/results/{id}/`**: 获取转换结果
- **`GET /api/v1/converter/results/{id}/download_dsl/`**: 下载 DSL 文件
- **`GET /api/v1/converter/results/{id}/download_report/`**: 下载令牌报告

#### 2.3 设计令牌管理
- **`GET /api/v1/converter/tokens/`**: 获取用户的令牌列表
- **`POST /api/v1/converter/tokens/`**: 上传新的令牌文件
- **`DELETE /api/v1/converter/tokens/{id}/`**: 删除令牌文件

### 3. 异步工作流

#### 3.1 任务创建流程
1. 用户通过 API `POST /tasks/` 创建转换任务
2. `ConversionTaskViewSet` 创建 `ConversionTask` 记录
3. 立即触发 `convert_design_file_task.delay()` 异步任务

#### 3.2 转换执行流程
1. Celery Worker 接收任务，调用 `ConversionTaskService`
2. 服务层调用 `DesignConverterService` 进行转换
3. 解析器层执行 DSL 生成
4. 前端渲染层生成 React 项目
5. `progress_callback` 实时更新任务进度
6. 任务完成后，创建 `ConversionResult` 记录

#### 3.3 进度跟踪机制
- **实时更新**：通过 `progress_callback` 机制实时汇报进度
- **阶段划分**：DSL 转换阶段和前端生成阶段
- **节点统计**：跟踪已处理节点数和总节点数

### 4. 错误处理 (`exceptions.py`)

#### 4.1 自定义异常体系
- **`ValidationError`**: 数据验证错误
- **`ConversionError`**: 转换过程错误
- **`TaskNotFoundError`**: 任务不存在错误
- **`FileProcessingError`**: 文件处理错误
- **`LLMServiceError`**: LLM 服务错误
- **`UnsupportedFileFormatError`**: 不支持的文件格式错误

#### 4.2 错误处理优势
- **结构化错误信息**：API 返回可预期的错误格式
- **错误分类**：不同类型的错误有不同的处理方式
- **用户友好**：提供清晰的错误描述和解决建议

### 5. 后台管理 (`admin.py`)

#### 5.1 管理界面功能
- **数据查看**：查看所有转换任务和结果
- **状态监控**：监控任务执行状态
- **调试支持**：查看详细的错误信息和日志
- **数据管理**：管理设计令牌和用户数据

#### 5.2 管理优势
- **开发调试**：方便开发者进行问题排查
- **运维监控**：管理员可以监控系统运行状态
- **数据维护**：支持数据的增删改查操作

## 使用流程 (API Flow)

### 1. 完整转换流程

#### 1.1 准备阶段（可选）
- **上传设计令牌**: `POST /api/v1/converter/tokens/` 上传 `design_tokens.json` 文件
- **目的**: 为转换过程提供设计系统支持，提高样式一致性

#### 1.2 创建转换任务
- **端点**: `POST /api/v1/converter/tasks/`
- **请求参数**:
  - `source_type`: 设计源类型（`sketch` 或 `figma`）
  - `input_file`: Sketch 文件（当 `source_type` 为 `sketch` 时）
  - `source_url`: Figma 链接（当 `source_type` 为 `figma` 时）
  - `design_tokens`: 设计令牌 ID（可选）
- **响应**: 返回任务详情，包含任务 ID

#### 1.3 监控转换进度
- **查看任务状态**: `GET /api/v1/converter/tasks/{id}/`
- **获取实时进度**: `GET /api/v1/converter/tasks/{id}/progress/`
- **进度字段**:
  - `status`: 任务状态（pending、processing、completed、failed）
  - `phase`: 当前阶段（dsl_conversion、frontend_generation）
  - `progress`: 进度百分比（0-100）
  - `handled_nodes`: 已处理节点数
  - `input_nodes`: 总节点数

#### 1.4 获取转换结果
- **查看结果**: `GET /api/v1/converter/results/{id}/`
- **结果包含**:
  - `dsl_output`: DSL 结构化数据
  - `token_report`: 令牌使用报告
  - `llm_usage`: LLM 使用统计
  - `project_download_path`: 前端项目路径

#### 1.5 下载产物文件
- **DSL 文件**: `GET /api/v1/converter/results/{id}/download_dsl/`
- **令牌报告**: `GET /api/v1/converter/results/{id}/download_report/`
- **前端项目**: 通过 `project_download_path` 字段获取下载路径

### 2. 错误处理流程

#### 2.1 任务失败处理
- **查看错误信息**: 通过任务详情查看 `error_message` 字段
- **重试任务**: `POST /api/v1/converter/tasks/{id}/retry/`
- **取消任务**: `POST /api/v1/converter/tasks/{id}/cancel/`

#### 2.2 常见错误类型
- **文件格式错误**: 检查上传的文件格式是否正确
- **解析错误**: 检查设计文件是否完整
- **LLM 服务错误**: 检查 LLM 服务配置和网络连接
- **权限错误**: 检查用户权限和文件访问权限

### 3. 最佳实践

#### 3.1 设计文件准备
- **Sketch 文件**: 确保导出为 JSON 格式，包含完整的图层信息
- **图层命名**: 使用有意义的图层名称，便于语义分析
- **组件组织**: 合理组织图层结构，避免过深的嵌套

#### 3.2 设计令牌配置
- **颜色令牌**: 定义常用的颜色变量
- **字体令牌**: 定义字体大小和样式
- **间距令牌**: 定义常用的间距值
- **圆角令牌**: 定义常用的圆角值

#### 3.3 性能优化
- **文件大小**: 控制设计文件大小，避免过大的文件
- **节点数量**: 减少不必要的图层，提高转换效率
- **并发限制**: 避免同时创建过多转换任务

### 4. 扩展功能

#### 4.1 多页面支持
- 系统自动识别多个画板，生成多个页面组件
- 每个页面对应一个 React 组件文件
- 自动生成路由配置，支持页面导航

#### 4.2 响应式设计（规划中）
- 未来版本将支持不同屏幕尺寸的布局适配
- 计划自动生成响应式 CSS 样式
- 将支持移动端和桌面端的不同布局

#### 4.3 组件复用
- 识别重复的组件模式
- 生成可复用的 React 组件
- 支持组件的参数化配置
