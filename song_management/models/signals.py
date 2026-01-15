"""
信号处理器 - 自动更新歌曲的统计字段
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .song import Song, SongRecord


@receiver(post_save, sender=SongRecord)
def update_song_stats_on_record_save(sender, instance, created, **kwargs):
    """
    当演唱记录被创建或更新时，自动更新歌曲的统计字段
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


@receiver(post_delete, sender=SongRecord)
def update_song_stats_on_record_delete(sender, instance, **kwargs):
    """
    当演唱记录被删除时，自动更新歌曲的统计字段
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