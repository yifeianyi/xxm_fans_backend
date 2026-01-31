"""
缓存模块 - 提供统一的缓存装饰器和缓存清理功能
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
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
        pattern: 缓存键模式（支持通配符 *）

    Note:
        此功能需要使用支持模式匹配的缓存后端（如 Redis）
        对于 LocMemCache，此函数可能无法正常工作

    Example:
        clear_cache_pattern('song_detail')  # 清除所有 song_detail:* 缓存
    """
    try:
        # 检查缓存后端是否支持模式匹配
        cache_backend = settings.CACHES.get('default', {}).get('BACKEND', '')

        if 'redis' in cache_backend.lower():
            # Redis 支持模式匹配
            try:
                # 获取 RedisCacheClient
                cache_client = cache._cache
                
                # 使用 get_client 方法获取 Redis 客户端
                redis_client = cache_client.get_client()
                
                # 构建完整的键模式（包含前缀和版本号）
                key_prefix = settings.CACHES.get('default', {}).get('KEY_PREFIX', '')
                full_pattern = f"{key_prefix}:*{pattern}*"
                
                # 使用 Redis 的 keys 方法
                if hasattr(redis_client, 'keys'):
                    keys = redis_client.keys(full_pattern)
                    if keys:
                        # 删除匹配的键
                        redis_client.delete(*keys)
                        logger.info(f"Cleared {len(keys)} cache keys matching pattern: *{pattern}*")
                    else:
                        logger.debug(f"No cache keys found matching pattern: *{pattern}*")
                else:
                    logger.warning("Redis client does not support keys() method")
            except Exception as e:
                logger.warning(f"Could not access Redis client: {e}")
                logger.warning("Pattern clearing not fully supported, falling back to ignoring")
        elif 'locmem' in cache_backend.lower():
            # LocMemCache 不支持模式匹配，需要遍历所有键
            if hasattr(cache, '_cache'):
                keys_to_delete = [key for key in cache._cache.keys() if pattern in key]
                if keys_to_delete:
                    for key in keys_to_delete:
                        cache.delete(key)
                    logger.info(f"Cleared {len(keys_to_delete)} cache keys matching pattern: *{pattern}*")
        else:
            logger.warning("Current cache backend does not support pattern matching")
    except Exception as e:
        logger.warning(f"Failed to clear cache pattern: {e}")


def clear_all_cache():
    """
    清除所有缓存
    """
    try:
        cache.clear()
        logger.info("Cleared all cache")
    except Exception as e:
        logger.warning(f"Failed to clear all cache: {e}")