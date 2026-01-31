"""
直播应用自定义异常类
"""


class LivestreamException(Exception):
    """直播基础异常类"""
    pass


class ParameterValidationError(LivestreamException):
    """参数验证失败异常"""
    def __init__(self, message: str, field_name: str = None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)


class DataNotFoundError(LivestreamException):
    """数据不存在异常"""
    def __init__(self, message: str, identifier: str = None):
        self.message = message
        self.identifier = identifier
        super().__init__(self.message)


class FileReadError(LivestreamException):
    """文件读取异常"""
    def __init__(self, message: str, file_path: str = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.message)


class PathValidationError(LivestreamException):
    """路径验证失败异常"""
    def __init__(self, message: str, requested_path: str = None):
        self.message = message
        self.requested_path = requested_path
        super().__init__(self.message)