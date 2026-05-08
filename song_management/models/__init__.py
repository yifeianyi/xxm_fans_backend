"""
Song Management 模型
"""
from .song import Song, SongRecord
from .style import Style, SongStyle
from .tag import Tag, SongTag
from .original_work import OriginalWork
from .like import SongRecordLike

from . import signals

__all__ = [
    'Song',
    'SongRecord',
    'Style',
    'SongStyle',
    'Tag',
    'SongTag',
    'OriginalWork',
    'SongRecordLike',
]