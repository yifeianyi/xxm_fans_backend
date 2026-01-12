"""
作品小时级指标模型
"""
from django.db import models


class WorkMetricsHour(models.Model):
    """作品小时级指标表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    view_count = models.IntegerField(default=0, verbose_name="播放数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    coin_count = models.IntegerField(default=0, verbose_name="投币数")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    session_id = models.IntegerField(verbose_name="会话ID")
    ingest_time = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    class Meta:
        verbose_name = "作品小时指标"
        verbose_name_plural = "作品小时指标"
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['crawl_time']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"{self.work_id} @ {self.crawl_time}"