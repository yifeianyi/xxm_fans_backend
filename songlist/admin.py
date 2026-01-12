from django.contrib import admin
from .models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting


@admin.register(YouyouSong)
class YouyouSongAdmin(admin.ModelAdmin):
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(BingjieSong)
class BingjieSongAdmin(admin.ModelAdmin):
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(YouyouSiteSetting)
class YouyouSiteSettingAdmin(admin.ModelAdmin):
    list_display = ['photo_url', 'position']
    list_filter = ['position']
    list_per_page = 50


@admin.register(BingjieSiteSetting)
class BingjieSiteSettingAdmin(admin.ModelAdmin):
    list_display = ['photo_url', 'position']
    list_filter = ['position']
    list_per_page = 50