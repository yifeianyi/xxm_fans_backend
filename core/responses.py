"""
统一响应格式模块 - 提供标准化的 API 响应
"""
from rest_framework.response import Response
from typing import Any, Optional, Dict, List


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200,
    status_code: int = 200
) -> Response:
    """
    成功响应

    Args:
        data: 响应数据，可以是任意类型（dict, list, str 等）
        message: 响应消息，默认 "操作成功"
        code: 业务响应码，默认 200
        status_code: HTTP 状态码，默认 200

    Returns:
        Response 对象

    Example:
        return success_response(data={"id": 1, "name": "test"})
        return success_response(data=[1, 2, 3], message="获取成功")
    """
    response_data = {
        'code': code,
        'message': message,
    }

    if data is not None:
        response_data['data'] = data

    return Response(response_data, status=status_code)


def error_response(
    message: str = "操作失败",
    code: int = 400,
    errors: Optional[Dict[str, List[str]]] = None,
    status_code: Optional[int] = None
) -> Response:
    """
    错误响应

    Args:
        message: 错误消息，默认 "操作失败"
        code: 错误码，默认 400
        errors: 详细错误信息，格式为 {"field": ["error1", "error2"]}
        status_code: HTTP 状态码，默认与 code 相同

    Returns:
        Response 对象

    Example:
        return error_response(message="参数错误", code=400)
        return error_response(
            message="验证失败",
            code=422,
            errors={"name": ["该字段不能为空"]}
        )
    """
    if status_code is None:
        status_code = code

    response_data = {
        'code': code,
        'message': message,
    }

    if errors:
        response_data['errors'] = errors

    return Response(response_data, status=status_code)


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "获取成功",
    code: int = 200
) -> Response:
    """
    分页响应

    Args:
        data: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页数量
        message: 响应消息，默认 "获取成功"
        code: 业务响应码，默认 200

    Returns:
        Response 对象

    Example:
        return paginated_response(
            data=[{"id": 1}, {"id": 2}],
            total=100,
            page=1,
            page_size=20
        )
    """
    return success_response(
        data={
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': data
        },
        message=message,
        code=code
    )


def created_response(data: Any = None, message: str = "创建成功") -> Response:
    """
    创建成功响应（HTTP 201）

    Args:
        data: 创建的数据
        message: 响应消息，默认 "创建成功"

    Returns:
        Response 对象
    """
    return success_response(data=data, message=message, code=201, status_code=201)


def updated_response(data: Any = None, message: str = "更新成功") -> Response:
    """
    更新成功响应

    Args:
        data: 更新后的数据
        message: 响应消息，默认 "更新成功"

    Returns:
        Response 对象
    """
    return success_response(data=data, message=message, code=200)


def deleted_response(message: str = "删除成功") -> Response:
    """
    删除成功响应

    Args:
        message: 响应消息，默认 "删除成功"

    Returns:
        Response 对象
    """
    return success_response(data=None, message=message, code=200)