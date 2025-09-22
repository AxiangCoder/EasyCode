import logging
from datetime import datetime
from typing import Dict, Any, Optional

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler

from converter.exceptions import ConverterException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    自定义异常处理器
    统一处理所有异常，返回标准化的错误响应格式

    Args:
        exc: 异常实例
        context: 包含请求和视图信息的字典

    Returns:
        Response对象或None（让DRF处理）
    """
    # 获取请求信息
    request = context.get('request')

    # 首先尝试使用DRF的默认异常处理器
    response = drf_exception_handler(exc, context)

    if response is not None:
        # DRF已经处理了异常，标准化响应格式
        return _standardize_drf_response(response, exc)

    # 处理自定义异常
    if isinstance(exc, ConverterException):
        return _handle_converter_exception(exc, request)

    # 处理其他未处理的异常
    return _handle_unexpected_exception(exc, request)


def _standardize_drf_response(response: Response, exc: Exception) -> Response:
    """
    标准化DRF默认异常响应格式

    Args:
        response: DRF原始响应
        exc: 异常实例

    Returns:
        标准化后的响应
    """
    # 保持DRF的HTTP状态码，但标准化响应体格式
    standardized_data = {
        "success": False,
        "error": {
            "code": _get_error_code_from_status(response.status_code),
            "message": _extract_error_message(response.data),
            "details": response.data if isinstance(response.data, dict) else {}
        },
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "path": getattr(response, '_request', {}).get('path', '') if hasattr(response, '_request') and getattr(response, '_request') else ''
    }

    return Response(standardized_data, status=response.status_code)


def _handle_converter_exception(exc: ConverterException, request) -> Response:
    """
    处理自定义ConverterException

    Args:
        exc: ConverterException实例
        request: 请求对象

    Returns:
        标准化的错误响应
    """
    # 根据异常类型确定HTTP状态码
    status_code = _get_status_code_for_exception(exc)

    # 记录错误日志
    logger.error(
        f"ConverterException: {exc.code} - {exc.message}",
        extra={
            'exception_code': exc.code,
            'exception_details': exc.details,
            'request_path': request.path if request else None,
            'request_method': request.method if request else None,
        }
    )

    # 返回标准化的错误响应
    return Response({
        "success": False,
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        },
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "path": request.path if request else None
    }, status=status_code)


def _handle_unexpected_exception(exc: Exception, request) -> Response:
    """
    处理意外异常

    Args:
        exc: 异常实例
        request: 请求对象

    Returns:
        错误响应
    """
    # 记录详细的错误日志
    logger.error(
        f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={
            'request_path': request.path if request else None,
            'request_method': request.method if request else None,
        }
    )

    # 在开发环境中返回详细错误信息
    from django.conf import settings
    is_debug = getattr(settings, 'DEBUG', False)

    error_details = {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc)
    } if is_debug else {}

    return Response({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误，请稍后重试" if not is_debug else str(exc),
            "details": error_details
        },
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "path": request.path if request else None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_error_code_from_status(status_code: int) -> str:
    """根据HTTP状态码返回错误代码"""
    status_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }
    return status_code_map.get(status_code, "UNKNOWN_ERROR")


def _extract_error_message(data: Any) -> str:
    """从DRF响应数据中提取错误消息"""
    if isinstance(data, dict):
        # 如果是字典，尝试提取detail字段
        if 'detail' in data:
            return str(data['detail'])
        # 如果有其他字段，尝试提取第一个
        for key, value in data.items():
            if isinstance(value, list) and value:
                return str(value[0])
            return str(value)
    elif isinstance(data, list):
        # 如果是列表，提取第一个错误
        return str(data[0]) if data else "Validation error"
    else:
        return str(data)


def _get_status_code_for_exception(exc: ConverterException) -> int:
    """根据异常类型确定HTTP状态码"""
    exception_status_map = {
        'VALIDATION_ERROR': status.HTTP_400_BAD_REQUEST,
        'FILE_PROCESSING_ERROR': status.HTTP_400_BAD_REQUEST,
        'CONVERSION_ERROR': status.HTTP_422_UNPROCESSABLE_ENTITY,
        'CONFIGURATION_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'TOKEN_MAPPING_ERROR': status.HTTP_422_UNPROCESSABLE_ENTITY,
        'UNSUPPORTED_FILE_FORMAT': status.HTTP_400_BAD_REQUEST,
        'TASK_NOT_FOUND': status.HTTP_404_NOT_FOUND,
        'TASK_ALREADY_RUNNING': status.HTTP_409_CONFLICT,
        'LLM_SERVICE_ERROR': status.HTTP_503_SERVICE_UNAVAILABLE,
    }

    return exception_status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)


def standardize_success_response(data: Any = None, message: str = "", status_code: int = 200) -> Response:
    """
    标准化成功响应格式

    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP状态码

    Returns:
        标准化的Response对象
    """
    response_data = {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

    return Response(response_data, status=status_code)


def get_paginated_response(queryset, serializer_class, request, context=None):
    """
    获取分页响应，使用标准格式

    Args:
        queryset: 查询集
        serializer_class: 序列化器类
        request: 请求对象
        context: 序列化器上下文

    Returns:
        标准化的分页响应
    """
    from rest_framework.pagination import PageNumberPagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # 使用DRF的分页器
    paginator = PageNumberPagination()
    paginator.page_size = request.query_params.get('page_size', 20)
    paginator.max_page_size = 100

    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer_context = context or {'request': request}
        serializer = serializer_class(page, many=True, context=serializer_context)
        return paginator.get_paginated_response(serializer.data)

    # 如果没有分页，返回标准格式
    serializer_context = context or {'request': request}
    serializer = serializer_class(queryset, many=True, context=serializer_context)

    return Response({
        "success": True,
        "data": serializer.data,
        "pagination": {
            "count": len(serializer.data),
            "total_pages": 1,
            "current_page": 1,
            "has_next": False,
            "has_previous": False
        },
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    })
