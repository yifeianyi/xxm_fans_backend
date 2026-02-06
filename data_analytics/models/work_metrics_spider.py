"""
作品指标爬虫数据模型
对应爬虫系统导入的小时级数据
"""
from django.db import models


class WorkMetricsSpider(models.Model):
    """
    作品指标爬虫数据表
    存储从B站爬取的小时级作品数据（播放量、点赞数等）
    """
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, blank=True, null=True, verbose_name="标题")
    crawl_date = models.DateField(verbose_name="爬取日期")
    crawl_hour = models.CharField(max_length=2, verbose_name="爬取小时")
    crawl_time = models.TimeField(verbose_name="爬取时间")
    view_count = models.IntegerField(default=0, verbose_name="播放数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    coin_count = models.IntegerField(default=0, verbose_name="投币数")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏数")
    share_count = models.IntegerField(default=0, verbose_name="转发数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'data_analytics_workmetricsspider'
        verbose_name = "作品指标爬虫数据"
        verbose_name_plural = "作品指标爬虫数据"
        unique_together = ("platform", "work_id", "crawl_date", "crawl_hour")
        ordering = ['-crawl_date', '-crawl_hour', 'work_id']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['crawl_date']),
            models.Index(fields=['crawl_date', 'crawl_hour']),
        ]

    def __str__(self):
        return f"{self.work_id} @ {self.crawl_date} {self.crawl_hour}:00"

    @property
    def crawl_datetime(self):
        """返回完整的爬取日期时间"""
        from datetime import datetime
        return datetime.combine(self.crawl_date, self.crawl_time)
