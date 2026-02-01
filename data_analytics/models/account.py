"""
账号配置模型
定义要追踪的B站账号
"""
from django.db import models


class Account(models.Model):
    """账号配置表"""
    PLATFORM_CHOICES = [
        ('bilibili', '哔哩哔哩'),
    ]

    uid = models.CharField(max_length=50, unique=True, verbose_name="账号UID")
    name = models.CharField(max_length=200, verbose_name="账号名称")
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        default='bilibili',
        verbose_name="平台"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'data_analytics_account'
        verbose_name = "账号配置"
        verbose_name_plural = "账号配置"
        ordering = ['id']
        indexes = [
            models.Index(fields=['platform', 'uid']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.platform}/{self.uid})"