"""
Song Management 应用配置
"""
from django.apps import AppConfig


class SongManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'song_management'
    verbose_name = '歌曲管理'