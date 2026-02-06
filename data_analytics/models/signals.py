"""
信号处理器 - 自动精细化清理缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .work_static import WorkStatic
from .work_metrics_hour import WorkMetricsHour
from .crawl_session import CrawlSession
from .work_metrics_spider import WorkMetricsSpider
from .crawl_session_spider import CrawlSessionSpider
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


# ========== 新爬虫模型信号处理器 ==========

@receiver(post_save, sender=WorkMetricsSpider)
def clear_cache_on_work_metrics_spider_save(sender, instance, created, **kwargs):
    """
    当爬虫作品指标数据被创建或更新时，精细化清理缓存
    """
    # 清理该作品的爬虫指标缓存
    clear_cache_pattern(f'work_metrics_spider:{instance.work_id}')


@receiver(post_delete, sender=WorkMetricsSpider)
def clear_cache_on_work_metrics_spider_delete(sender, instance, **kwargs):
    """
    当爬虫作品指标数据被删除时，精细化清理缓存
    """
    # 清理该作品的爬虫指标缓存
    clear_cache_pattern(f'work_metrics_spider:{instance.work_id}')


@receiver(post_save, sender=CrawlSessionSpider)
def clear_cache_on_crawl_session_spider_save(sender, instance, created, **kwargs):
    """
    当爬虫会话被创建或更新时，精细化清理缓存
    """
    # 清理该爬虫会话的详情缓存
    clear_cache_pattern(f'crawl_session_spider:{instance.session_id}')


@receiver(post_delete, sender=CrawlSessionSpider)
def clear_cache_on_crawl_session_spider_delete(sender, instance, **kwargs):
    """
    当爬虫会话被删除时，精细化清理缓存
    """
    # 清理该爬虫会话的详情缓存
    clear_cache_pattern(f'crawl_session_spider:{instance.session_id}')


# ========== 自动导出 views.json 信号处理器 ==========

import logging
import os
import sys
import time
from threading import Thread

logger = logging.getLogger(__name__)


def _get_spider_tools_path() -> str:
    """获取 spider 工具路径"""
    current_file = os.path.abspath(__file__)
    # 上溯到 repo/xxm_fans_backend 目录
    for _ in range(3):
        current_file = os.path.dirname(current_file)
    return os.path.join(current_file, 'tools', 'spider')


def _delayed_export_views():
    """延迟执行导出任务"""
    time.sleep(5)  # 延迟5秒执行，合并短时间内的多次变更
    try:
        spider_tools = _get_spider_tools_path()
        if spider_tools not in sys.path:
            sys.path.insert(0, spider_tools)

        from export_views import ViewsExporter

        exporter = ViewsExporter()
        if exporter.export():
            logger.info("自动导出 views.json 成功")
        else:
            logger.error("自动导出 views.json 失败")

    except Exception as e:
        logger.error(f"自动导出 views.json 失败: {e}")


@receiver(post_save, sender=WorkStatic)
def auto_export_views_on_save(sender, instance, created, **kwargs):
    """
    当 WorkStatic 数据创建或更新时，自动触发 views.json 导出
    使用延迟和防抖机制，避免频繁触发
    """
    current_time = time.time()

    # 防抖: 10秒内只触发一次
    if not hasattr(auto_export_views_on_save, '_last_trigger'):
        auto_export_views_on_save._last_trigger = 0

    if current_time - auto_export_views_on_save._last_trigger < 10:
        return

    auto_export_views_on_save._last_trigger = current_time

    # 在后台线程中执行，避免阻塞主线程
    thread = Thread(target=_delayed_export_views, daemon=True)
    thread.start()
    logger.debug(f"WorkStatic {instance.work_id} 变更，已触发自动导出任务")


@receiver(post_delete, sender=WorkStatic)
def auto_export_views_on_delete(sender, instance, **kwargs):
    """
    当 WorkStatic 数据删除时，自动触发 views.json 导出
    """
    current_time = time.time()

    # 防抖: 10秒内只触发一次
    if not hasattr(auto_export_views_on_delete, '_last_trigger'):
        auto_export_views_on_delete._last_trigger = 0

    if current_time - auto_export_views_on_delete._last_trigger < 10:
        return

    auto_export_views_on_delete._last_trigger = current_time

    # 在后台线程中执行
    thread = Thread(target=_delayed_export_views, daemon=True)
    thread.start()
    logger.debug(f"WorkStatic {instance.work_id} 删除，已触发自动导出任务")