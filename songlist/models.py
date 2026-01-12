from django.db import models


class BaseSong(models.Model):
    """歌曲基类"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=100, verbose_name='原唱歌手')
    language = models.CharField(max_length=50, verbose_name='语言')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        abstract = True
        ordering = ['song_name']

    def __str__(self):
        return self.song_name


class BaseSiteSetting(models.Model):
    """网站设置基类"""
    photo_url = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(
        verbose_name='位置',
        choices=[
            (1, '头像图标'),
            (2, '背景图片'),
        ]
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"设置 - 位置: {self.get_position_display()}"


class YouyouSong(BaseSong):
    """乐游歌曲表"""
    class Meta:
        verbose_name = '乐游歌曲'
        verbose_name_plural = '乐游歌曲'


class BingjieSong(BaseSong):
    """冰洁歌曲表"""
    class Meta:
        verbose_name = '冰洁歌曲'
        verbose_name_plural = '冰洁歌曲'


class YouyouSiteSetting(BaseSiteSetting):
    """乐游网站设置表"""
    class Meta:
        verbose_name = '乐游网站设置'
        verbose_name_plural = '乐游网站设置'


class BingjieSiteSetting(BaseSiteSetting):
    """冰洁网站设置表"""
    class Meta:
        verbose_name = '冰洁网站设置'
        verbose_name_plural = '冰洁网站设置'