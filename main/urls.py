from django.urls import path, include
from . import views
from .views import SongListView, SongRecordListView, StyleListView, top_songs_api, is_mobile_api

urlpatterns = [
    path('', views.index, name='index'),
    path('api/songs/', SongListView.as_view(), name='song-list'),
    path('api/songs/<int:song_id>/records/', SongRecordListView.as_view(), name='song-record-list'),
    path('api/styles/', StyleListView.as_view(), name='style-list'),
    path('api/top_songs/', top_songs_api, name='top-songs'),
    path('api/is_mobile/', is_mobile_api, name='is-mobile'),
]
