"""
Song Management 应用测试
"""
from .test_views import (
    SongListCacheTest,
    TopSongsQueryTest,
    SongRecordErrorHandlingTest,
)
from .test_serializers import SongSerializerTest
from .test_models import SongModelIndexTest, SongRecordIndexDocsTest
from .test_likes import (
    ToggleLikeTest,
    LikeStatusTest,
    RateLimitTest,
    RecordListViewLikeDataTest,
    ToggleLikeInvalidInputTest,
)

__all__ = [
    'SongListCacheTest',
    'TopSongsQueryTest',
    'SongRecordErrorHandlingTest',
    'SongSerializerTest',
    'SongModelIndexTest',
    'SongRecordIndexDocsTest',
    'ToggleLikeTest',
    'LikeStatusTest',
    'RateLimitTest',
    'RecordListViewLikeDataTest',
    'ToggleLikeInvalidInputTest',
]
