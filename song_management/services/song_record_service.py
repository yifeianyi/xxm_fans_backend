"""
演唱记录服务
"""
from typing import List
from django.core.paginator import Paginator
from core.cache import cache_result
from core.exceptions import SongNotFoundException
from ..models import Song, SongRecord


class SongRecordService:
    """演唱记录服务类"""

    @staticmethod
    @cache_result(timeout=600, key_prefix="song_records")
    def get_records_by_song(
        song_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """
        获取指定歌曲的演唱记录（分页）

        Args:
            song_id: 歌曲 ID
            page: 页码
            page_size: 每页数量

        Returns:
            分页数据字典，包含 total, page, page_size, results

        Raises:
            SongNotFoundException: 歌曲不存在
        """
        # 验证歌曲是否存在
        try:
            Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            raise SongNotFoundException(f"歌曲 ID {song_id} 不存在")

        # 获取演唱记录
        queryset = SongRecord.objects.filter(song_id=song_id).order_by('-performed_at')

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # 处理封面 URL
        results = []
        for record in page_obj:
            record_data = {
                'id': record.id,
                'song_id': record.song_id,
                'performed_at': record.performed_at,
                'url': record.url,
                'notes': record.notes,
                'cover_url': record.cover_url,
            }

            # 如果没有封面，生成默认封面路径
            if not record.cover_url and record.performed_at:
                date = record.performed_at
                record_data['cover_url'] = f"/covers/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%Y-%m-%d')}.jpg"

            results.append(record_data)

        return {
            'total': paginator.count,
            'page': page_obj.number,
            'page_size': page_size,
            'results': results
        }

    @staticmethod
    def get_record_count_by_song(song_id: int) -> int:
        """
        获取指定歌曲的演唱记录数量

        Args:
            song_id: 歌曲 ID

        Returns:
            演唱记录数量
        """
        return SongRecord.objects.filter(song_id=song_id).count()

    @staticmethod
    def get_latest_record(song_id: int):
        """
        获取指定歌曲的最新演唱记录

        Args:
            song_id: 歌曲 ID

        Returns:
            最新演唱记录，如果没有则返回 None
        """
        return SongRecord.objects.filter(song_id=song_id).order_by('-performed_at').first()