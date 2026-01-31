"""
信号处理器 - 自动精细化清理缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .settings import Recommendation, SiteSettings, Milestone
from core.cache import clear_cache_pattern


@receiver(post_save, sender=Recommendation)
def clear_cache_on_recommendation_save(sender, instance, created, **kwargs):
    """
    当推荐语被创建或更新时，精细化清理缓存
    """
    # 清理推荐语缓存
    clear_cache_pattern('get_recommendation')


@receiver(post_delete, sender=Recommendation)
def clear_cache_on_recommendation_delete(sender, instance, **kwargs):
    """
    当推荐语被删除时，精细化清理缓存
    """
    # 清理推荐语缓存
    clear_cache_pattern('get_recommendation')


@receiver(post_save, sender=SiteSettings)
def clear_cache_on_settings_save(sender, instance, created, **kwargs):
    """
    当网站设置被创建或更新时，精细化清理缓存
    """
    # 清理网站设置缓存
    clear_cache_pattern('get_site_settings')


@receiver(post_delete, sender=SiteSettings)
def clear_cache_on_settings_delete(sender, instance, **kwargs):
    """
    当网站设置被删除时，精细化清理缓存
    """
    # 清理网站设置缓存
    clear_cache_pattern('get_site_settings')


@receiver(post_save, sender=Milestone)
def clear_cache_on_milestone_save(sender, instance, created, **kwargs):
    """
    当里程碑被创建或更新时，精细化清理缓存
    """
    # 清理里程碑列表缓存
    clear_cache_pattern('get_milestones')
    # 清理该里程碑的详情缓存
    clear_cache_pattern(f'get_milestone:{instance.id}')


@receiver(post_delete, sender=Milestone)
def clear_cache_on_milestone_delete(sender, instance, **kwargs):
    """
    当里程碑被删除时，精细化清理缓存
    """
    # 清理里程碑列表缓存
    clear_cache_pattern('get_milestones')
    # 清理该里程碑的详情缓存
    clear_cache_pattern(f'get_milestone:{instance.id}')