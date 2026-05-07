from django.db import models


class MomentSource(models.TextChoices):
    WEIBO = 'weibo', '微博'
    BILIBILI = 'bilibili', 'B站'


class Moment(models.Model):
    source = models.CharField(
        max_length=20,
        choices=MomentSource.choices,
        verbose_name='来源平台',
        help_text='动态来源：微博或B站'
    )
    source_id = models.CharField(
        max_length=100,
        verbose_name='平台原始ID',
        help_text='微博或B站动态的唯一标识'
    )
    content = models.TextField(
        verbose_name='动态内容',
        help_text='纯文本内容'
    )
    images = models.JSONField(
        default=list,
        verbose_name='图片列表',
        help_text='[{"original_url": "", "thumbnail_url": ""}]'
    )
    publish_time = models.DateTimeField(
        verbose_name='发布时间',
        help_text='动态在原平台的发布时间'
    )
    like_count = models.IntegerField(
        default=0,
        verbose_name='点赞数'
    )
    comment_count = models.IntegerField(
        default=0,
        verbose_name='评论数'
    )
    share_count = models.IntegerField(
        default=0,
        verbose_name='转发数'
    )
    source_url = models.URLField(
        blank=True,
        verbose_name='原始链接',
        help_text='动态在原平台的链接'
    )
    video_bvid = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='B站BV号',
        help_text='当来源为B站且动态包含视频时，保存视频的BV号'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='抓取时间'
    )

    class Meta:
        db_table = 'moments'
        verbose_name = '动态'
        verbose_name_plural = '动态'
        ordering = ['-publish_time']
        unique_together = ('source', 'source_id')
        indexes = [
            models.Index(fields=['source', 'publish_time']),
            models.Index(fields=['-publish_time']),
        ]

    def __str__(self):
        source_label = '微博' if self.source == 'weibo' else 'B站'
        preview = self.content[:30] + '...' if len(self.content) > 30 else self.content
        return f'[{source_label}] {preview}'


class PlatformCookie(models.Model):
    PLATFORM_CHOICES = [
        ('weibo', '微博'),
        ('bilibili', 'B站'),
    ]

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        unique=True,
        verbose_name='平台',
        help_text='Cookie 对应的平台'
    )
    cookie_string = models.TextField(
        verbose_name='Cookie 字符串',
        help_text='完整的 Cookie 字符串，从浏览器开发者工具复制'
    )
    is_valid = models.BooleanField(
        default=True,
        verbose_name='是否有效',
        help_text='Cookie 是否仍然有效'
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='上次检查时间'
    )
    expire_notified = models.BooleanField(
        default=False,
        verbose_name='已发送过期通知',
        help_text='Cookie 过期后是否已发送邮件通知管理员'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'moments_platform_cookies'
        verbose_name = '平台 Cookie'
        verbose_name_plural = '平台 Cookie'

    def __str__(self):
        status = '有效' if self.is_valid else '已过期'
        platform_label = '微博' if self.platform == 'weibo' else 'B站'
        return f'[{platform_label}] {status}'
