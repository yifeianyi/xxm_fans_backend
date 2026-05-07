from django.contrib import admin
from .models import FanProfile, LiveAttendance


@admin.register(FanProfile)
class FanProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'bilibili_uid', 'platform', 'first_seen_at', 'created_at')
    list_filter = ('platform',)
    search_fields = ('username', 'bilibili_uid')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(LiveAttendance)
class LiveAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'fan_username', 'livestream_date', 'is_attended',
        'danmaku_count', 'has_gift', 'has_sc', 'has_guard'
    )
    list_filter = ('is_attended', 'has_gift', 'has_sc', 'has_guard')
    search_fields = ('fan__username', 'fan__bilibili_uid')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-livestream__date',)

    def fan_username(self, obj):
        return obj.fan.username
    fan_username.short_description = '粉丝'
    fan_username.admin_order_field = 'fan__username'

    def livestream_date(self, obj):
        return obj.livestream.date
    livestream_date.short_description = '直播日期'
    livestream_date.admin_order_field = 'livestream__date'
