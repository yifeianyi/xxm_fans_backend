"""
自定义异常模块 - 提供统一的异常类
"""
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    """基础 API 异常"""

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__(detail=detail, code=code)


class SongNotFoundException(BaseAPIException):
    """歌曲未找到异常"""
    status_code = 404
    default_detail = "歌曲未找到"
    default_code = "song_not_found"


class InvalidParameterException(BaseAPIException):
    """无效参数异常"""
    status_code = 400
    default_detail = "参数无效"
    default_code = "invalid_parameter"


class ArtistNotFoundException(BaseAPIException):
    """歌手未找到异常"""
    status_code = 404
    default_detail = "歌手未找到"
    default_code = "artist_not_found"


class CollectionNotFoundException(BaseAPIException):
    """合集未找到异常"""
    status_code = 404
    default_detail = "合集未找到"
    default_code = "collection_not_found"


class WorkNotFoundException(BaseAPIException):
    """作品未找到异常"""
    status_code = 404
    default_detail = "作品未找到"
    default_code = "work_not_found"


class PermissionDeniedException(BaseAPIException):
    """权限拒绝异常"""
    status_code = 403
    default_detail = "权限不足"
    default_code = "permission_denied"


class ValidationException(BaseAPIException):
    """验证失败异常"""
    status_code = 422
    default_detail = "数据验证失败"
    default_code = "validation_error"


class CacheException(BaseAPIException):
    """缓存异常"""
    status_code = 500
    default_detail = "缓存操作失败"
    default_code = "cache_error"


class DatabaseException(BaseAPIException):
    """数据库异常"""
    status_code = 500
    default_detail = "数据库操作失败"
    default_code = "database_error"