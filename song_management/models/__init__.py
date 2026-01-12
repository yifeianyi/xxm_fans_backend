"""
Song Management 模型
"""
from .song import Song, SongRecord
from .style import Style, SongStyle
from .tag import Tag, SongTag

__all__ = [
    'Song',
    'SongRecord',
    'Style',
    'SongStyle',
    'Tag',
    'SongTag',
]