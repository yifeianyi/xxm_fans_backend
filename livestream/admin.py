from django.contrib import admin
from .models import Livestream


@admin.register(Livestream)
class LivestreamAdmin(admin.ModelAdmin):
    """直播记录管理后台"""

    list_display = [
        'date',
        'title',
        'duration_formatted',
        'view_count',
        'danmaku_count',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'date']
    search_fields = ['title', 'summary', 'bvid']
    date_hierarchy = 'date'
    ordering = ['-date']

    fieldsets = (
        ('基础信息', {
            'fields': ('date', 'title', 'summary', 'live_moment', 'is_active', 'sort_order')
        }),
        ('B站视频信息', {
            'fields': ('bvid', 'duration_seconds', 'duration_formatted', 'parts')
        }),
        ('统计数据', {
            'fields': ('view_count', 'danmaku_count')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time')
        }),
        ('弹幕云图', {
            'fields': ('danmaku_cloud_url',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()