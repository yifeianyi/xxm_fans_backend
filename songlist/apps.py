from django.apps import AppConfig


class SonglistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'songlist'
    verbose_name = '歌单管理'