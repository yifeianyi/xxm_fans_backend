from django.urls import path, include
from . import views
from .views import SongListView, SongRecordListView, top_songs_api, is_mobile_api, style_list_api, random_song_api, recommendation_api

urlpatterns = [
    path('', views.index, name='index'),
    path('api/songs/', SongListView.as_view(), name='song-list'),
    path('api/songs/<int:song_id>/records/', SongRecordListView.as_view(), name='song-record-list'),
    path('api/styles/', style_list_api, name='style-list'),
    path('api/top_songs/', top_songs_api, name='top-songs'),
    path('api/is_mobile/', is_mobile_api, name='is-mobile'),
    path('api/random-song/', random_song_api, name='random-song'),
    path('api/recommendation/', recommendation_api, name='recommendation'),
]
