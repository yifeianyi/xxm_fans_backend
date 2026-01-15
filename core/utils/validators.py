"""
验证器模块 - 提供常用的数据验证函数
"""
import re
import os
from typing import Optional, List


def validate_url(url: str) -> bool:
    """
    验证 URL 格式

    Args:
        url: 待验证的 URL

    Returns:
        验证通过返回 True，否则返回 False

    Example:
        if validate_url("https://example.com"):
            print("URL 格式正确")
    """
    if not url or not isinstance(url, str):
        return False

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    return url_pattern.match(url) is not None


def validate_image_url(url: str) -> bool:
    """
    验证图片 URL 格式

    Args:
        url: 待验证的图片 URL

    Returns:
        验证通过返回 True，否则返回 False

    Example:
        if validate_image_url("https://example.com/image.jpg"):
            print("图片 URL 格式正确")
    """
    if not validate_url(url):
        return False

    # 检查文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    url_lower = url.lower()

    for ext in image_extensions:
        if url_lower.endswith(ext):
            return True

    return False


def validate_email(email: str) -> bool:
    """
    验证邮箱格式

    Args:
        email: 待验证的邮箱地址

    Returns:
        验证通过返回 True，否则返回 False

    Example:
        if validate_email("user@example.com"):
            print("邮箱格式正确")
    """
    if not email or not isinstance(email, str):
        return False

    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    return email_pattern.match(email) is not None


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆）

    Args:
        phone: 待验证的手机号

    Returns:
        验证通过返回 True，否则返回 False

    Example:
        if validate_phone("13800138000"):
            print("手机号格式正确")
    """
    if not phone or not isinstance(phone, str):
        return False

    # 中国大陆手机号：1开头的11位数字
    phone_pattern = re.compile(r'^1[3-9]\d{9}$')

    return phone_pattern.match(phone) is not None


def validate_positive_integer(value: int) -> bool:
    """
    验证正整数

    Args:
        value: 待验证的值

    Returns:
        验证通过返回 True，否则返回 False
    """
    return isinstance(value, int) and value > 0


def validate_string_length(
    value: str,
    min_length: int = 0,
    max_length: int = 1000
) -> bool:
    """
    验证字符串长度

    Args:
        value: 待验证的字符串
        min_length: 最小长度，默认 0
        max_length: 最大长度，默认 1000

    Returns:
        验证通过返回 True，否则返回 False
    """
    if not isinstance(value, str):
        return False

    return min_length <= len(value) <= max_length


def validate_choice(value: str, choices: List[str]) -> bool:
    """
    验证值是否在可选列表中

    Args:
        value: 待验证的值
        choices: 可选值列表

    Returns:
        验证通过返回 True，否则返回 False

    Example:
        if validate_choice("male", ["male", "female"]):
            print("值在可选列表中")
    """
    return value in choices


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名

    Example:
        safe_name = sanitize_filename("file/name?.txt")
        # 返回: "filename.txt"
    """
    # 移除不安全字符
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')

    # 移除前后空格
    filename = filename.strip()

    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    return filename
