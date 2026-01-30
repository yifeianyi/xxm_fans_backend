"""
API 视图 - 索引文件
"""
from django.http import HttpResponse

# 导入所有视图
from .song_views import SongListView
from .record_views import SongRecordListView
from .other_views import style_list_api, tag_list_api, top_songs_api, random_song_api
from .original_work_views import original_works_list_api

# 导出所有视图
__all__ = [
    'SongListView',
    'SongRecordListView',
    'style_list_api',
    'tag_list_api',
    'top_songs_api',
    'random_song_api',
    'original_works_list_api',
]


def index(request):
    """默认视图"""
    return HttpResponse("Hello, world. You're at the song_management index.")
