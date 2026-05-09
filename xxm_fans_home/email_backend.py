from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.conf import settings


class DatabaseEmailBackend(SMTPBackend):
    """从数据库读取 SMTP 配置的 Email Backend，数据库不可用时回退到环境变量"""

    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        db_host, db_port, db_user, db_password, db_use_tls = self._load_from_db()
        super().__init__(
            host=host or db_host,
            port=port or db_port,
            username=username or db_user,
            password=password or db_password,
            use_tls=use_tls if use_tls is not None else db_use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs
        )

    @staticmethod
    def _load_from_db():
        try:
            from site_settings.models import EmailConfig
            config = EmailConfig.objects.first()
            if config and config.smtp_username and config.smtp_password:
                return (
                    config.smtp_host,
                    config.smtp_port,
                    config.smtp_username,
                    config.smtp_password,
                    config.smtp_use_tls,
                )
        except Exception:
            pass
        return (
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD,
            settings.EMAIL_USE_TLS,
        )
