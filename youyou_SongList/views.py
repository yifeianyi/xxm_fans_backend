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
        # 简化photoURL，只返回文件名
        updated_settings = []
        for setting in settings:
            # 只返回文件名，前端统一使用/photos/前缀
            if '/' in setting['photoURL']:
                filename = setting['photoURL'].split('/')[-1]
                setting['photoURL'] = filename
            updated_settings.append(setting)
        return JsonResponse(updated_settings, safe=False)


def favicon(request):
    # 获取position为1的设置作为favicon
    try:
        setting = you_site_setting.objects.get(position=1)
        # 重定向到对应的图片文件，前端统一使用/photos/前缀
        from django.shortcuts import redirect
        filename = setting.photoURL
        if '/' in filename:
            filename = filename.split('/')[-1]
        photo_url = 'photos/' + filename
        return redirect(photo_url)
    except you_site_setting.DoesNotExist:
        # 如果没有找到position为1的设置，返回默认favicon
        from django.http import HttpResponse
        return HttpResponse(status=404)