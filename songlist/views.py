from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Song, SiteSetting
import json
import random


def song_list(request):
    """歌曲列表API"""
    if request.method == 'GET':
        # 获取查询参数
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')

        # 构建查询
        songs = Song.objects.all()

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


def language_list(request):
    """获取所有语言列表"""
    if request.method == 'GET':
        languages = Song.objects.exclude(language='').values_list('language', flat=True).distinct()
        return JsonResponse(list(languages), safe=False)


def style_list(request):
    """获取所有曲风列表"""
    if request.method == 'GET':
        styles = Song.objects.exclude(style='').values_list('style', flat=True).distinct()
        return JsonResponse(list(styles), safe=False)


def random_song(request):
    """获取随机歌曲"""
    if request.method == 'GET':
        # 获取所有歌曲
        songs = Song.objects.all()

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
    """网站设置API"""
    if request.method == 'GET':
        settings = SiteSetting.objects.all().values()
        # 简化photo_url，只返回文件名
        updated_settings = []
        for setting in settings:
            # 只返回文件名，前端统一使用/photos/前缀
            if '/' in setting['photo_url']:
                filename = setting['photo_url'].split('/')[-1]
                setting['photo_url'] = filename
            updated_settings.append(setting)
        return JsonResponse(updated_settings, safe=False)


def favicon(request):
    """获取favicon"""
    # 获取position为1的设置作为favicon
    try:
        setting = SiteSetting.objects.get(position=1)
        # 重定向到对应的图片文件，前端统一使用/photos/前缀
        from django.shortcuts import redirect
        filename = setting.photo_url
        if '/' in filename:
            filename = filename.split('/')[-1]
        photo_url = 'songlist_frontend/photos/' + filename
        return redirect(photo_url)
    except SiteSetting.DoesNotExist:
        # 如果没有找到position为1的设置，返回默认favicon
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/vite.svg')