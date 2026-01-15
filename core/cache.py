"""
缓存模块 - 提供统一的缓存装饰器
"""
from functools import wraps
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def cache_result(timeout=600, key_prefix=None):
    """
    缓存装饰器，统一处理缓存逻辑

    Args:
        timeout: 缓存超时时间（秒），默认 600 秒（10 分钟）
        key_prefix: 缓存键前缀，用于区分不同的缓存

    Returns:
        装饰器函数

    Example:
        @cache_result(timeout=300, key_prefix="songs_list")
        def get_songs():
            # 业务逻辑
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_prefix:
                # 使用参数生成唯一键
                args_str = ','.join(str(arg) for arg in args)
                kwargs_str = ','.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{args_str}:{kwargs_str}"
            else:
                # 使用函数名和参数生成键
                args_str = ','.join(str(arg) for arg in args)
                kwargs_str = ','.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{args_str}:{kwargs_str}"

            # 尝试从缓存获取
            try:
                result = cache.get(cache_key)
                if result is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return result
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            # 执行函数
            result = func(*args, **kwargs)

            # 尝试设置缓存
            try:
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cache set: {cache_key} (timeout={timeout}s)")
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return result
        return wrapper
    return decorator


def clear_cache_pattern(pattern):
    """
    清除匹配模式的缓存

    Args:
        pattern: 缓存键模式

    Note:
        此功能需要使用支持模式匹配的缓存后端（如 Redis）
        对于 LocMemCache，此函数可能无法正常工作
    """
    try:
        # 获取所有缓存键
        if hasattr(cache, 'keys'):
            keys = cache.keys(f"*{pattern}*")
            if keys:
                cache.delete_many(keys)
                logger.info(f"Cleared {len(keys)} cache keys matching pattern: {pattern}")
        else:
            logger.warning("Current cache backend does not support pattern matching")
    except Exception as e:
        logger.warning(f"Failed to clear cache pattern: {e}")