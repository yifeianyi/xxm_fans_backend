from django.db import models


class Song(models.Model):
    """统一的歌曲模型 - 用于冰洁和乐游的歌单"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=100, verbose_name='歌手')
    language = models.CharField(max_length=50, verbose_name='语言')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '歌曲'
        verbose_name_plural = '歌曲'
        ordering = ['song_name']

    def __str__(self):
        return self.song_name


class SiteSetting(models.Model):
    """网站设置模型 - 用于冰洁和乐游的网站设置"""
    photo_url = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(
        verbose_name='位置',
        choices=[
            (1, '头像图标'),
            (2, '背景图片'),
        ]
    )

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'

    def __str__(self):
        return f"设置 - 位置: {self.get_position_display()}"