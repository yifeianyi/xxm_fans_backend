"""
信号处理器 - 自动精细化清理缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .collection import Collection
from .work import Work
from core.cache import clear_cache_pattern


@receiver(post_save, sender=Collection)
def clear_cache_on_collection_save(sender, instance, created, **kwargs):
    """
    当合集被创建或更新时，精细化清理缓存
    """
    # 清理该合集的详情缓存
    clear_cache_pattern(f'collection_detail:{instance.id}')
    # 清理合集列表缓存
    clear_cache_pattern('get_collections')
    # 清理该合集下的作品列表缓存
    clear_cache_pattern(f'get_works:collection_id={instance.id}')


@receiver(post_delete, sender=Collection)
def clear_cache_on_collection_delete(sender, instance, **kwargs):
    """
    当合集被删除时，精细化清理缓存
    """
    # 清理该合集的详情缓存
    clear_cache_pattern(f'collection_detail:{instance.id}')
    # 清理合集列表缓存
    clear_cache_pattern('get_collections')
    # 清理该合集下的所有作品列表缓存
    clear_cache_pattern(f'get_works:collection_id={instance.id}')


@receiver(post_save, sender=Work)
def clear_cache_on_work_save(sender, instance, created, **kwargs):
    """
    当作品被创建或更新时，精细化清理缓存
    """
    # 清理该作品的详情缓存
    clear_cache_pattern(f'get_work_by_id:{instance.id}')
    # 清理合集列表缓存（因为作品数量可能变化）
    clear_cache_pattern('get_collections')
    # 清理该合集下的作品列表缓存
    clear_cache_pattern(f'get_works:collection_id={instance.collection.id}')
    # 清理作品列表缓存（所有作品）
    clear_cache_pattern('get_works:')


@receiver(post_delete, sender=Work)
def clear_cache_on_work_delete(sender, instance, **kwargs):
    """
    当作品被删除时，精细化清理缓存
    """
    # 清理该作品的详情缓存
    clear_cache_pattern(f'get_work_by_id:{instance.id}')
    # 清理合集列表缓存
    clear_cache_pattern('get_collections')
    # 清理该合集下的作品列表缓存
    clear_cache_pattern(f'get_works:collection_id={instance.collection.id}')
    # 清理作品列表缓存（所有作品）
    clear_cache_pattern('get_works:')