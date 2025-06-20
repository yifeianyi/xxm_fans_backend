from django.urls import path,include
from . import views

urlpatterns = [
    # path('',views.index, name="index")
    path("",views.songs_list,name="歌单"),
    path('song/<int:song_id>/records',views.song_records_api,name= "song_records_api")
]
