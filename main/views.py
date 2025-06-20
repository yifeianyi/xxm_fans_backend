from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Songs
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
        records = song.records.order_by("-performed_at").values("performed_at", "url", "notes")
        return JsonResponse(list(records), safe=False)
    except Songs.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)