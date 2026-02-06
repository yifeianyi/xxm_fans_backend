"""
爬虫会话模型
对应爬虫系统的会话记录
"""
from django.db import models


class CrawlSessionSpider(models.Model):
    """
    爬虫会话表
    存储每次爬取任务的会话信息
    """
    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    crawl_date = models.DateField(verbose_name="爬取日期")
    crawl_hour = models.CharField(max_length=2, verbose_name="爬取小时")
    start_time = models.TimeField(blank=True, null=True, verbose_name="开始时间")
    end_time = models.TimeField(blank=True, null=True, verbose_name="结束时间")
    total_count = models.IntegerField(default=0, verbose_name="总作品数")
    success_count = models.IntegerField(default=0, verbose_name="成功数")
    fail_count = models.IntegerField(default=0, verbose_name="失败数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'data_analytics_crawlsessionspider'
        verbose_name = "爬虫会话"
        verbose_name_plural = "爬虫会话"
        ordering = ['-crawl_date', '-crawl_hour']
        indexes = [
            models.Index(fields=['crawl_date']),
            models.Index(fields=['crawl_date', 'crawl_hour']),
        ]

    def __str__(self):
        return f"{self.session_id} ({self.crawl_date} {self.crawl_hour}:00)"

    @property
    def success_rate(self):
        """计算成功率"""
        if self.total_count > 0:
            return (self.success_count / self.total_count) * 100
        return 0

    @property
    def crawl_datetime(self):
        """返回完整的爬取日期时间"""
        from datetime import datetime
        if self.start_time:
            return datetime.combine(self.crawl_date, self.start_time)
        return None
