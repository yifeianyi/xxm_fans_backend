"""
信号处理器 - 自动精细化清理缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .work_static import WorkStatic
from .work_metrics_hour import WorkMetricsHour
from .crawl_session import CrawlSession
from core.cache import clear_cache_pattern


@receiver(post_save, sender=WorkStatic)
def clear_cache_on_work_static_save(sender, instance, created, **kwargs):
    """
    当作品统计数据被创建或更新时，精细化清理缓存
    """
    # 清理该作品的详情缓存
    clear_cache_pattern(f'work_detail:{instance.work_id}')


@receiver(post_delete, sender=WorkStatic)
def clear_cache_on_work_static_delete(sender, instance, **kwargs):
    """
    当作品统计数据被删除时，精细化清理缓存
    """
    # 清理该作品的详情缓存
    clear_cache_pattern(f'work_detail:{instance.work_id}')


@receiver(post_save, sender=WorkMetricsHour)
def clear_cache_on_work_metrics_save(sender, instance, created, **kwargs):
    """
    当作品指标数据被创建或更新时，精细化清理缓存
    """
    # 清理该作品的指标汇总缓存
    clear_cache_pattern(f'work_metrics_summary:{instance.work_id}')


@receiver(post_delete, sender=WorkMetricsHour)
def clear_cache_on_work_metrics_delete(sender, instance, **kwargs):
    """
    当作品指标数据被删除时，精细化清理缓存
    """
    # 清理该作品的指标汇总缓存
    clear_cache_pattern(f'work_metrics_summary:{instance.work_id}')


@receiver(post_save, sender=CrawlSession)
def clear_cache_on_crawl_session_save(sender, instance, created, **kwargs):
    """
    当爬取会话被创建或更新时，精细化清理缓存
    """
    # 清理该爬取会话的详情缓存
    clear_cache_pattern(f'crawl_session_detail:{instance.id}')


@receiver(post_delete, sender=CrawlSession)
def clear_cache_on_crawl_session_delete(sender, instance, **kwargs):
    """
    当爬取会话被删除时，精细化清理缓存
    """
    # 清理该爬取会话的详情缓存
    clear_cache_pattern(f'crawl_session_detail:{instance.id}')