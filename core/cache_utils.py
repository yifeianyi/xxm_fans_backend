"""
缓存工具模块 - 提供统一的缓存装饰器和工具函数
"""
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class CacheKeyBuilder:
    """缓存键构建器"""
    
    @staticmethod
    def build_key(prefix: str, *args, **kwargs) -> str:
        """
        构建缓存键
        
        Args:
            prefix: 键前缀
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            str: 缓存键
        """
        key_parts = [prefix]
        
        # 添加位置参数
        if args:
            args_str = ':'.join(str(arg) for arg in args)
            key_parts.append(args_str)
        
        # 添加关键字参数（排序后）
        if kwargs:
            sorted_kwargs = json.dumps(kwargs, sort_keys=True, default=str)
            kwargs_hash = hashlib.md5(sorted_kwargs.encode()).hexdigest()[:8]
            key_parts.append(kwargs_hash)
        
        return ':'.join(key_parts)
    
    @staticmethod
    def build_model_key(model_name: str, obj_id: Any, field: Optional[str] = None) -> str:
        """
        构建模型对象缓存键
        
        Args:
            model_name: 模型名称
            obj_id: 对象ID
            field: 特定字段（可选）
            
        Returns:
            str: 缓存键
        """
        key = f"model:{model_name}:{obj_id}"
        if field:
            key = f"{key}:{field}"
        return key
    
    @staticmethod
    def build_list_key(model_name: str, **filters) -> str:
        """
        构建列表查询缓存键
        
        Args:
            model_name: 模型名称
            **filters: 过滤条件
            
        Returns:
            str: 缓存键
        """
        if filters:
            sorted_filters = json.dumps(filters, sort_keys=True, default=str)
            filters_hash = hashlib.md5(sorted_filters.encode()).hexdigest()[:12]
            return f"model:{model_name}:list:{filters_hash}"
        return f"model:{model_name}:list:all"


class cached:
    """
    缓存装饰器
    
    使用示例:
        @cached(timeout=300, key_prefix='song')
        def get_song_detail(song_id):
            return Song.objects.get(id=song_id)
            
        @cached(timeout=600, key_prefix='song_list')
        def get_song_list(page=1, limit=20):
            return Song.objects.all()[page*limit:(page+1)*limit]
    """
    
    def __init__(
        self,
        timeout: int = 300,
        key_prefix: str = '',
        cache_none: bool = False,
        unless: Optional[Callable] = None
    ):
        """
        初始化缓存装饰器
        
        Args:
            timeout: 缓存超时时间（秒）
            key_prefix: 缓存键前缀
            cache_none: 是否缓存 None 值
            unless: 条件函数，返回 True 时不缓存
        """
        self.timeout = timeout
        self.key_prefix = key_prefix
        self.cache_none = cache_none
        self.unless = unless
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 检查 unless 条件
            if self.unless and self.unless(*args, **kwargs):
                return func(*args, **kwargs)
            
            # 构建缓存键
            cache_key = CacheKeyBuilder.build_key(
                self.key_prefix or func.__name__,
                *args[1:],  # 排除 self
                **kwargs
            )
            
            # 尝试从缓存获取
            try:
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            if result is not None or self.cache_none:
                try:
                    cache.set(cache_key, result, self.timeout)
                    logger.debug(f"Cache set: {cache_key}")
                except Exception as e:
                    logger.warning(f"Cache set failed: {e}")
            
            return result
        
        # 添加清除缓存的方法
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(
            CacheKeyBuilder.build_key(
                self.key_prefix or func.__name__,
                *args,
                **kwargs
            )
        )
        
        wrapper.invalidate_all = lambda: cache.delete_pattern(
            f"{self.key_prefix or func.__name__}:*"
        ) if hasattr(cache, 'delete_pattern') else None
        
        return wrapper


class ModelCacheManager:
    """模型缓存管理器"""
    
    DEFAULT_TIMEOUT = 300
    
    @classmethod
    def get(cls, model_name: str, obj_id: Any, getter_func: Callable, timeout: int = None):
        """
        获取缓存的模型对象
        
        Args:
            model_name: 模型名称
            obj_id: 对象ID
            getter_func: 获取对象的函数
            timeout: 缓存超时时间
            
        Returns:
            模型对象
        """
        cache_key = CacheKeyBuilder.build_model_key(model_name, obj_id)
        
        try:
            obj = cache.get(cache_key)
            if obj is not None:
                logger.debug(f"Model cache hit: {cache_key}")
                return obj
        except Exception as e:
            logger.warning(f"Model cache get failed: {e}")
        
        # 从数据库获取
        obj = getter_func()
        
        # 缓存结果
        if obj is not None:
            try:
                cache.set(cache_key, obj, timeout or cls.DEFAULT_TIMEOUT)
                logger.debug(f"Model cache set: {cache_key}")
            except Exception as e:
                logger.warning(f"Model cache set failed: {e}")
        
        return obj
    
    @classmethod
    def set(cls, model_name: str, obj_id: Any, obj: Any, timeout: int = None):
        """设置模型缓存"""
        cache_key = CacheKeyBuilder.build_model_key(model_name, obj_id)
        try:
            cache.set(cache_key, obj, timeout or cls.DEFAULT_TIMEOUT)
        except Exception as e:
            logger.warning(f"Model cache set failed: {e}")
    
    @classmethod
    def delete(cls, model_name: str, obj_id: Any):
        """删除模型缓存"""
        cache_key = CacheKeyBuilder.build_model_key(model_name, obj_id)
        try:
            cache.delete(cache_key)
        except Exception as e:
            logger.warning(f"Model cache delete failed: {e}")
    
    @classmethod
    def invalidate_list(cls, model_name: str):
        """使列表缓存失效"""
        pattern = f"model:{model_name}:list:*"
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
            else:
                # 回退：使用迭代删除
                keys = cache.keys(pattern) if hasattr(cache, 'keys') else []
                for key in keys:
                    cache.delete(key)
        except Exception as e:
            logger.warning(f"Model cache invalidate failed: {e}")


# 预定义的缓存超时时间
class CacheTimeout:
    """缓存超时时间常量"""
    SHORT = 60          # 1分钟
    DEFAULT = 300       # 5分钟
    MEDIUM = 600        # 10分钟
    LONG = 1800         # 30分钟
    HOUR = 3600         # 1小时
    DAY = 86400         # 1天
    WEEK = 604800       # 1周


# 常用缓存键前缀
class CacheKeys:
    """缓存键前缀常量"""
    SONG = 'song'
    SONG_LIST = 'song:list'
    SONG_RECORD = 'song:record'
    STYLE = 'style'
    TAG = 'tag'
    TOP_SONGS = 'song:top'
    RANDOM_SONG = 'song:random'
    COLLECTION = 'collection'
    WORK = 'work'
    GALLERY = 'gallery'
    LIVESTREAM = 'livestream'
    RECOMMENDATION = 'recommendation'
    SETTINGS = 'settings'
