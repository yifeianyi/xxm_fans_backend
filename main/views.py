from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Songs, SongStyle, Style
from django.shortcuts import render

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

    # ✅ 获取 styles 参数（支持 ?styles=民谣&styles=流行 和 ?styles=民谣,流行 两种格式）
    style_list = request.GET.getlist("styles")
    if not style_list:
        style_raw = request.GET.get("styles")
        if style_raw:
            style_list = style_raw.split(",")
    # ✅ 清除空字符串
    style_list = [s for s in style_list if s.strip()]
    # ✅ 基础查询
    songs = Songs.objects.all().order_by("-last_performed")

    if query:
        songs = songs.filter(song_name__icontains=query)

    if style_list:
        songs = songs.filter(songstyle__style__name__in=style_list).distinct()

    # ✅ 分页处理
    paginator = Paginator(songs, page_size)
    page = paginator.get_page(page_num)

    # ✅ 构造响应数据
    results = []
    for song in page.object_list:
        styles = [s.style.name for s in SongStyle.objects.filter(song=song)]
        results.append({
            "id": song.id,
            "song_name": song.song_name,
            "singer": song.singer,
            "last_performed": song.last_performed,
            "perform_count": song.perform_count,
            "styles": styles,
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
