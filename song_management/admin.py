"""
Admin 配置
"""
from django.contrib import admin
from .models import Song, SongRecord, Style, SongStyle, Tag, SongTag


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """歌曲管理"""
    list_display = ['id', 'song_name', 'singer', 'language', 'last_performed', 'perform_count']
    list_filter = ['language', 'last_performed']
    search_fields = ['song_name', 'singer']
    list_per_page = 50
    readonly_fields = ['perform_count']

    fieldsets = (
        ('基本信息', {
            'fields': ('song_name', 'singer', 'language')
        }),
        ('演唱信息', {
            'fields': ('last_performed', 'perform_count')
        }),
    )


@admin.register(SongRecord)
class SongRecordAdmin(admin.ModelAdmin):
    """演唱记录管理"""
    list_display = ['id', 'song', 'performed_at', 'url']
    list_filter = ['performed_at']
    search_fields = ['song__song_name']
    list_per_page = 50


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    """曲风管理"""
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


@admin.register(SongStyle)
class SongStyleAdmin(admin.ModelAdmin):
    """歌曲曲风关联管理"""
    list_display = ['id', 'song', 'style']
    list_filter = ['style']
    search_fields = ['song__song_name', 'style__name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """标签管理"""
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


@admin.register(SongTag)
class SongTagAdmin(admin.ModelAdmin):
    """歌曲标签关联管理"""
    list_display = ['id', 'song', 'tag']
    list_filter = ['tag']
    search_fields = ['song__song_name', 'tag__name']