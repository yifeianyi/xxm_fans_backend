"""
自定义异常处理中间件
"""
from rest_framework.views import exception_handler
from rest_framework import status
from core.responses import error_response
from core.exceptions import BaseAPIException
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器

    Args:
        exc: 异常对象
        context: 上下文信息

    Returns:
        Response 对象
    """
    # 调用 DRF 默认的异常处理器
    response = exception_handler(exc, context)

    # 如果是自定义异常，使用统一的响应格式
    if isinstance(exc, BaseAPIException):
        return error_response(
            message=str(exc.detail),
            code=exc.status_code,
            status_code=exc.status_code
        )

    # 如果 DRF 默认处理器返回了响应，转换格式
    if response is not None:
        # 提取错误信息
        message = response.data.get('detail', str(response.data))

        # 如果是验证错误，提取详细错误信息
        if isinstance(response.data, dict) and 'detail' not in response.data:
            errors = response.data
            message = "数据验证失败"
        else:
            errors = None

        return error_response(
            message=message,
            code=response.status_code,
            errors=errors,
            status_code=response.status_code
        )

    # 处理未捕获的异常
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return error_response(
        message="服务器内部错误",
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )