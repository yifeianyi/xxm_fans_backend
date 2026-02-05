"""
歌曲相关模型
"""
from django.db import models


class Song(models.Model):
    """歌曲模型"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=200, blank=True, null=True, verbose_name='歌手')
    first_perform = models.DateField(blank=True, null=True, verbose_name='首次演唱时间')
    last_performed = models.DateField(blank=True, null=True, verbose_name='最近演唱时间')
    perform_count = models.IntegerField(default=0, verbose_name='演唱次数')
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name='语言')

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"
        ordering = ['song_name']
        indexes = [
            models.Index(fields=['song_name']),
            models.Index(fields=['singer']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.song_name

    @property
    def styles(self):
        """获取歌曲的曲风列表"""
        return [song_style.style.name for song_style in self.song_styles.all()]

    @property
    def tags(self):
        """获取歌曲的标签列表"""
        return [song_tag.tag.name for song_tag in self.song_tags.all()]


class SongRecord(models.Model):
    """演唱记录模型"""
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='歌曲'
    )
    performed_at = models.DateField(verbose_name='演唱时间')
    url = models.URLField(blank=True, null=True, verbose_name='视频链接')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    cover_url = models.CharField(max_length=300, blank=True, null=True, verbose_name='封面URL')

    class Meta:
        verbose_name = "演唱记录"
        verbose_name_plural = "演唱记录"
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['song', '-performed_at']),
            models.Index(fields=['performed_at']),
        ]

    def __str__(self):
        return f"{self.song.song_name} @ {self.performed_at}"

    def get_cover_thumbnail_url(self):
        """获取封面缩略图 URL"""
        if not self.cover_url:
            return self.cover_url
        
        from core.thumbnail_generator import ThumbnailGenerator
        return ThumbnailGenerator.get_thumbnail_url(self.cover_url)