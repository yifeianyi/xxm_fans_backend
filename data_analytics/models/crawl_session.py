"""
爬取会话模型
"""
from django.db import models


class CrawlSession(models.Model):
    """爬取会话表"""
    source = models.CharField(max_length=50, verbose_name="数据源")
    node_id = models.CharField(max_length=100, verbose_name="节点ID")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    total_work_count = models.IntegerField(default=0, verbose_name="总作品数")
    success_count = models.IntegerField(default=0, verbose_name="成功数")
    fail_count = models.IntegerField(default=0, verbose_name="失败数")
    note = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "爬取会话"
        verbose_name_plural = "爬取会话"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['source', 'node_id']),
            models.Index(fields=['start_time']),
        ]

    def __str__(self):
        return f"{self.source} - {self.node_id} @ {self.start_time}"