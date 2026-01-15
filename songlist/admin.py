from django.contrib import admin
from .models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting


def create_song_admin(model):
    """创建歌曲Admin类的工厂函数"""
    class SongAdmin(admin.ModelAdmin):
        list_display = ['song_name', 'singer', 'language', 'style']
        list_filter = ['language', 'style']
        search_fields = ['song_name', 'singer']
        list_per_page = 50

    return SongAdmin


def create_site_setting_admin(model):
    """创建网站设置Admin类的工厂函数"""
    class SiteSettingAdmin(admin.ModelAdmin):
        list_display = ['photo_url', 'position']
        list_filter = ['position']
        list_per_page = 50

    return SiteSettingAdmin


# 动态注册所有歌手的Admin
admin.site.register(YouyouSong, create_song_admin(YouyouSong))
admin.site.register(BingjieSong, create_song_admin(BingjieSong))
admin.site.register(YouyouSiteSetting, create_site_setting_admin(YouyouSiteSetting))
admin.site.register(BingjieSiteSetting, create_site_setting_admin(BingjieSiteSetting))