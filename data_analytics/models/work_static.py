"""
作品静态信息模型
"""
from django.db import models


class WorkStatic(models.Model):
    """作品静态信息表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    author = models.CharField(max_length=200, verbose_name="作者")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    cover_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="封面URL", help_text="支持本地路径（如 /media/data_analytics/covers/xxx.jpg）或外部URL")
    is_valid = models.BooleanField(default=True, verbose_name="投稿是否有效")

    class Meta:
        db_table = 'data_analytics_workstatic'
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"
        unique_together = ("platform", "work_id")
        ordering = ['-publish_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['publish_time']),
        ]

    def __str__(self):
        return f"{self.title} - {self.author}"