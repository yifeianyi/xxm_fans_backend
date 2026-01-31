from django.db.models import Q
from datetime import datetime
from ..models import Livestream
import json


class LivestreamService:
    """直播数据服务 - 优先使用 Livestream 模型，fallback 到 JSON 文件"""

    # 直播数据 JSON 文件路径（fallback 数据源）
    LIVE_DATA_FILE = '/home/yifeianyi/Desktop/xxm_fans_home/live_final.json'

    @classmethod
    def get_livestreams_by_month(cls, year: int, month: int):
        """
        获取指定月份的所有直播记录

        Args:
            year: 年份
            month: 月份 (1-12)

        Returns:
            List[dict]: 直播记录列表
        """
        livestreams = []

        # 优先从 Livestream 模型获取数据
        db_livestreams = Livestream.objects.filter(
            date__year=year,
            date__month=month,
            is_active=True
        ).order_by('-date')

        if db_livestreams.exists():
            # 使用数据库数据
            for livestream in db_livestreams:
                livestreams.append(livestream.to_dict())
        else:
            # Fallback: 从 JSON 文件加载数据
            livestreams = cls._get_livestreams_from_json(year, month)

        return livestreams

    @classmethod
    def get_livestream_by_date(cls, date_str: str):
        """
        获取指定日期的直播记录

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)

        Returns:
            dict: 直播记录详情，如果不存在返回 None
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

        # 优先从 Livestream 模型获取数据
        try:
            livestream = Livestream.objects.get(date=date_obj, is_active=True)
            return livestream.to_dict()
        except Livestream.DoesNotExist:
            pass

        # Fallback: 从 JSON 文件获取数据
        return cls._get_livestream_from_json(date_str)

    @classmethod
    def _get_livestreams_from_json(cls, year: int, month: int):
        """从 JSON 文件获取指定月份的直播记录"""
        livestreams = []
        live_data = cls._load_live_data()

        month_data = [
            item for item in live_data
            if cls._parse_date(item.get('date', ''))
            and cls._parse_date(item['date']).year == year
            and cls._parse_date(item['date']).month == month
        ]

        for item in month_data:
            date_str = item.get('date', '')
            date_obj = cls._parse_date(date_str)

            if not date_obj:
                continue

            livestream = cls._build_livestream_from_json(date_obj, item)
            if livestream:
                livestreams.append(livestream)

        livestreams.sort(key=lambda x: x['date'], reverse=True)
        return livestreams

    @classmethod
    def _get_livestream_from_json(cls, date_str: str):
        """从 JSON 文件获取指定日期的直播记录"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

        live_data = cls._load_live_data()
        matched_item = None

        for item in live_data:
            if cls._parse_date(item.get('date', '')) == date_obj:
                matched_item = item
                break

        if not matched_item:
            return None

        return cls._build_livestream_from_json(date_obj, matched_item)

    @classmethod
    def _load_live_data(cls):
        """加载 live_final.json 数据"""
        try:
            with open(cls.LIVE_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def _parse_date(cls, date_str: str):
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    @classmethod
    def _build_livestream_from_json(cls, date: datetime.date, live_item: dict):
        """从 JSON 数据构建直播记录"""
        date_str = date.strftime('%Y-%m-%d')

        # 获取当日歌切（演唱记录）
        song_cuts = cls._get_song_cuts_by_date(date)

        # 获取当日截图（从 LiveMoment 目录）
        screenshots = cls._get_screenshots_by_date(date)

        # 使用 live_final.json 中的标题和描述
        title = live_item.get('title', f'{date_str} 直播记录')
        summary = live_item.get('describe', f'{date_str} 的精彩直播时刻')
        duration = live_item.get('duration_formatted', 'N/A')
        bvid = live_item.get('bvid', '')
        parts = live_item.get('parts', 1)

        # 生成 live_moment 目录路径
        live_moment = f'/gallery/LiveMoment/{date.year}/{date.month:02d}/{date.day:02d}/'

        return {
            'id': date_str,
            'date': date_str,
            'title': title,
            'summary': summary,
            'viewCount': 'N/A',
            'danmakuCount': 'N/A',
            'startTime': 'N/A',
            'endTime': 'N/A',
            'duration': duration,
            'bvid': bvid,
            'parts': parts,
            'recordings': [],  # 前端根据 bvid 和 parts 生成
            'songCuts': song_cuts,
            'screenshots': screenshots,
            'danmakuCloudUrl': '',
            'coverUrl': screenshots[0] if screenshots else '',  # 使用第一张截图作为封面
        }

    @classmethod
    def _get_song_cuts_by_date(cls, date: datetime.date):
        """
        获取指定日期的歌切列表（演唱记录）

        Args:
            date: 日期对象

        Returns:
            list: 歌切列表，每项包含：
                - id: 演唱记录ID（用于跳转到详情页）
                - name: 歌曲名称
                - videoUrl: 演唱记录链接（B站视频链接）
        """
        from song_management.models import SongRecord

        song_records = SongRecord.objects.filter(
            performed_at=date
        ).select_related('song').order_by('song__song_name')

        return [{
            'id': record.id,  # 演唱记录ID，可用于跳转到详情页
            'name': record.song.song_name,
            'videoUrl': record.url or '',  # 演唱记录链接（B站视频链接）
        } for record in song_records]

    @classmethod
    def _get_screenshots_by_date(cls, date: datetime.date):
        """获取指定日期的截图列表（从 LiveMoment 目录）"""
        from django.core.files.storage import default_storage
        import os

        # 生成 live_moment 目录路径
        live_moment = f'/gallery/LiveMoment/{date.year}/{date.month:02d}/{date.day:02d}/'
        folder_path = live_moment.lstrip('/')

        try:
            # 检查目录是否存在
            full_path = os.path.join(default_storage.location, folder_path)
            if not os.path.exists(full_path):
                return []

            # 获取目录下所有图片文件
            if os.path.isdir(full_path):
                files = os.listdir(full_path)
                image_files = sorted([
                    f for f in files
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
                ])

                # 返回完整的图片 URL 列表
                return [f"{live_moment}{f}" for f in image_files]
            return []
        except Exception:
            return []