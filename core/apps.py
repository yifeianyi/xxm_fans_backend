from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = '核心模块'

    def ready(self):
        """应用启动时注册信号处理器"""
        try:
            import core.signals
        except ImportError:
            pass