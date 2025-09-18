# Converter app
# 注意：为了避免在Django启动时导入可能有问题的依赖（如openai），
# 我们不在__init__.py中预导入服务类，而是在需要时动态导入

from .exceptions import (
    ConverterException, FileProcessingError, ValidationError,
    ConversionError, UnsupportedFileFormatError, TaskNotFoundError
)

__all__ = [
    'ConverterException',
    'FileProcessingError',
    'ValidationError',
    'ConversionError',
    'UnsupportedFileFormatError',
    'TaskNotFoundError',
]
