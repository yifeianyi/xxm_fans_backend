"""
曲风相关模型
"""
from django.db import models


class Style(models.Model):
    """曲风模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='曲风名称')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = "曲风"
        verbose_name_plural = "曲风"
        ordering = ['name']

    def __str__(self):
        return self.name


class SongStyle(models.Model):
    """歌曲-曲风关联表"""
    song = models.ForeignKey(
        'song_management.Song',
        on_delete=models.CASCADE,
        related_name='song_styles',
        verbose_name='歌曲'
    )
    style = models.ForeignKey(
        'song_management.Style',
        on_delete=models.CASCADE,
        related_name='style_songs',
        verbose_name='曲风'
    )

    class Meta:
        unique_together = ("song", "style")
        verbose_name = "歌曲曲风"
        verbose_name_plural = "歌曲曲风"

    def __str__(self):
        return f"{self.song.song_name} - {self.style.name}"