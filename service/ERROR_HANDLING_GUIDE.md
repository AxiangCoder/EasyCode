# 项目错误处理指南

## 概述

本项目实现了统一的错误处理机制，确保所有API接口在出错时返回一致的错误格式，并提供详细的错误信息以便调试和用户体验优化。

## 错误响应格式

### 标准错误响应格式

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "用户友好的错误消息",
        "details": {
            "field": "具体字段",
            "value": "错误值",
            "additional_info": "其他详细信息"
        }
    },
    "timestamp": "2024-01-01T12:00:00.000Z",
    "path": "/api/tasks/123/"
}
```

### 成功响应格式

```json
{
    "success": true,
    "data": { /* 实际数据 */ },
    "message": "操作成功",
    "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 自定义异常类

项目定义了以下自定义异常类：

### 基础异常类

- `ConverterException` - 转换服务异常基类
  - `code`: 错误代码
  - `message`: 错误消息
  - `details`: 详细信息字典

### 具体异常类

| 异常类 | 错误代码 | HTTP状态码 | 说明 |
|--------|----------|------------|------|
| `FileProcessingError` | FILE_PROCESSING_ERROR | 400 | 文件处理异常 |
| `ValidationError` | VALIDATION_ERROR | 400 | 数据验证异常 |
| `ConversionError` | CONVERSION_ERROR | 422 | 转换过程异常 |
| `ConfigurationError` | CONFIGURATION_ERROR | 500 | 配置异常 |
| `TokenMappingError` | TOKEN_MAPPING_ERROR | 422 | 令牌映射异常 |
| `UnsupportedFileFormatError` | UNSUPPORTED_FILE_FORMAT | 400 | 不支持的文件格式 |
| `TaskNotFoundError` | TASK_NOT_FOUND | 404 | 任务未找到异常 |
| `TaskAlreadyRunningError` | TASK_ALREADY_RUNNING | 409 | 任务已在运行异常 |
| `LLMServiceError` | LLM_SERVICE_ERROR | 503 | LLM服务异常 |

## 使用方法

### 1. 在视图中使用自定义异常

```python
from .exceptions import ConversionError, TaskNotFoundError

def my_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        # 处理任务
    except Task.DoesNotExist:
        raise TaskNotFoundError(task_id)
    except Exception as e:
        raise ConversionError(
            message=f"处理失败: {str(e)}",
            task_id=task_id
        )
```

### 2. 使用标准成功响应

```python
from core.utils import standardize_success_response

def my_view(request):
    data = {"key": "value"}
    return standardize_success_response(
        data=data,
        message="操作成功"
    )
```

### 3. 使用分页响应

```python
from core.utils import get_paginated_response

def list_view(request):
    queryset = MyModel.objects.all()
    return get_paginated_response(
        queryset,
        MyModelSerializer,
        request
    )
```

## 错误处理流程

1. **异常抛出**: 在业务逻辑中抛出适当的自定义异常
2. **全局捕获**: `core.utils.custom_exception_handler` 自动捕获所有异常
3. **格式化**: 将异常转换为标准错误响应格式
4. **日志记录**: 自动记录详细的错误日志
5. **响应返回**: 返回标准化的错误响应给客户端

## 配置

### settings.py 配置

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler',
    # ... 其他配置
}
```

## 日志记录

错误会自动记录到Django日志系统中，包含以下信息：

- 错误代码和消息
- 请求路径和方法
- 异常堆栈跟踪
- 自定义异常的详细信息

## 开发环境 vs 生产环境

- **开发环境**: 返回详细的错误信息和堆栈跟踪
- **生产环境**: 返回用户友好的错误消息，隐藏敏感信息

## 最佳实践

### 1. 选择合适的异常类型

根据错误场景选择最合适的异常类：

```python
# 文件相关错误
raise FileProcessingError("文件损坏", file_path="/path/to/file")

# 数据验证错误
raise ValidationError("邮箱格式错误", field="email", value="invalid@email")

# 业务逻辑错误
raise ConversionError("转换失败", step="token_mapping", task_id="123")
```

### 2. 提供详细的错误信息

```python
raise ConversionError(
    message="令牌映射失败",
    details={
        "token_key": "button.color",
        "layer_name": "Header/Button",
        "available_tokens": ["primary", "secondary"]
    }
)
```

### 3. 在合适的地方捕获异常

```python
def process_task(task_id):
    try:
        # 核心业务逻辑
        result = do_complex_operation()
        return result
    except ValueError as e:
        # 转换为业务异常
        raise ValidationError(str(e), field="input_data")
    except Exception as e:
        # 记录原始异常，抛出业务异常
        logger.error(f"Unexpected error in process_task: {e}")
        raise ConversionError(f"任务处理失败: {str(e)}", task_id=task_id)
```

### 4. 使用成功响应工具

```python
# 推荐方式
return standardize_success_response(
    data=serializer.data,
    message="任务创建成功"
)

# 不推荐（格式不统一）
return Response(serializer.data)
```

## 测试错误处理

### 1. 单元测试

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from .exceptions import TaskNotFoundError

class ErrorHandlingTest(APITestCase):
    def test_task_not_found_error(self):
        # 触发异常
        with self.assertRaises(TaskNotFoundError):
            get_task_by_id("nonexistent_id")

    def test_api_error_response(self):
        response = self.client.get('/api/tasks/nonexistent/')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'TASK_NOT_FOUND')
```

### 2. 集成测试

```python
def test_error_response_format(self):
    response = self.client.post('/api/tasks/', invalid_data)
    expected_structure = {
        'success': False,
        'error': {
            'code': str,
            'message': str,
            'details': dict
        },
        'timestamp': str,
        'path': str
    }
    # 验证响应结构
    self.assertEqual(response.data.keys(), expected_structure.keys())
```

## 常见问题

### Q: 什么时候使用自定义异常而不是标准异常？

A: 当需要：
- 返回特定的HTTP状态码
- 提供结构化的错误信息
- 进行特定的错误处理逻辑

### Q: 如何处理第三方库的异常？

A: 捕获第三方异常并包装为自定义异常：

```python
try:
    third_party_function()
except ThirdPartyError as e:
    raise ConversionError(f"第三方服务错误: {str(e)}", step="external_api")
```

### Q: 如何自定义错误消息？

A: 根据DEBUG设置返回不同详细程度的错误信息：

```python
if settings.DEBUG:
    message = f"详细错误信息: {str(e)}"
else:
    message = "操作失败，请稍后重试"
```

## 维护建议

1. **定期审查**: 检查错误日志，识别常见错误模式
2. **更新异常类**: 根据新的业务需求添加新的异常类
3. **监控告警**: 设置错误率告警，及时发现问题
4. **文档更新**: 保持错误代码文档与代码同步
