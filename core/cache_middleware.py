"""
缓存中间件 - 提供缓存相关的 HTTP 响应头和监控
"""
import time
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class CacheStats:
    """缓存统计"""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_time = 0
    
    def hit(self, duration: float):
        self.hits += 1
        self.total_time += duration
    
    def miss(self, duration: float):
        self.misses += 1
        self.total_time += duration
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    
    @property
    def avg_time(self) -> float:
        total = self.hits + self.misses
        return self.total_time / total if total > 0 else 0


class CacheHeaderMiddleware:
    """
    缓存响应头中间件
    
    添加以下响应头：
    - X-Cache: HIT/MISS
    - X-Cache-Key: 缓存键
    - X-Response-Time: 响应时间
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.stats = CacheStats()
    
    def __call__(self, request: HttpRequest):
        start_time = time.time()
        
        # 标记请求开始时间
        request._cache_start_time = start_time
        
        response = self.get_response(request)
        
        # 计算响应时间
        duration = time.time() - start_time
        
        # 添加响应头
        response['X-Response-Time'] = f'{duration:.3f}s'
        
        # 如果请求被缓存，添加缓存头
        if hasattr(request, '_cache_hit'):
            response['X-Cache'] = 'HIT' if request._cache_hit else 'MISS'
        
        return response


class CacheControlMiddleware:
    """
    缓存控制中间件
    
    根据 URL 模式自动设置 Cache-Control 响应头
    """
    
    # 缓存配置：URL 模式 -> (max_age, public/private)
    CACHE_PATTERNS = {
        r'^/api/songs/$': (300, True),           # 歌曲列表缓存 5 分钟
        r'^/api/songs/\d+/records/$': (300, True),  # 演唱记录缓存 5 分钟
        r'^/api/top_songs/$': (600, True),       # 排行榜缓存 10 分钟
        r'^/api/styles/$': (3600, True),         # 曲风列表缓存 1 小时
        r'^/api/tags/$': (3600, True),           # 标签列表缓存 1 小时
        r'^/api/fansDIY/collections/$': (300, True),  # 合集列表缓存 5 分钟
        r'^/api/gallery/$': (300, True),         # 图集列表缓存 5 分钟
        r'^/api/site-settings/$': (60, True),    # 网站设置缓存 1 分钟
        r'^/api/random-song/$': (0, False),      # 随机歌曲不缓存
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        
        # 只处理成功的 GET 请求
        if request.method != 'GET' or response.status_code != 200:
            return response
        
        import re
        path = request.path_info
        
        # 匹配 URL 模式
        for pattern, (max_age, is_public) in self.CACHE_PATTERNS.items():
            if re.match(pattern, path):
                if max_age > 0:
                    visibility = 'public' if is_public else 'private'
                    response['Cache-Control'] = f'{visibility}, max-age={max_age}'
                else:
                    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                break
        
        return response


class CacheMonitorMiddleware:
    """
    缓存监控中间件
    
    监控缓存命中率和性能指标
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.stats = CacheStats()
    
    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        
        # 定期记录统计信息（每 100 个请求）
        total = self.stats.hits + self.stats.misses
        if total > 0 and total % 100 == 0:
            logger.info(
                f"Cache stats - Hit rate: {self.stats.hit_rate:.2%}, "
                f"Hits: {self.stats.hits}, Misses: {self.stats.misses}, "
                f"Avg time: {self.stats.avg_time:.3f}s"
            )
        
        return response


def get_cache_key(request: HttpRequest, prefix: str = '') -> str:
    """
    根据请求生成缓存键
    
    Args:
        request: HTTP 请求
        prefix: 键前缀
        
    Returns:
        str: 缓存键
    """
    key = f"{prefix}:{request.path}"
    
    # 添加查询参数
    if request.META.get('QUERY_STRING'):
        key = f"{key}?{request.META['QUERY_STRING']}"
    
    # 如果用户已认证，添加用户 ID
    if request.user.is_authenticated:
        key = f"{key}:user={request.user.id}"
    
    return key


def cache_page(timeout: int, key_prefix: str = ''):
    """
    页面缓存装饰器（用于视图函数）
    
    Args:
        timeout: 缓存超时时间
        key_prefix: 键前缀
        
    使用示例:
        @cache_page(300, 'song_list')
        def song_list_view(request):
            ...
    """
    def decorator(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            # 只缓存 GET 请求
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            
            cache_key = get_cache_key(request, key_prefix or view_func.__name__)
            
            # 尝试从缓存获取
            try:
                cached_response = cache.get(cache_key)
                if cached_response is not None:
                    request._cache_hit = True
                    return cached_response
            except Exception as e:
                logger.warning(f"Page cache get failed: {e}")
            
            # 执行视图
            response = view_func(request, *args, **kwargs)
            
            # 缓存响应
            if response.status_code == 200:
                try:
                    cache.set(cache_key, response, timeout)
                    request._cache_hit = False
                except Exception as e:
                    logger.warning(f"Page cache set failed: {e}")
            
            return response
        
        return wrapper
    return decorator
