from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from ..models import PlatformCookie


class CookieService:

    @classmethod
    def get_cookie(cls, platform):
        """获取指定平台的有效 Cookie"""
        cookie = PlatformCookie.objects.filter(
            platform=platform,
            is_valid=True
        ).first()
        return cookie.get_cookie_string() if cookie else None

    @classmethod
    def mark_expired(cls, platform):
        """标记 Cookie 过期并发送邮件通知"""
        try:
            cookie = PlatformCookie.objects.get(platform=platform)
        except PlatformCookie.DoesNotExist:
            return

        if cookie.is_valid:
            cookie.is_valid = False
            cookie.last_checked = timezone.now()
            cookie.save(update_fields=['is_valid', 'last_checked'])

            if not cookie.expire_notified:
                cls._send_expiry_email(platform)
                cookie.expire_notified = True
                cookie.save(update_fields=['expire_notified'])

    @classmethod
    def mark_valid(cls, platform):
        """标记 Cookie 仍然有效"""
        try:
            cookie = PlatformCookie.objects.get(platform=platform)
        except PlatformCookie.DoesNotExist:
            return
        cookie.is_valid = True
        cookie.last_checked = timezone.now()
        cookie.expire_notified = False
        cookie.save(update_fields=['is_valid', 'last_checked', 'expire_notified'])

    @classmethod
    def _send_expiry_email(cls, platform):
        """发送 Cookie 过期提醒邮件"""
        platform_label = '微博' if platform == 'weibo' else 'B站'
        admin_email = getattr(settings, 'ADMIN_EMAIL', None)
        if not admin_email:
            return

        subject = f'[小满虫之家] {platform_label} Cookie 已过期'
        message = (
            f'管理员您好，\n\n'
            f'{platform_label} 平台的 Cookie 已过期，爬虫无法正常抓取动态。\n\n'
            f'请登录 {platform_label} 网页版，从浏览器开发者工具复制新的 Cookie，'
            f'并在 Django Admin 后台的"平台 Cookie"中更新。\n\n'
            f'过期时间：{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            f'-- 小满虫之家自动通知系统'
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[admin_email],
            fail_silently=True,
        )
