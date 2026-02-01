"""
粉丝数据模型
存储各账号的粉丝数变化数据
"""
from django.db import models


class FollowerMetrics(models.Model):
    """粉丝指标表"""
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        verbose_name="账号"
    )
    follower_count = models.IntegerField(default=0, verbose_name="粉丝数")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    ingest_time = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    class Meta:
        db_table = 'data_analytics_followermetrics'
        verbose_name = "粉丝指标"
        verbose_name_plural = "粉丝指标"
        ordering = ['-crawl_time']
        unique_together = ("account", "crawl_time")
        indexes = [
            models.Index(fields=['account', 'crawl_time']),
            models.Index(fields=['crawl_time']),
        ]

    def __str__(self):
        return f"{self.account.name}: {self.follower_count} @ {self.crawl_time}"