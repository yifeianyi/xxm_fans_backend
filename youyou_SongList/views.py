from django.shortcuts import render
from django.http import JsonResponse
from .models import you_Songs, you_site_setting
import json

# Create your views here.
def song_list(request):
    if request.method == 'GET':
        songs = you_Songs.objects.all().values()
        return JsonResponse(list(songs), safe=False)


def site_settings(request):
    if request.method == 'GET':
        settings = you_site_setting.objects.all().values()
        # 修改photoURL，添加photos/前缀
        updated_settings = []
        for setting in settings:
            # 如果photoURL不以photos/开头，则添加前缀
            if not setting['photoURL'].startswith('photos/'):
                setting['photoURL'] = 'photos/' + setting['photoURL']
            updated_settings.append(setting)
        return JsonResponse(updated_settings, safe=False)


def favicon(request):
    # 获取position为1的设置作为favicon
    try:
        setting = you_site_setting.objects.get(position=1)
        # 重定向到对应的图片文件，确保URL有photos/前缀
        from django.shortcuts import redirect
        photo_url = setting.photoURL
        if not photo_url.startswith('photos/'):
            photo_url = 'photos/' + photo_url
        return redirect(photo_url)
    except you_site_setting.DoesNotExist:
        # 如果没有找到position为1的设置，返回默认favicon
        from django.http import HttpResponse
        return HttpResponse(status=404)