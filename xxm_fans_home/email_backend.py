import logging
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class DatabaseEmailBackend(SMTPBackend):

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
        except ImportError:
            logger.debug("EmailConfig model not available yet")
            return DatabaseEmailBackend._env_fallback()

        try:
            config = EmailConfig.objects.first()
        except Exception as e:
            logger.warning("Failed to query EmailConfig: %s", e)
            return DatabaseEmailBackend._env_fallback()

        if config and config.smtp_username:
            try:
                decrypted_password = config.get_password()
            except Exception as e:
                logger.warning("Failed to decrypt smtp_password: %s", e)
                decrypted_password = ''

            if config.admin_email:
                setattr(settings, 'ADMIN_EMAIL', config.admin_email)
            if config.from_email:
                setattr(settings, 'DEFAULT_FROM_EMAIL', config.from_email)
            elif config.smtp_username:
                setattr(settings, 'DEFAULT_FROM_EMAIL', config.smtp_username)

            return (
                config.smtp_host,
                config.smtp_port,
                config.smtp_username,
                decrypted_password,
                config.smtp_use_tls,
            )
        return DatabaseEmailBackend._env_fallback()

    @staticmethod
    def _env_fallback():
        return (
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD,
            settings.EMAIL_USE_TLS,
        )
