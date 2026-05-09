from django.apps import AppConfig


class LivefansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'livefans'
    verbose_name = '粉丝直播数据'

    def ready(self):
        import livefans.signals  # noqa: F401
