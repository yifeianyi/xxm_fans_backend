from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import you_Songs, you_site_setting
import json
import random

# Create your views here.
def song_list(request):
    if request.method == 'GET':
        # 获取查询参数
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')
        
        # 构建查询
        songs = you_Songs.objects.all()
        
        # 语言筛选
        if language:
            songs = songs.filter(language=language)
            
        # 曲风筛选
        if style:
            songs = songs.filter(style=style)
            
        # 搜索功能（歌名或歌手）
        if search:
            songs = songs.filter(
                Q(song_name__icontains=search) | Q(singer__icontains=search)
            )
            
        songs = songs.values()
        return JsonResponse(list(songs), safe=False)


def get_languages(request):
    """获取所有语言列表"""
    if request.method == 'GET':
        languages = you_Songs.objects.exclude(language='').values_list('language', flat=True).distinct()
        return JsonResponse(list(languages), safe=False)


def get_styles(request):
    """获取所有曲风列表"""
    if request.method == 'GET':
        styles = you_Songs.objects.exclude(style='').values_list('style', flat=True).distinct()
        return JsonResponse(list(styles), safe=False)


def get_random_song(request):
    """获取随机歌曲"""
    if request.method == 'GET':
        # 获取所有歌曲
        songs = you_Songs.objects.all()
        
        # 如果有筛选条件，应用筛选
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')
        
        if language:
            songs = songs.filter(language=language)
        if style:
            songs = songs.filter(style=style)
        if search:
            songs = songs.filter(
                Q(song_name__icontains=search) | Q(singer__icontains=search)
            )
        
        # 如果没有符合条件的歌曲，返回404
        if not songs.exists():
            return JsonResponse({'error': 'No songs available.'}, status=404)
        
        # 随机选择一首歌曲
        random_song = random.choice(songs)
        
        # 返回歌曲信息
        song_data = {
            'id': random_song.id,
            'song_name': random_song.song_name,
            'language': random_song.language,
            'singer': random_song.singer,
            'style': random_song.style,
            'note': random_song.note,
        }
        
        return JsonResponse(song_data)


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