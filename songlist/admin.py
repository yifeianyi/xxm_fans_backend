from django.contrib import admin
from .models import Song, SiteSetting


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['photo_url', 'position']
    list_filter = ['position']
    list_per_page = 50