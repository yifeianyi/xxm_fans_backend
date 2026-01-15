"""
歌曲服务
"""
from typing import List, Optional
from django.db.models import Q
from django.core.cache import cache
from core.cache import cache_result
from core.exceptions import SongNotFoundException, InvalidParameterException
from ..models import Song


class SongService:
    """歌曲服务类"""

    @staticmethod
    def get_songs(
        query: Optional[str] = None,
        language: Optional[str] = None,
        styles: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        ordering: Optional[str] = None
    ) -> List[Song]:
        """
        获取歌曲列表，支持筛选和排序

        Args:
            query: 搜索关键词（歌名或歌手）
            language: 语言筛选
            styles: 曲风列表
            tags: 标签列表
            ordering: 排序字段

        Returns:
            歌曲列表
        """
        queryset = Song.objects.all()

        # 搜索
        if query:
            queryset = queryset.filter(
                Q(song_name__icontains=query) | Q(singer__icontains=query)
            )

        # 语言筛选
        if language:
            languages = language.split(',')
            languages = [lang.strip() for lang in languages if lang.strip()]
            if languages:
                queryset = queryset.filter(language__in=languages)

        # 曲风筛选
        if styles:
            style_filter = Q()
            for style in styles:
                style_filter |= Q(song_styles__style__name=style)
            queryset = queryset.filter(style_filter).distinct()

        # 标签筛选
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(song_tags__tag__name=tag)
            queryset = queryset.filter(tag_filter).distinct()

        # 排序
        if ordering:
            queryset = queryset.order_by(ordering)

        return list(queryset)

    @staticmethod
    @cache_result(timeout=600, key_prefix="song_detail")
    def get_song_by_id(song_id: int) -> Song:
        """
        根据 ID 获取歌曲

        Args:
            song_id: 歌曲 ID

        Returns:
            歌曲对象

        Raises:
            SongNotFoundException: 歌曲不存在
        """
        try:
            return Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            raise SongNotFoundException(f"歌曲 ID {song_id} 不存在")

    @staticmethod
    @cache_result(timeout=300, key_prefix="random_song")
    def get_random_song() -> Optional[Song]:
        """
        获取随机歌曲

        Returns:
            随机歌曲，如果没有歌曲则返回 None
        """
        return Song.objects.order_by('?').first()

    @staticmethod
    def get_all_languages() -> List[str]:
        """
        获取所有语言列表

        Returns:
            语言列表
        """
        languages = Song.objects.exclude(language='').values_list('language', flat=True).distinct()
        return list(set(languages))

    @staticmethod
    def get_song_count() -> int:
        """
        获取歌曲总数

        Returns:
            歌曲总数
        """
        return Song.objects.count()