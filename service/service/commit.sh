#!/bin/bash

# 1. 将所有更改添加到暂存区
echo "Adding all changes to staging area..."
git add .

# 2. 提交更改并附带详细信息
echo "Committing changes..."
git commit -m "feat(converter): 实现可插拔的解析器架构" -m "重构核心转换引擎，通过引入基于策略模式的解析器架构，以支持多种设计源（如 Sketch、Figma）。此次重构将 DesignConverterService 与具体的 SketchConverter 实现解耦，为未来接入新的设计工具提供了扩展性。

主要变更包括：

- **引入解析器策略模式**:
    - 新增 converter/parsers/base.py 文件，定义了抽象基类 BaseParser，为所有解析器提供统一接口。
    - 在 converter/parsers/__init__.py 中创建了解析器工厂 get_parser_class，用于根据 source_type 动态选择解析器。
    - 将原 sketch_converter 逻辑迁移至 converter/parsers/sketch/，并将其重构为实现 BaseParser 接口的 SketchParser。

- **增强数据模型**:
    - 为 ConversionTask 模型添加 source_type 和 source_url 字段，以支持处理不同的设计源。
    - 更新 ConversionTaskSerializer，增加验证逻辑以确保 Sketch 类型任务包含 input_file，Figma 类型任务包含 source_url。

- **重构服务层**:
    - DesignConverterService 现在作为中心编排器，负责获取解析器、预计算节点、执行转换和保存结果。
    - ConversionTaskService 和 Celery 异步任务（tasks.py）已更新，以适配新的服务流程。

- **修复与清理**:
    - 修复 llm_service.py 中指向旧目录的错误导入路径。
    - 恢复 SketchParser 中被误删为省略号的完整 LLM 提示词。
    - 移除已无用的 sum_nodes 函数，其逻辑已合并到 SketchParser.count_nodes 中。

- **文档**:
    - 更新 converter/README.md，使其准确反映新的解析器架构、模型变更和 API 用法。"

echo "Commit script created successfully."
echo "To execute it, run the following command in your terminal:"
echo "bash commit.sh"
