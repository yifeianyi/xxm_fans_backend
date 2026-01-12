"""
Song Management 应用测试
"""
from .test_song_service import SongServiceTest
from .test_song_record_service import SongRecordServiceTest
from .test_ranking_service import RankingServiceTest
from .test_views import SongManagementViewTest
from .test_admin import (
    SongAdminTest,
    SongRecordAdminTest,
    StyleAdminTest,
    SongStyleAdminTest,
    TagAdminTest,
    SongTagAdminTest,
    AdminIntegrationTest
)

__all__ = [
    'SongServiceTest',
    'SongRecordServiceTest',
    'RankingServiceTest',
    'SongManagementViewTest',
    'SongAdminTest',
    'SongRecordAdminTest',
    'StyleAdminTest',
    'SongStyleAdminTest',
    'TagAdminTest',
    'SongTagAdminTest',
    'AdminIntegrationTest',
]