"""
Song Management 服务层
"""
from .song_service import SongService
from .song_record_service import SongRecordService
from .ranking_service import RankingService

__all__ = [
    'SongService',
    'SongRecordService',
    'RankingService',
]