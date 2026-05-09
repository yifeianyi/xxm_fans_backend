from django.db import models
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class Recommendation(models.Model):
    """推荐语模型"""
    content = models.TextField(help_text="推荐语内容")
    recommended_songs = models.ManyToManyField(
        'song_management.Song',
        blank=True,
        help_text="推荐的歌曲",
        related_name='recommendations'
    )
    is_active = models.BooleanField(default=True, help_text="是否激活显示")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "推荐语"
        verbose_name_plural = "推荐语"
        ordering = ['-created_at']

    def __str__(self):
        return f"推荐语: {self.content[:50]}..." if len(self.content) > 50 else f"推荐语: {self.content}"


class SiteSettings(models.Model):
    """网站设置模型"""
    favicon = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name="网站图标"
    )

    # 艺人信息字段
    artist_name = models.CharField(max_length=100, blank=True, verbose_name="艺人名称")
    artist_avatar = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name="艺人头像"
    )
    artist_birthday = models.DateField(blank=True, null=True, verbose_name="艺人生日")
    artist_constellation = models.CharField(max_length=50, blank=True, verbose_name="星座")
    artist_location = models.CharField(max_length=200, blank=True, verbose_name="栖息地")
    artist_profession = models.JSONField(default=list, verbose_name="职业")
    artist_voice_features = models.JSONField(default=list, verbose_name="声线特色")

    # 社交媒体链接
    bilibili_url = models.URLField(max_length=500, blank=True, verbose_name="B站链接")
    weibo_url = models.URLField(max_length=500, blank=True, verbose_name="微博链接")
    netease_music_url = models.URLField(max_length=500, blank=True, verbose_name="网易云音乐链接")
    youtube_url = models.URLField(max_length=500, blank=True, verbose_name="YouTube链接")
    qq_music_url = models.URLField(max_length=500, blank=True, verbose_name="QQ音乐链接")
    xiaohongshu_url = models.URLField(max_length=500, blank=True, verbose_name="小红书链接")
    douyin_url = models.URLField(max_length=500, blank=True, verbose_name="抖音链接")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def __str__(self):
        return "网站设置"

    def favicon_url(self):
        """返回favicon的URL路径"""
        if self.favicon:
            return self.favicon.url
        return None

    def artist_avatar_url(self):
        """返回艺人头像的URL路径"""
        if self.artist_avatar:
            return self.artist_avatar.url
        return None


class Milestone(models.Model):
    """里程碑模型"""
    date = models.DateField(verbose_name="里程碑日期")
    title = models.CharField(max_length=200, verbose_name="里程碑标题")
    description = models.TextField(verbose_name="里程碑描述")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "里程碑"
        verbose_name_plural = "里程碑"
        ordering = ['-date', 'display_order']

    def __str__(self):
        return f"{self.date} - {self.title}"


class EmailConfig(models.Model):
    """邮箱配置模型（单例，用于 SMTP 邮件发送）"""
    smtp_host = models.CharField(max_length=200, default='smtp.qq.com', verbose_name='SMTP服务器')
    smtp_port = models.IntegerField(default=587, verbose_name='SMTP端口')
    smtp_use_tls = models.BooleanField(default=True, verbose_name='使用TLS')
    smtp_username = models.CharField(max_length=200, blank=True, default='', verbose_name='发件邮箱')
    smtp_password = models.CharField(max_length=300, blank=True, default='', verbose_name='SMTP授权码')

    _plain_password = None

    def set_password(self, raw_password):
        if raw_password:
            from core.crypto_utils import encrypt
            self.smtp_password = encrypt(raw_password)
        else:
            self.smtp_password = ''

    def get_password(self):
        if self._plain_password is not None:
            return self._plain_password
        if self.smtp_password:
            try:
                from core.crypto_utils import decrypt
                return decrypt(self.smtp_password)
            except Exception:
                return self.smtp_password
        return ''

    def save(self, *args, **kwargs):
        if self._plain_password is not None:
            self.set_password(self._plain_password)
            self._plain_password = None
        super().save(*args, **kwargs)
    admin_email = models.EmailField(max_length=200, blank=True, default='', verbose_name='管理员邮箱')
    from_email = models.EmailField(max_length=200, blank=True, default='', verbose_name='发件人地址')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '邮箱配置'
        verbose_name_plural = '邮箱配置'

    def __str__(self):
        return f"邮箱配置 ({self.smtp_username or '未配置'})"