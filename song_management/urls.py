"""
URL 配置
"""
from django.urls import path
from .api.views import (
    SongListView,
    SongRecordListView,
    style_list_api,
    tag_list_api,
    top_songs_api,
    random_song_api,
)

app_name = 'song_management'

urlpatterns = [
    # 歌曲相关
    path('api/songs/', SongListView.as_view(), name='song-list'),
    path('api/songs/<int:song_id>/records/', SongRecordListView.as_view(), name='song-record-list'),
    
    # 曲风和标签
    path('api/styles/', style_list_api, name='style-list'),
    path('api/tags/', tag_list_api, name='tag-list'),
    
    # 排行榜和随机
    path('api/top_songs/', top_songs_api, name='top-songs'),
    path('api/random-song/', random_song_api, name='random-song'),
]
