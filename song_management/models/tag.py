"""
标签相关模型
"""
from django.db import models


class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='标签名称')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        ordering = ['name']

    def __str__(self):
        return self.name


class SongTag(models.Model):
    """歌曲-标签关联表"""
    song = models.ForeignKey(
        'song_management.Song',
        on_delete=models.CASCADE,
        related_name='song_tags',
        verbose_name='歌曲'
    )
    tag = models.ForeignKey(
        'song_management.Tag',
        on_delete=models.CASCADE,
        related_name='tag_songs',
        verbose_name='标签'
    )

    class Meta:
        unique_together = ("song", "tag")
        verbose_name = "歌曲标签"
        verbose_name_plural = "歌曲标签"
        indexes = [
            models.Index(fields=['song']),
            models.Index(fields=['tag']),
            models.Index(fields=['song', 'tag']),
        ]

    def __str__(self):
        return f"{self.song.song_name} - {self.tag.name}"