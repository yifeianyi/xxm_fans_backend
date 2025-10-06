from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
import os
from .models import you_Songs, you_site_setting

# Register your models here.
@admin.register(you_Songs)
class you_SongsAdmin(admin.ModelAdmin):
    list_display = ('song_name', 'language', 'singer', 'style')
    search_fields = ('song_name', 'singer')
    list_filter = ('language', 'style')


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = you_site_setting
        fields = '__all__'
        widgets = {
            'photoURL': forms.FileInput(attrs={'accept': 'image/*'}),
        }


@admin.register(you_site_setting)
class you_site_settingAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display = ('position', 'photo_preview')
    list_filter = ('position',)
    fields = ('position', 'photoURL')
    
    def photo_preview(self, obj):
        if obj.photoURL:
            # 处理图片路径，确保能正确显示预览
            photo_url = obj.photoURL
            if photo_url.startswith('/'):
                photo_url = photo_url[1:]
            return mark_safe(f'<img src="/{photo_url}" style="height:48px;max-width:80px;object-fit:cover;" />')
        return "-"
    photo_preview.short_description = "图片预览"
    
    def save_model(self, request, obj, form, change):
        # 处理图片上传
        if 'photoURL' in request.FILES:
            uploaded_file = request.FILES['photoURL']
            # 确保目录存在
            frontend_photos_dir = os.path.join(settings.BASE_DIR, 'youyou_SongList_frontend', 'photos')
            os.makedirs(frontend_photos_dir, exist_ok=True)
            
            # 保存文件，文件名为position值
            filename = f"{obj.position}.png"
            file_path = os.path.join(frontend_photos_dir, filename)
            
            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 同时复制到public目录
            public_dir = os.path.join(settings.BASE_DIR, 'youyou_SongList_frontend', 'public')
            os.makedirs(public_dir, exist_ok=True)
            public_file_path = os.path.join(public_dir, filename)
            with open(file_path, 'rb') as src, open(public_file_path, 'wb') as dst:
                dst.write(src.read())
            
            # 更新photoURL字段为相对于项目根目录的路径
            relative_path = os.path.relpath(file_path, settings.BASE_DIR)
            obj.photoURL = f"/{relative_path.replace(os.sep, '/')}"
        
        super().save_model(request, obj, form, change)