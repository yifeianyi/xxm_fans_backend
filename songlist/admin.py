from django.contrib import admin
from django.utils.html import format_html
from .models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting


@admin.register(YouyouSong)
class YouyouSongAdmin(admin.ModelAdmin):
    """乐游歌曲Admin配置"""
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(BingjieSong)
class BingjieSongAdmin(admin.ModelAdmin):
    """冰洁歌曲Admin配置"""
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


class BaseSiteSettingAdmin(admin.ModelAdmin):
    """网站设置基础Admin配置"""
    list_display = ['photo_preview', 'position', 'get_photo_url']
    list_filter = ['position']
    list_per_page = 50
    readonly_fields = ['photo_preview']
    fieldsets = (
        ('图片设置', {
            'fields': ('photo', 'photo_url'),
        }),
        ('其他设置', {
            'fields': ('position',),
        }),
    )

    def photo_preview(self, obj):
        """图片预览"""
        if obj.photo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.photo.url)
        elif obj.photo_url:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.photo_url)
        return '无图片'
    photo_preview.short_description = '图片预览'

    def get_photo_url(self, obj):
        """获取图片URL"""
        if obj.photo:
            return obj.photo.url
        return obj.photo_url
    get_photo_url.short_description = '图片URL'

    def save_model(self, request, obj, form, change):
        """保存时自动设置 photo_url"""
        if obj.photo:
            obj.photo_url = obj.photo.url
        super().save_model(request, obj, form, change)


@admin.register(YouyouSiteSetting)
class YouyouSiteSettingAdmin(BaseSiteSettingAdmin):
    """乐游网站设置Admin配置"""
    pass


@admin.register(BingjieSiteSetting)
class BingjieSiteSettingAdmin(BaseSiteSettingAdmin):
    """冰洁网站设置Admin配置"""
    pass