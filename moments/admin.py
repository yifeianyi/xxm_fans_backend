from django.contrib import admin
from .models import Moment, PlatformCookie


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ('source', 'source_id', 'content_preview', 'publish_time', 'created_at')
    list_filter = ('source', 'publish_time')
    search_fields = ('content', 'source_id')
    readonly_fields = ('created_at',)
    ordering = ('-publish_time',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'


@admin.register(PlatformCookie)
class PlatformCookieAdmin(admin.ModelAdmin):
    list_display = ('platform', 'is_valid', 'expire_notified', 'last_checked', 'updated_at')
    list_filter = ('platform', 'is_valid')
    readonly_fields = ('last_checked', 'updated_at', 'created_at')
