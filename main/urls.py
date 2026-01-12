from django.urls import path, include
from . import views
from .views import SongListView, SongRecordListView, top_songs_api, style_list_api, tag_list_api, random_song_api
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('api/songs/', SongListView.as_view(), name='song-list'),
    path('api/songs/<int:song_id>/records/', SongRecordListView.as_view(), name='song-record-list'),
    path('api/styles/', style_list_api, name='style-list'),
    path('api/tags/', tag_list_api, name='tag-list'),
    path('api/top_songs/', top_songs_api, name='top-songs'),
    path('api/random-song/', random_song_api, name='random-song'),
]
