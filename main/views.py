from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Songs, SongStyle, Style
from django.shortcuts import render
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.core.cache import cache
from .utils import is_mobile

# Create your views here.

def index(request):
    print("Index view called!")
    return HttpResponse("hello world")

def songs_list(request):
    query = request.GET.get("q","")
    songs = Songs.objects.all().order_by("-perform_count")

    if query:
        songs = songs.filter(
            song_name__icontains=query
        ) | songs.filter(
            singer__icontains=query
        )

    paginator = Paginator(songs, 50)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    # return render(request, "songs_list.html",{"songs":songs})
    return render(request, "songs_list.html", {"page_obj": page_obj, "query": query})

def song_records_api(request, song_id):
    page_num = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))
    cache_key = f"song_records:{song_id}:{page_num}:{page_size}"
    records = cache.get(cache_key)

    if records is not None:
        return JsonResponse(records, safe=False)

    try:
        song = Songs.objects.get(id=song_id)
        raw_records = song.records.order_by("-performed_at").values("performed_at", "url", "notes", "cover_url")
        paginator = Paginator(raw_records, page_size)
        page = paginator.get_page(page_num)
        results = []
        for r in page.object_list:
            if r["performed_at"]:
                date = r["performed_at"]
                date_str = date.strftime("%Y-%m-%d")
                year = date.strftime("%Y")
                month = date.strftime("%m")
                r["cover_url"] = r.get("cover_url") or f"/covers/{year}/{month}/{date_str}.jpg"
            else:
                r["cover_url"] = "/covers/default.jpg"
            results.append(r)
        data = {
            "total": paginator.count,
            "page": page.number,
            "page_size": paginator.per_page,
            "results": results
        }
        cache.set(cache_key, data, 600)
        return JsonResponse(data, safe=False)
    except Songs.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)


# def song_records_api(request, song_id):
#     cache_key = f"song_records:{song_id}"
#     records = cache.get(cache_key)
    
#     if records is not None:
#         return JsonResponse(records, safe=False)
    
#     try:
#         song = Songs.objects.get(id=song_id)
#         records = list(song.records.order_by("-performed_at").values("performed_at", "url", "notes", "cover_url"))
#         cache.set(cache_key, records, 600)  # 缓存 10 分钟
#         return JsonResponse(records, safe=False)
#     except Songs.DoesNotExist:
#         return JsonResponse({"error": "Song not found."}, status=404)    

from rest_framework.decorators import api_view
from rest_framework.response import Response
@api_view(['GET'])
def song_list_api(request):
    query = request.GET.get("q", "")
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("limit", 50)
    ordering = request.GET.get("ordering", "")
    style_list = request.GET.getlist("styles")
    if not style_list:
        style_raw = request.GET.get("styles")
        if style_raw:
            style_list = style_raw.split(",")
    style_list = [s for s in style_list if s.strip()]
    # 构造缓存key，包含所有查询参数
    cache_key = f"song_list_api:{query}:{page_num}:{page_size}:{ordering}:{'-'.join(style_list)}"
    data = cache.get(cache_key)
    if data is not None:
        return Response(data)
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
        songs = songs.filter(Q(song_name__icontains=query) | Q(singer__icontains=query))
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
            "language": song.language,
        })
    data = {
        "total": paginator.count,
        "page": page.number,
        "page_size": paginator.per_page,
        "results": results
    }
    cache.set(cache_key, data, 600)  # 缓存10分钟
    return Response(data)

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
    limit = int(request.GET.get('limit', 10))  # 新增limit参数，默认10
    qs = Songs.objects.all()
    if days:
        since = datetime.now().date() - timedelta(days=days)
        qs = qs.filter(records__performed_at__gte=since)
    # annotate 统计演唱次数
    qs = qs.annotate(recent_count=Count('records')).order_by('-recent_count', '-last_performed')[:limit]
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

@api_view(['GET'])
def is_mobile_api(request):
    return Response({'is_mobile': is_mobile(request)})
