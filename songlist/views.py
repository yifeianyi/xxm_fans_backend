from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting
import json
import random


def song_list(request):
    """歌曲列表API - 支持按歌手筛选"""
    if request.method == 'GET':
        # 获取查询参数
        artist = request.GET.get('artist', '')
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')

        # 根据歌手选择对应的模型
        if artist == 'youyou':
            songs = YouyouSong.objects.all()
        elif artist == 'bingjie':
            songs = BingjieSong.objects.all()
        else:
            # 如果没有指定歌手，返回所有数据（合并两个表）
            youyou_songs = YouyouSong.objects.all()
            bingjie_songs = BingjieSong.objects.all()
            songs = list(youyou_songs) + list(bingjie_songs)
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
    """获取所有语言列表 - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        # 根据歌手选择对应的模型
        if artist == 'youyou':
            songs = YouyouSong.objects.exclude(language='')
        elif artist == 'bingjie':
            songs = BingjieSong.objects.exclude(language='')
        else:
            # 合并两个表的语言
            youyou_languages = set(YouyouSong.objects.exclude(language='').values_list('language', flat=True))
            bingjie_languages = set(BingjieSong.objects.exclude(language='').values_list('language', flat=True))
            languages = youyou_languages.union(bingjie_languages)
            return JsonResponse(list(languages), safe=False)

        languages = songs.values_list('language', flat=True).distinct()
        return JsonResponse(list(languages), safe=False)


def style_list(request):
    """获取所有曲风列表 - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        # 根据歌手选择对应的模型
        if artist == 'youyou':
            songs = YouyouSong.objects.exclude(style='')
        elif artist == 'bingjie':
            songs = BingjieSong.objects.exclude(style='')
        else:
            # 合并两个表的曲风
            youyou_styles = set(YouyouSong.objects.exclude(style='').values_list('style', flat=True))
            bingjie_styles = set(BingjieSong.objects.exclude(style='').values_list('style', flat=True))
            styles = youyou_styles.union(bingjie_styles)
            return JsonResponse(list(styles), safe=False)

        styles = songs.values_list('style', flat=True).distinct()
        return JsonResponse(list(styles), safe=False)


def random_song(request):
    """获取随机歌曲 - 支持按歌手筛选"""
    if request.method == 'GET':
        # 获取查询参数
        artist = request.GET.get('artist', '')
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')

        # 根据歌手选择对应的模型
        if artist == 'youyou':
            songs = YouyouSong.objects.all()
        elif artist == 'bingjie':
            songs = BingjieSong.objects.all()
        else:
            # 如果没有指定歌手，从两个表中随机选择
            all_songs = list(YouyouSong.objects.all()) + list(BingjieSong.objects.all())
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


def site_settings(request):
    """网站设置API - 支持按歌手筛选"""
    if request.method == 'GET':
        artist = request.GET.get('artist', '')

        # 根据歌手选择对应的模型
        if artist == 'youyou':
            settings = YouyouSiteSetting.objects.all()
        elif artist == 'bingjie':
            settings = BingjieSiteSetting.objects.all()
        else:
            # 合并两个表的设置
            youyou_settings = YouyouSiteSetting.objects.all().values()
            bingjie_settings = BingjieSiteSetting.objects.all().values()
            settings = list(youyou_settings) + list(bingjie_settings)
            # 简化photo_url，只返回文件名
            updated_settings = []
            for setting in settings:
                if '/' in setting['photo_url']:
                    filename = setting['photo_url'].split('/')[-1]
                    setting['photo_url'] = filename
                updated_settings.append(setting)
            return JsonResponse(updated_settings, safe=False)

        settings = settings.values()
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
    """获取favicon - 支持按歌手筛选"""
    artist = request.GET.get('artist', '')
    # 获取position为1的设置作为favicon
    try:
        if artist == 'youyou':
            setting = YouyouSiteSetting.objects.get(position=1)
        elif artist == 'bingjie':
            setting = BingjieSiteSetting.objects.get(position=1)
        else:
            # 默认使用乐游的设置
            setting = YouyouSiteSetting.objects.get(position=1)
        # 重定向到对应的图片文件，前端统一使用/photos/前缀
        from django.shortcuts import redirect
        filename = setting.photo_url
        if '/' in filename:
            filename = filename.split('/')[-1]
        photo_url = 'songlist_frontend/photos/' + filename
        return redirect(photo_url)
    except (YouyouSiteSetting.DoesNotExist, BingjieSiteSetting.DoesNotExist):
        # 如果没有找到position为1的设置，返回默认favicon
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/vite.svg')