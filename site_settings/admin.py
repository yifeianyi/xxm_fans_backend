from django.contrib import admin
from site_settings.models import SiteSettings, Recommendation


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """网站设置Admin"""
    list_display = ['id', 'favicon_url', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = []
    readonly_fields = ['created_at', 'updated_at']

    def favicon_url(self, obj):
        """显示favicon URL"""
        return obj.favicon_url()
    favicon_url.short_description = '图标URL'

    def has_add_permission(self, request):
        """限制只能创建一个网站设置"""
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """推荐语Admin"""
    list_display = ['id', 'content_preview', 'is_active', 'song_count', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['content']
    filter_horizontal = ['recommended_songs']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['activate_recommendations', 'deactivate_recommendations']

    def content_preview(self, obj):
        """显示推荐语预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '推荐语内容'

    def song_count(self, obj):
        """显示推荐歌曲数量"""
        return obj.recommended_songs.count()
    song_count.short_description = '推荐歌曲数'

    def activate_recommendations(self, request, queryset):
        """批量激活推荐语"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 条推荐语。')
    activate_recommendations.short_description = '激活选中的推荐语'

    def deactivate_recommendations(self, request, queryset):
        """批量停用推荐语"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 条推荐语。')
    deactivate_recommendations.short_description = '停用选中的推荐语'