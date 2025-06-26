from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Songs, SongStyle, Style
from django.shortcuts import render
from datetime import datetime, timedelta
from django.db.models import Count

# Create your views here.

def index(request):
    print("Index view called!")
    return HttpResponse("hello world")

def songs_list(request):
    query = request.GET.get("q","")
    songs = Songs.objects.all().order_by("-perform_count")

    if query:
        songs = songs.filter(song_name__icontains=query)

    paginator = Paginator(songs, 50)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    # return render(request, "songs_list.html",{"songs":songs})
    return render(request, "songs_list.html", {"page_obj":page_obj})

def song_records_api(request, song_id):
    try:
        song = Songs.objects.get(id = song_id)
        records = song.records.order_by("-performed_at").values("performed_at", "url", "notes","cover_url")
        return JsonResponse(list(records), safe=False)
    except Songs.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)
    

from rest_framework.decorators import api_view
from rest_framework.response import Response
@api_view(['GET'])
def song_list_api(request):
    query = request.GET.get("q", "")
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("limit", 50)
    ordering = request.GET.get("ordering", "")
    # ✅ 获取 styles 参数
    style_list = request.GET.getlist("styles")
    if not style_list:
        style_raw = request.GET.get("styles")
        if style_raw:
            style_list = style_raw.split(",")
    style_list = [s for s in style_list if s.strip()]
    # ✅ 基础查询
    songs = Songs.objects.all()
    # ✅ 排序处理
    allowed_order_fields = ['singer', 'last_performed', 'perform_count']
    if ordering:
        field = ordering.lstrip('-')
        if field in allowed_order_fields:
            songs = songs.order_by(ordering)
        else:
            songs = songs.order_by('-last_performed')
    else:
        songs = songs.order_by('-last_performed')
    if query:
        songs = songs.filter(song_name__icontains=query)
    if style_list:
        songs = songs.filter(songstyle__style__name__in=style_list).distinct()
    # 分页处理
    paginator = Paginator(songs, page_size)
    page = paginator.get_page(page_num)
    results = []
    for song in page.object_list:
        styles = [s.style.name for s in SongStyle.objects.filter(song=song)]
        results.append({
            "id": song.id,
            "song_name": song.song_name,
            "singer": song.singer,
            "styles": styles,
            "last_performed": song.last_performed,
            "perform_count": song.perform_count,
        })
    return Response({
        "total": paginator.count,
        "page": page.number,
        "page_size": paginator.per_page,
        "results": results
    })

@api_view(['GET'])
def style_list_api(request):
    styles = Style.objects.all().values_list("name", flat=True)
    return Response(list(styles))

@api_view(['GET'])
def top_songs_api(request):
    range_map = {
        'all': None,
        '1m': 30,
        '3m': 90,
        '1y': 365,
        '10d': 10,
        '20d': 20,
        '30d': 30,
    }
    range_key = request.GET.get('range', 'all')
    days = range_map.get(range_key, None)
    qs = Songs.objects.all()
    if days:
        since = datetime.now().date() - timedelta(days=days)
        qs = qs.filter(records__performed_at__gte=since)
    # annotate 统计演唱次数
    qs = qs.annotate(recent_count=Count('records')).order_by('-recent_count', '-last_performed')[:10]
    result = [
        {
            'id': s.id,
            'song_name': s.song_name,
            'singer': s.singer,
            'perform_count': s.recent_count,
            'last_performed': s.last_performed,
        }
        for s in qs
    ]
    return Response(result)
