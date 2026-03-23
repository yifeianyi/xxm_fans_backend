from django.contrib import admin
from django.utils.html import format_html
from .models import ARTIST_CONFIG


class BaseSongAdmin(admin.ModelAdmin):
    """歌曲Admin基础配置"""
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
            # 使用 name 而不是 url，避免 URL 编码问题
            # 只保存文件名，不保存完整路径
            import os
            obj.photo_url = os.path.basename(obj.photo.name)
        super().save_model(request, obj, form, change)


def create_admin_classes(artist_key, artist_name):
    """动态创建Admin类"""
    class_name = artist_key.capitalize()
    
    # 动态创建歌曲Admin类
    song_admin_class = type(
        f'{class_name}SongAdmin',
        (BaseSongAdmin,),
        {
            '__module__': 'songlist.admin',
        }
    )
    
    # 动态创建网站设置Admin类
    setting_admin_class = type(
        f'{class_name}SiteSettingAdmin',
        (BaseSiteSettingAdmin,),
        {
            '__module__': 'songlist.admin',
        }
    )
    
    return song_admin_class, setting_admin_class


def register_artist_admins():
    """注册所有歌手的Admin"""
    from . import models
    
    for artist_key, artist_name in ARTIST_CONFIG.items():
        class_name = artist_key.capitalize()
        song_model_name = f'{class_name}Song'
        setting_model_name = f'{class_name}SiteSetting'
        
        # 从models模块获取动态创建的模型类
        song_model = getattr(models, song_model_name, None)
        setting_model = getattr(models, setting_model_name, None)
        
        if song_model and not admin.site.is_registered(song_model):
            song_admin_class, _ = create_admin_classes(artist_key, artist_name)
            admin.site.register(song_model, song_admin_class)
        
        if setting_model and not admin.site.is_registered(setting_model):
            _, setting_admin_class = create_admin_classes(artist_key, artist_name)
            admin.site.register(setting_model, setting_admin_class)


# 注册所有Admin
register_artist_admins()
