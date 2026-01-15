"""
排行榜服务
"""
from typing import List
from datetime import datetime, timedelta
from django.db.models import Count
from core.cache import cache_result
from ..models import Song


class RankingService:
    """排行榜服务类"""

    @staticmethod
    @cache_result(timeout=300, key_prefix="top_songs")
    def get_top_songs(range_key: str = 'all', limit: int = 10) -> List[dict]:
        """
        获取热门歌曲排行榜

        Args:
            range_key: 时间范围
                - 'all': 全部时间
                - '1m': 最近1个月
                - '3m': 最近3个月
                - '1y': 最近1年
                - '10d': 最近10天
                - '20d': 最近20天
                - '30d': 最近30天
            limit: 返回数量

        Returns:
            热门歌曲列表
        """
        # 时间范围映射
        range_map = {
            'all': None,
            '1m': 30,
            '3m': 90,
            '1y': 365,
            '10d': 10,
            '20d': 20,
            '30d': 30,
        }

        days = range_map.get(range_key, None)
        queryset = Song.objects.all()

        # 按时间范围筛选
        if days:
            since = datetime.now().date() - timedelta(days=days)
            queryset = queryset.filter(records__performed_at__gte=since)

        # 统计演唱次数并排序
        queryset = queryset.annotate(
            recent_count=Count('records')
        ).order_by('-recent_count', '-last_performed')[:limit]

        # 构建结果
        result = []
        for song in queryset:
            result.append({
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': song.recent_count,
                'last_performed': song.last_performed,
            })

        return result

    @staticmethod
    def get_most_performed_songs(limit: int = 10) -> List[dict]:
        """
        获取演唱次数最多的歌曲

        Args:
            limit: 返回数量

        Returns:
            歌曲列表
        """
        queryset = Song.objects.all().order_by('-perform_count')[:limit]

        result = []
        for song in queryset:
            result.append({
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': song.perform_count,
                'last_performed': song.last_performed,
            })

        return result

    @staticmethod
    def get_recently_performed_songs(limit: int = 10) -> List[dict]:
        """
        获取最近演唱的歌曲

        Args:
            limit: 返回数量

        Returns:
            歌曲列表
        """
        queryset = Song.objects.all().order_by('-last_performed')[:limit]

        result = []
        for song in queryset:
            result.append({
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': song.perform_count,
                'last_performed': song.last_performed,
            })

        return result