"""
信号处理器 - 自动更新歌曲的统计字段和精细化清理缓存
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .song import Song, SongRecord
from .style import Style, SongStyle
from .tag import Tag, SongTag
from .original_work import OriginalWork
from core.cache import clear_cache_pattern


@receiver(post_save, sender=SongRecord)
def update_song_stats_on_record_save(sender, instance, created, **kwargs):
    """
    当演唱记录被创建或更新时，自动更新歌曲的统计字段并精细化清理缓存
    """
    # 获取当前关联的歌曲
    current_song = instance.song

    # 如果是更新操作（非创建），检查歌曲是否发生了变化
    if not created and instance.pk:
        try:
            # 尝试获取保存前的歌曲信息
            old_instance = SongRecord.objects.select_related('song').only('song').get(pk=instance.pk)
            old_song = old_instance.song

            # 如果歌曲发生了变化，需要更新旧歌曲的统计信息
            if old_song != current_song:
                old_records = old_song.records.all()
                old_song.perform_count = old_records.count()
                earliest_old_record = old_records.order_by('performed_at').first()
                old_song.first_perform = earliest_old_record.performed_at if earliest_old_record else None
                latest_old_record = old_records.order_by('-performed_at').first()
                old_song.last_performed = latest_old_record.performed_at if latest_old_record else None
                old_song.save(update_fields=['perform_count', 'first_perform', 'last_performed'])

                # 清理旧歌曲的缓存
                clear_cache_pattern(f'song_records:{old_song.id}')
                clear_cache_pattern(f'song_detail:{old_song.id}')
        except SongRecord.DoesNotExist:
            # 如果找不到旧记录，忽略并继续处理
            pass

    # 更新当前歌曲的统计信息
    records = current_song.records.all()

    # 更新演唱次数
    current_song.perform_count = records.count()

    # 更新首次演唱时间
    earliest_record = records.order_by('performed_at').first()
    current_song.first_perform = earliest_record.performed_at if earliest_record else None

    # 更新最近演唱时间
    latest_record = records.order_by('-performed_at').first()
    current_song.last_performed = latest_record.performed_at if latest_record else None

    current_song.save(update_fields=['perform_count', 'first_perform', 'last_performed'])

    # 精细化清理缓存：只清理与该歌曲相关的缓存
    clear_cache_pattern(f'song_records:{current_song.id}')  # 清理该歌曲的记录缓存
    clear_cache_pattern(f'song_detail:{current_song.id}')  # 清理该歌曲的详情缓存
    clear_cache_pattern('top_songs')  # 清理排行榜缓存
    clear_cache_pattern('random_song')  # 清理随机歌曲缓存
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')


@receiver(post_delete, sender=SongRecord)
def update_song_stats_on_record_delete(sender, instance, **kwargs):
    """
    当演唱记录被删除时，自动更新歌曲的统计字段并精细化清理缓存
    """
    song = instance.song
    records = song.records.all()

    # 更新演唱次数
    song.perform_count = records.count()

    # 更新首次演唱时间
    earliest_record = records.order_by('performed_at').first()
    song.first_perform = earliest_record.performed_at if earliest_record else None

    # 更新最近演唱时间
    latest_record = records.order_by('-performed_at').first()
    song.last_performed = latest_record.performed_at if latest_record else None

    song.save(update_fields=['perform_count', 'first_perform', 'last_performed'])

    # 精细化清理缓存：只清理与该歌曲相关的缓存
    clear_cache_pattern(f'song_records:{song.id}')  # 清理该歌曲的记录缓存
    clear_cache_pattern('top_songs')  # 清理排行榜缓存
    clear_cache_pattern('random_song')  # 清理随机歌曲缓存
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')


@receiver(post_save, sender=Song)
def clear_cache_on_song_save(sender, instance, created, **kwargs):
    """
    当歌曲被创建或更新时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存
    clear_cache_pattern(f'song_detail:{instance.id}')
    
    # 如果更新了曲风或标签，也需要清理排行榜缓存
    if not created:
        clear_cache_pattern('top_songs')
        clear_cache_pattern('random_song')
        # 清理歌曲列表 API 缓存
        clear_cache_pattern('song_list_api')


@receiver(post_delete, sender=Song)
def clear_cache_on_song_delete(sender, instance, **kwargs):
    """
    当歌曲被删除时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存和记录缓存
    clear_cache_pattern(f'song_detail:{instance.id}')
    clear_cache_pattern(f'song_records:{instance.id}')
    
    # 清理排行榜和随机歌曲缓存
    clear_cache_pattern('top_songs')
    clear_cache_pattern('random_song')
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')


@receiver(post_save, sender=SongStyle)
def clear_cache_on_song_style_save(sender, instance, created, **kwargs):
    """
    当歌曲-曲风关联被创建或更新时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存
    clear_cache_pattern(f'song_detail:{instance.song.id}')
    # 清理排行榜缓存（因为曲风可能影响筛选结果）
    clear_cache_pattern('top_songs')
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')
    # 清理曲风列表缓存
    clear_cache_pattern('style_list_simple')


@receiver(post_delete, sender=SongStyle)
def clear_cache_on_song_style_delete(sender, instance, **kwargs):
    """
    当歌曲-曲风关联被删除时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存
    clear_cache_pattern(f'song_detail:{instance.song.id}')
    # 清理排行榜缓存
    clear_cache_pattern('top_songs')
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')
    # 清理曲风列表缓存
    clear_cache_pattern('style_list_simple')


@receiver(post_save, sender=SongTag)
def clear_cache_on_song_tag_save(sender, instance, created, **kwargs):
    """
    当歌曲-标签关联被创建或更新时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存
    clear_cache_pattern(f'song_detail:{instance.song.id}')
    # 清理排行榜缓存
    clear_cache_pattern('top_songs')
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')
    # 清理标签列表缓存
    clear_cache_pattern('tag_list_simple')


@receiver(post_delete, sender=SongTag)
def clear_cache_on_song_tag_delete(sender, instance, **kwargs):
    """
    当歌曲-标签关联被删除时，精细化清理缓存
    """
    # 清理该歌曲的详情缓存
    clear_cache_pattern(f'song_detail:{instance.song.id}')
    # 清理排行榜缓存
    clear_cache_pattern('top_songs')
    # 清理歌曲列表 API 缓存
    clear_cache_pattern('song_list_api')
    # 清理标签列表缓存
    clear_cache_pattern('tag_list_simple')


@receiver(post_save, sender=OriginalWork)
def clear_cache_on_original_work_save(sender, instance, created, **kwargs):
    """
    当原创作品被创建或更新时，精细化清理缓存
    """
    # 清理原创作品列表缓存
    clear_cache_pattern('original_works_list')


@receiver(post_delete, sender=OriginalWork)
def clear_cache_on_original_work_delete(sender, instance, **kwargs):
    """
    当原创作品被删除时，精细化清理缓存
    """
    # 清理原创作品列表缓存
    clear_cache_pattern('original_works_list')