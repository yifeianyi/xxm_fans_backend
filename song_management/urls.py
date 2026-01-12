"""
URL 配置
"""
from django.urls import path
from .api.views import (
    SongListView,
    SongDetailView,
    SongRecordListView,
    StyleListView,
    TagListView,
    TopSongsView,
    RandomSongView,
    LanguageListView,
)

app_name = 'song_management'

urlpatterns = [
    # 歌曲相关
    path('songs/', SongListView.as_view(), name='song-list'),
    path('songs/<int:song_id>/', SongDetailView.as_view(), name='song-detail'),
    path('songs/<int:song_id>/records/', SongRecordListView.as_view(), name='song-records'),
    
    # 曲风和标签
    path('styles/', StyleListView.as_view(), name='style-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('languages/', LanguageListView, name='language-list'),
    
    # 排行榜和随机
    path('top-songs/', TopSongsView, name='top-songs'),
    path('random-song/', RandomSongView, name='random-song'),
]