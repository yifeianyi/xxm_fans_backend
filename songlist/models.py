from django.db import models


# 歌手配置字典（一句话配置一个歌手）
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
}


def create_artist_models(artist_key, artist_name):
    """同时创建歌手的Song和SiteSetting模型"""
    class_name = artist_key.capitalize()  # youyou -> Youyou, bingjie -> Bingjie

    # 创建Song模型
    class SongMeta:
        verbose_name = f'{artist_name}歌曲'
        verbose_name_plural = f'{artist_name}歌曲'
        app_label = 'songlist'
        ordering = ['song_name']

    song_attrs = {
        '__module__': 'songlist.models',
        'song_name': models.CharField(max_length=200, verbose_name='歌曲名称'),
        'singer': models.CharField(max_length=100, verbose_name='原唱歌手'),
        'language': models.CharField(max_length=50, verbose_name='语言'),
        'style': models.CharField(max_length=50, verbose_name='曲风'),
        'note': models.TextField(blank=True, verbose_name='备注'),
        'Meta': SongMeta,
        '__str__': lambda self: self.song_name,
    }

    song_model = type(f'{class_name}Song', (models.Model,), song_attrs)

    # 创建SiteSetting模型
    class SettingMeta:
        verbose_name = f'{artist_name}网站设置'
        verbose_name_plural = f'{artist_name}网站设置'
        app_label = 'songlist'

    setting_attrs = {
        '__module__': 'songlist.models',
        'photo': models.ImageField(
            upload_to=f'songlist/{artist_key}/',
            verbose_name='图片',
            blank=True,
            null=True
        ),
        'photo_url': models.CharField(
            max_length=500,
            verbose_name='图片URL',
            blank=True,
            help_text='如果上传了图片，此字段将自动填充'
        ),
        'position': models.IntegerField(
            verbose_name='位置',
            choices=[
                (1, '头像图标'),
                (2, '背景图片'),
            ]
        ),
        'Meta': SettingMeta,
        '__str__': lambda self: f"设置 - 位置: {self.get_position_display()}",
    }

    setting_model = type(f'{class_name}SiteSetting', (models.Model,), setting_attrs)

    return song_model, setting_model


# 动态创建所有歌手的模型
for artist_key, artist_name in ARTIST_CONFIG.items():
    song_model, setting_model = create_artist_models(artist_key, artist_name)
    class_name = artist_key.capitalize()
    globals()[f'{class_name}Song'] = song_model
    globals()[f'{class_name}SiteSetting'] = setting_model


# 导出模型供其他模块使用
YouyouSong = globals()['YouyouSong']
BingjieSong = globals()['BingjieSong']
YouyouSiteSetting = globals()['YouyouSiteSetting']
BingjieSiteSetting = globals()['BingjieSiteSetting']


# 将模型添加到模块的 __all__ 中，确保Django能正确识别
__all__ = ['YouyouSong', 'BingjieSong', 'YouyouSiteSetting', 'BingjieSiteSetting']