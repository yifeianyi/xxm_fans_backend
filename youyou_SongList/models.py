from django.db import models

# Create your models here.
class you_Songs(models.Model):
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    language = models.CharField(max_length=50, verbose_name='语言')
    singer = models.CharField(max_length=100, verbose_name='歌手')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return self.song_name

    class Meta:
        verbose_name = '歌曲'
        verbose_name_plural = '歌曲'


class you_site_setting(models.Model):
    photoURL = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(verbose_name='位置')  # 1: head_icon, 2: background

    def __str__(self):
        return f"设置 - 位置: {self.position}"

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'