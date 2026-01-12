from django.db import models


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