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
        return JsonResponse(list(settings), safe=False)