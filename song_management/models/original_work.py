"""
原创作品模型
"""
from django.db import models


class OriginalWork(models.Model):
    """原创作品模型"""
    title = models.CharField(max_length=200, verbose_name='作品标题')
    release_date = models.DateField(verbose_name='发布日期')
    description = models.TextField(blank=True, null=True, verbose_name='作品描述')
    cover = models.ImageField(upload_to='covers/original/', blank=True, null=True, verbose_name='封面图片')
    netease_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='网易云音乐 ID')
    bilibili_bvid = models.CharField(max_length=50, blank=True, null=True, verbose_name='B站 BV 号')
    featured = models.BooleanField(default=False, verbose_name='是否精选')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "原创作品"
        verbose_name_plural = "原创作品"
        ordering = ['-featured', '-release_date']
        indexes = [
            models.Index(fields=['featured']),
            models.Index(fields=['release_date']),
            models.Index(fields=['netease_id']),
            models.Index(fields=['bilibili_bvid']),
        ]

    def __str__(self):
        return self.title

    @property
    def date(self):
        """格式化的发布日期（兼容前端）"""
        return self.release_date.strftime('%Y.%m.%d') if self.release_date else ''

    @property
    def desc(self):
        """描述（兼容前端）"""
        return self.description or ''

    @property
    def neteaseId(self):
        """网易云音乐 ID（兼容前端）"""
        return self.netease_id

    @property
    def bilibiliBvid(self):
        """B站 BV 号（兼容前端）"""
        return self.bilibili_bvid