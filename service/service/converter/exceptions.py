from typing import Dict, Any, Optional


class ConverterException(Exception):
    """转换服务异常基类"""
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class FileProcessingError(ConverterException):
    """文件处理异常"""
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(
            code="FILE_PROCESSING_ERROR",
            message=message,
            details={"file_path": file_path}
        )


class ValidationError(ConverterException):
    """数据验证异常"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details={"field": field, "value": value}
        )


class ConversionError(ConverterException):
    """转换过程异常"""
    def __init__(self, message: str, step: Optional[str] = None, task_id: Optional[str] = None):
        super().__init__(
            code="CONVERSION_ERROR",
            message=message,
            details={"step": step, "task_id": task_id}
        )


class ConfigurationError(ConverterException):
    """配置异常"""
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            code="CONFIGURATION_ERROR",
            message=message,
            details={"config_key": config_key}
        )


class TokenMappingError(ConverterException):
    """令牌映射异常"""
    def __init__(self, message: str, token_key: Optional[str] = None, layer_name: Optional[str] = None):
        super().__init__(
            code="TOKEN_MAPPING_ERROR",
            message=message,
            details={"token_key": token_key, "layer_name": layer_name}
        )


class UnsupportedFileFormatError(ConverterException):
    """不支持的文件格式异常"""
    def __init__(self, file_format: str, supported_formats: list):
        super().__init__(
            code="UNSUPPORTED_FILE_FORMAT",
            message=f"不支持的文件格式: {file_format}",
            details={
                "file_format": file_format,
                "supported_formats": supported_formats
            }
        )


class TaskNotFoundError(ConverterException):
    """任务未找到异常"""
    def __init__(self, task_id: str):
        super().__init__(
            code="TASK_NOT_FOUND",
            message=f"转换任务不存在: {task_id}",
            details={"task_id": task_id}
        )


class TaskAlreadyRunningError(ConverterException):
    """任务已在运行异常"""
    def __init__(self, task_id: str):
        super().__init__(
            code="TASK_ALREADY_RUNNING",
            message=f"转换任务已在运行中: {task_id}",
            details={"task_id": task_id}
        )


class LLMServiceError(ConverterException):
    """LLM服务异常"""
    def __init__(self, message: str, service_name: str = "LLM"):
        super().__init__(
            code="LLM_SERVICE_ERROR",
            message=message,
            details={"service_name": service_name}
        )
