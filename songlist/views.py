from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting
import json
import random


# 歌手配置字典（包含模型和中文名称）
ARTIST_CONFIG = {
    'youyou': {
        'song_model': YouyouSong,
        'setting_model': YouyouSiteSetting,
        'name': '乐游',
    },
    'bingjie': {
        'song_model': BingjieSong,
        'setting_model': BingjieSiteSetting,
        'name': '冰洁',
    },
}


def get_artist_model(artist, model_type='song'):
    """根据歌手标识获取对应的模型"""
    if artist in ARTIST_CONFIG:
        return ARTIST_CONFIG[artist][f'{model_type}_model']
    return None


def get_all_songs():
    """获取所有歌手的歌曲"""
    all_songs = []
    for artist_config in ARTIST_CONFIG.values():
        all_songs.extend(list(artist_config['song_model'].objects.all()))
    return all_songs


def get_all_settings():
    """获取所有歌手的设置"""
    all_settings = []
    for artist_config in ARTIST_CONFIG.values():
        all_settings.extend(list(artist_config['setting_model'].objects.all().values()))
    return all_settings


def song_list(request):
    """歌曲列表API - 支持按歌手筛选"""
    if request.method == 'GET':
        # 获取查询参数
        artist = request.GET.get('artist', '')
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')

        # 根据歌手选择对应的模型
        song_model = get_artist_model(artist, 'song')

        if song_model:
            songs = song_model.objects.all()
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
        else:
            # 如果没有指定歌手，返回所有数据（合并所有表）
            songs = get_all_songs()
            # 应用筛选
            if language:
                songs = [s for s in songs if s.language == language]
            if style:
                songs = [s for s in songs if s.style == style]
            if search:
                songs = [s for s in songs if search.lower() in s.song_name.lower() or search.lower() in s.singer.lower()]
            return JsonResponse([{
                'id': s.id,
                'song_name': s.song_name,
                'singer': s.singer,
                'language': s.language,
                'style': s.style,
                'note': s.note,
            } for s in songs], safe=False)


def language_list(request):
    """获取所有语言列表 - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        song_model = get_artist_model(artist, 'song')

        if song_model:
            songs = song_model.objects.exclude(language='')
            languages = songs.values_list('language', flat=True).distinct()
            return JsonResponse(list(languages), safe=False)
        else:
            # 合并所有表的语言
            all_languages = set()
            for artist_config in ARTIST_CONFIG.values():
                languages = set(artist_config['song_model'].objects.exclude(language='').values_list('language', flat=True))
                all_languages.update(languages)
            return JsonResponse(list(all_languages), safe=False)


def style_list(request):
    """获取所有曲风列表 - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        song_model = get_artist_model(artist, 'song')

        if song_model:
            songs = song_model.objects.exclude(style='')
            styles = songs.values_list('style', flat=True).distinct()
            return JsonResponse(list(styles), safe=False)
        else:
            # 合并所有表的曲风
            all_styles = set()
            for artist_config in ARTIST_CONFIG.values():
                styles = set(artist_config['song_model'].objects.exclude(style='').values_list('style', flat=True))
                all_styles.update(styles)
            return JsonResponse(list(all_styles), safe=False)


def random_song(request):
    """获取随机歌曲 - 支持按歌手筛选"""
    if request.method == 'GET':
        # 获取查询参数
        artist = request.GET.get('artist', '')
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')

        song_model = get_artist_model(artist, 'song')

        if song_model:
            songs = song_model.objects.all()
            # 应用筛选条件
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
        else:
            # 如果没有指定歌手，从所有表中随机选择
            all_songs = get_all_songs()
            # 应用筛选
            if language:
                all_songs = [s for s in all_songs if s.language == language]
            if style:
                all_songs = [s for s in all_songs if s.style == style]
            if search:
                all_songs = [s for s in all_songs if search.lower() in s.song_name.lower() or search.lower() in s.singer.lower()]

            if not all_songs:
                return JsonResponse({'error': 'No songs available.'}, status=404)

            random_song = random.choice(all_songs)
            song_data = {
                'id': random_song.id,
                'song_name': random_song.song_name,
                'language': random_song.language,
                'singer': random_song.singer,
                'style': random_song.style,
                'note': random_song.note,
            }
            return JsonResponse(song_data)

            random_song = random.choice(all_songs)
            song_data = {
                'id': random_song.id,
                'song_name': random_song.song_name,
                'language': random_song.language,
                'singer': random_song.singer,
                'style': random_song.style,
                'note': random_song.note,
            }
            return JsonResponse(song_data)

        # 应用筛选条件
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


def get_artist_info(request):
    """获取歌手信息（包括中文名称）"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        if artist in ARTIST_CONFIG:
            artist_info = {
                'key': artist,
                'name': ARTIST_CONFIG[artist]['name'],
            }
            return JsonResponse(artist_info)
        else:
            return JsonResponse({'error': 'Artist not found'}, status=404)


def site_settings(request):
    """网站设置API - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        setting_model = get_artist_model(artist, 'setting')

        if setting_model:
            settings = setting_model.objects.all().values()
            # 简化photo_url，只返回文件名
            updated_settings = []
            for setting in settings:
                if '/' in setting['photo_url']:
                    filename = setting['photo_url'].split('/')[-1]
                    setting['photo_url'] = filename
                updated_settings.append(setting)
            return JsonResponse(updated_settings, safe=False)
        else:
            # 合并所有表的设置
            all_settings = get_all_settings()
            # 简化photo_url，只返回文件名
            updated_settings = []
            for setting in all_settings:
                if '/' in setting['photo_url']:
                    filename = setting['photo_url'].split('/')[-1]
                    setting['photo_url'] = filename
                updated_settings.append(setting)
            return JsonResponse(updated_settings, safe=False)


def favicon(request):
    """获取favicon - 支持按歌手筛选"""
    artist = request.GET.get('artist', '')

    setting_model = get_artist_model(artist, 'setting')

    # 获取position为1的设置作为favicon
    try:
        if setting_model:
            setting = setting_model.objects.get(position=1)
        else:
            # 默认使用第一个歌手的设置
            setting_model = get_artist_model(list(ARTIST_CONFIG.keys())[0], 'setting')
            setting = setting_model.objects.get(position=1)

        # 重定向到对应的图片文件，前端统一使用/photos/前缀
        from django.shortcuts import redirect
        filename = setting.photo_url
        if '/' in filename:
            filename = filename.split('/')[-1]
        photo_url = 'songlist_frontend/photos/' + filename
        return redirect(photo_url)
    except Exception:
        # 如果没有找到position为1的设置，返回默认favicon
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/vite.svg')