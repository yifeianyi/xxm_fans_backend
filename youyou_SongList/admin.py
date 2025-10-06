from django.contrib import admin
from .models import you_Songs, you_site_setting

# Register your models here.
@admin.register(you_Songs)
class you_SongsAdmin(admin.ModelAdmin):
    list_display = ('song_name', 'language', 'singer', 'style')
    search_fields = ('song_name', 'singer')
    list_filter = ('language', 'style')


@admin.register(you_site_setting)
class you_site_settingAdmin(admin.ModelAdmin):
    list_display = ('position', 'photoURL')
    list_filter = ('position',)