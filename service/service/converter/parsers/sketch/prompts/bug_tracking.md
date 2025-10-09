# Bug Tracking

## Bug 发现情况

1.  **缺少 `justify-content` 和 `align-items` 字段**:
    *   当前的 LLM 布局分析未能稳定返回 `justify-content` 和 `align-items` 这两个关键的 flexbox 属性，导致前端渲染时无法精确控制对齐方式。

2.  **`Virtual Group - flex` 的生成逻辑不明确**:
    *   当 LLM 分析结果包含多个布局组或离群元素时，会创建虚拟组（Virtual Group）。需要明确其生成条件、坐标计算逻辑以及如何处理嵌套层级，以确保布局的准确性。

3.  **如何使用 `padding` 优雅地实现布局**:
    *   当前的布局分析主要依赖 `gap` 属性。可以探索在父容器上使用 `padding` 并结合 `gap` 的方式，以更灵活、更优雅地实现 `flex` 或 `grid` 布局，特别是在处理边缘间距时。

## Bug 修复详细情况

### 1. 修复 `justify-content` 和 `align-items` 字段缺失问题

*   **解决方案**:
    *   修改 `layout_analysis_prompt.md` 中的提示词，明确要求 LLM 分析并返回 `justifyContent` 和 `alignItems` 属性。
    *   在 Schema 定义中将这两个字段设为可选，并提供详细的说明和示例。
*   **注意事项**:
    *   需要确保 LLM 能够理解这两个属性在不同 `direction` (row/column) 下的含义。
    *   后端 `_traverse_layer` 函数需要能够正确处理返回结果中可能包含这两个新字段的情况。

### 2. 明确 `Virtual Group - flex` 的生成逻辑

*   **解决方案**:
    *   (待定) 进一步分析和重构 `_process_llm_layout_analysis` 函数。
*   **注意事项**:
    *   (待定)

### 3. 使用 `padding` 优化布局实现

*   **解决方案**:
    *   (待定) 探索在提示词中引导 LLM 识别可以转换为 `padding` 的布局模式。
*   **注意事项**:
    *   (待定)
