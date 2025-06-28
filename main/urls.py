from django.urls import path,include
from . import views
from .views import song_list_api, top_songs_api, is_mobile_api
urlpatterns = [
    # path('',views.index, name="index")
    path("",views.songs_list,name="歌单"),
    path('api/songs/<int:song_id>/records',views.song_records_api,name= "song_records_api"),
    path("api/songs",song_list_api),
    path('api/styles', views.style_list_api),
    path('api/top_songs', top_songs_api),
    path('api/is_mobile/', is_mobile_api),
]
