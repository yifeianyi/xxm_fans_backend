"""
Song Management API
"""
from .serializers import (
    SongSerializer,
    SongRecordSerializer,
    StyleSerializer,
    TagSerializer,
)
from .views import (
    SongListView,
    SongDetailView,
    SongRecordListView,
    StyleListView,
    TagListView,
    TopSongsView,
    RandomSongView,
    LanguageListView,
)

__all__ = [
    'SongSerializer',
    'SongRecordSerializer',
    'StyleSerializer',
    'TagSerializer',
    'SongListView',
    'SongDetailView',
    'SongRecordListView',
    'StyleListView',
    'TagListView',
    'TopSongsView',
    'RandomSongView',
    'LanguageListView',
]