from django.db.models import Q
from datetime import datetime
from ..models import Livestream
from ..exceptions import (
    ParameterValidationError,
    DataNotFoundError,
    FileReadError,
    PathValidationError,
)
import json
import logging

logger = logging.getLogger('livestream')


class LivestreamService:
    """直播数据服务 - 优先使用 Livestream 模型，fallback 到 JSON 文件"""

    @staticmethod
    def _get_config():
        """获取直播配置"""
        from django.conf import settings
        return getattr(settings, 'LIVESTREAM_CONFIG', {})

    @classmethod
    def _get_live_data_file(cls):
        """获取 Fallback 数据源文件路径"""
        return cls._get_config().get('LIVE_DATA_FILE', '')

    @classmethod
    def _get_min_year(cls):
        """获取最小年份"""
        return cls._get_config().get('MIN_YEAR', 2019)

    @classmethod
    def _get_max_year(cls):
        """获取最大年份"""
        return cls._get_config().get('MAX_YEAR', 2030)

    @staticmethod
    def validate_year(year: int) -> bool:
        """
        验证年份是否在允许的范围内

        Args:
            year: 年份

        Returns:
            bool: 如果年份有效返回 True，否则返回 False
        """
        return LivestreamService._get_min_year() <= year <= LivestreamService._get_max_year()

    @staticmethod
    def validate_month(month: int) -> bool:
        """
        验证月份是否有效

        Args:
            month: 月份

        Returns:
            bool: 如果月份有效返回 True，否则返回 False
        """
        return 1 <= month <= 12

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """
        验证日期字符串格式是否正确

        Args:
            date_str: 日期字符串（格式：YYYY-MM-DD）

        Returns:
            bool: 如果日期格式正确返回 True，否则返回 False
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @classmethod
    def get_livestreams_by_month(cls, year: int, month: int, include_details: bool = False):
        """
        获取指定月份的所有直播记录

        Args:
            year: 年份
            month: 月份 (1-12)
            include_details: 是否包含详细信息（截图、歌切等）

        Returns:
            List[dict]: 直播记录列表

        Raises:
            ParameterValidationError: 参数验证失败
        """
        # 参数验证
        if not cls.validate_year(year):
            error_msg = f'年份验证失败: {year}，允许范围: {cls._get_min_year()}-{cls._get_max_year()}'
            logger.warning(error_msg)
            raise ParameterValidationError(error_msg, field_name='year')

        if not cls.validate_month(month):
            error_msg = f'月份验证失败: {month}，允许范围: 1-12'
            logger.warning(error_msg)
            raise ParameterValidationError(error_msg, field_name='month')

        livestreams = []

        try:
            # 优先从 Livestream 模型获取数据
            db_livestreams = Livestream.objects.filter(
                date__year=year,
                date__month=month,
                is_active=True
            ).order_by('-date')

            if db_livestreams.exists():
                # 使用数据库数据
                for livestream in db_livestreams:
                    livestreams.append(livestream.to_dict(include_details=include_details))
            else:
                # Fallback: 从 JSON 文件加载数据
                livestreams = cls._get_livestreams_from_json(year, month, include_details=include_details)
        except Exception as e:
            logger.error(f'获取月度直播记录失败: {e}', exc_info=True)
            raise

        return livestreams

    @classmethod
    def get_livestream_by_date(cls, date_str: str):
        """
        获取指定日期的直播记录

        Args:
            date_str: 日期字符串 (YYYY-MM-DD)

        Returns:
            dict: 直播记录详情，如果不存在返回 None

        Raises:
            ParameterValidationError: 参数验证失败
        """
        # 日期格式验证
        if not cls.validate_date(date_str):
            error_msg = f'日期格式验证失败: {date_str}，期望格式: YYYY-MM-DD'
            logger.warning(error_msg)
            raise ParameterValidationError(error_msg, field_name='date')

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # 额外验证年份范围
            if not cls.validate_year(date_obj.year):
                error_msg = f'年份验证失败: {date_obj.year}，允许范围: {cls._get_min_year()}-{cls._get_max_year()}'
                logger.warning(error_msg)
                raise ParameterValidationError(error_msg, field_name='year')
        except ValueError:
            error_msg = f'日期解析失败: {date_str}，期望格式: YYYY-MM-DD'
            logger.error(error_msg)
            raise ParameterValidationError(error_msg, field_name='date')

        try:
            # 优先从 Livestream 模型获取数据
            livestream = Livestream.objects.get(date=date_obj, is_active=True)
            return livestream.to_dict(include_details=True)
        except Livestream.DoesNotExist:
            # Fallback: 从 JSON 文件获取数据
            return cls._get_livestream_from_json(date_str)
        except Exception as e:
            logger.error(f'获取单日直播记录失败: {e}', exc_info=True)
            raise

    @classmethod
    def _get_livestreams_from_json(cls, year: int, month: int, include_details: bool = False):
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

            livestream = cls._build_livestream_from_json(date_obj, item, include_details=include_details)
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
        """
        加载 live_final.json 数据

        Returns:
            list: 直播数据列表

        Raises:
            FileReadError: 文件读取失败
        """
        file_path = cls._get_live_data_file()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f'直播数据文件不存在: {file_path}')
            raise FileReadError(f'直播数据文件不存在', file_path=file_path)
        except json.JSONDecodeError as e:
            logger.error(f'直播数据文件格式错误: {e}', exc_info=True)
            raise FileReadError(f'直播数据文件格式错误: {e}', file_path=file_path)
        except Exception as e:
            logger.error(f'加载直播数据文件失败: {e}', exc_info=True)
            raise FileReadError(f'加载直播数据文件失败: {e}', file_path=file_path)

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
    def _build_livestream_from_json(cls, date: datetime.date, live_item: dict, include_details: bool = False):
        """从 JSON 数据构建直播记录"""
        date_str = date.strftime('%Y-%m-%d')

        # 使用 live_final.json 中的标题和描述
        title = live_item.get('title', f'{date_str} 直播记录')
        summary = live_item.get('describe', f'{date_str} 的精彩直播时刻')
        duration = live_item.get('duration_formatted', 'N/A')
        bvid = live_item.get('bvid', '')
        parts = live_item.get('parts', 1)

        # 基础信息
        result = {
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
        }

        # 只有在需要时才加载详细信息
        if include_details:
            # 获取当日歌切（演唱记录）
            song_cuts = cls._get_song_cuts_by_date(date)

            # 获取当日截图（从 LiveMoment 目录，包含缩略图）
            screenshots_with_thumbnails = cls._get_screenshots_by_date(date)

            # 生成完整的 recordings 数组
            recordings = cls._generate_recordings(bvid, title, parts)

            # 优先使用演唱记录的封面缩略图，其次使用截图缩略图
            cover_url = cls._get_first_song_cover_thumbnail(date)
            if not cover_url and screenshots_with_thumbnails:
                cover_url = screenshots_with_thumbnails[0]['thumbnailUrl']

            result.update({
                'recordings': recordings,  # 后端生成的完整视频链接列表
                'songCuts': song_cuts,
                'screenshots': screenshots_with_thumbnails,  # 包含缩略图的数组
                'danmakuCloudUrl': '',
                'coverUrl': cover_url,  # 优先使用演唱记录封面缩略图
            })
        else:
            # 优先使用演唱记录的封面缩略图，其次使用截图缩略图
            cover_url = cls._get_first_song_cover_thumbnail(date)
            if not cover_url:
                screenshots_with_thumbnails = cls._get_screenshots_by_date(date)
                if screenshots_with_thumbnails:
                    cover_url = screenshots_with_thumbnails[0]['thumbnailUrl']
            result['coverUrl'] = cover_url

        return result

    @classmethod
    def _get_first_song_cover_thumbnail(cls, date: datetime.date):
        """
        获取指定日期第一首演唱记录的封面缩略图

        Args:
            date: 日期对象

        Returns:
            str: 封面缩略图URL，如果没有则返回空字符串
        """
        from song_management.models import SongRecord

        try:
            song_record = SongRecord.objects.filter(
                performed_at=date
            ).select_related('song').order_by('song__song_name').first()

            if song_record and song_record.cover_url:
                return song_record.get_cover_thumbnail_url() or ''
        except Exception as e:
            logger.error(f'获取演唱记录封面缩略图失败: {e}', exc_info=True)

        return ''

    @classmethod
    def _get_song_cuts_by_date(cls, date: datetime.date):
        """
        获取指定日期的歌切列表（演唱记录）

        Args:
            date: 日期对象

        Returns:
            list: 歌切列表，每项包含：
                - performed_at: 演唱日期
                - song_name: 歌曲名称
                - url: 演唱记录链接（B站视频链接）
                - coverThumbnailUrl: 封面缩略图URL
        """
        from song_management.models import SongRecord

        song_records = SongRecord.objects.filter(
            performed_at=date
        ).select_related('song').order_by('song__song_name')

        return [{
            'performed_at': record.performed_at.strftime('%Y-%m-%d'),
            'song_name': record.song.song_name,
            'url': record.url or '',
            'coverThumbnailUrl': record.get_cover_thumbnail_url() or '',
        } for record in song_records]

    @staticmethod
    def _generate_recordings(bvid: str, title: str, parts: int):
        """生成分段视频列表（包含完整的视频链接）"""
        if not bvid:
            return []

        recordings = []

        if parts == 1:
            recordings.append({
                'title': title,
                'url': f'https://www.bilibili.com/video/{bvid}'
            })
        else:
            for i in range(1, parts + 1):
                recordings.append({
                    'title': f'{title} - P{i}',
                    'url': f'https://www.bilibili.com/video/{bvid}?p={i}'
                })

        return recordings

    @staticmethod
    def _validate_path(base_dir: str, requested_path: str) -> bool:
        """
        验证路径是否在允许的目录范围内（防止目录遍历攻击）

        Args:
            base_dir: 基础目录（允许访问的根目录）
            requested_path: 请求的路径

        Returns:
            bool: 如果路径安全返回 True，否则返回 False
        """
        import os
        abs_base = os.path.abspath(base_dir)
        abs_requested = os.path.abspath(requested_path)
        return os.path.commonpath([abs_base, abs_requested]) == abs_base

    @classmethod
    def _get_screenshots_by_date(cls, date: datetime.date, live_moment: str = None):
        """
        获取指定日期的截图列表，包含缩略图URL（从 LiveMoment 目录）

        Args:
            date: 日期对象
            live_moment: LiveMoment 目录路径（可选，如果不提供则自动生成）

        Returns:
            list: 截图列表，每项包含：
                - url: 原图URL
                - thumbnailUrl: 缩略图URL

        Raises:
            PathValidationError: 路径验证失败
        """
        from django.core.files.storage import default_storage
        import os

        # 如果没有提供 live_moment 路径，则自动生成
        if not live_moment:
            live_moment = f'/gallery/LiveMoment/{date.year}/{date.month:02d}/{date.day:02d}/'

        folder_path = live_moment.lstrip('/')

        try:
            # 构建完整路径
            full_path = os.path.join(default_storage.location, folder_path)

            # 路径安全验证：确保请求的路径在允许的目录范围内
            allowed_base = default_storage.location
            if not cls._validate_path(allowed_base, full_path):
                error_msg = f'路径安全验证失败: {full_path}'
                logger.warning(error_msg)
                raise PathValidationError(error_msg, requested_path=full_path)

            # 检查目录是否存在
            if not os.path.exists(full_path):
                return []

            # 获取目录下所有图片文件
            if os.path.isdir(full_path):
                files = os.listdir(full_path)
                image_files = sorted([
                    f for f in files
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
                ])

                # 缩略图存放在 /gallery/thumbnails/LiveMoment/ 目录下
                # 命名格式：YYYY_MM_DD-N.webp
                date_prefix = f"{date.year}_{date.month:02d}_{date.day:02d}"

                # 返回包含原图URL和缩略图URL的数组
                result = []
                for idx, f in enumerate(image_files, 1):
                    thumbnail_filename = f"{date_prefix}-{idx}.webp"
                    thumbnail_path = f"/gallery/thumbnails/LiveMoment/{date.year}/{date.month:02d}/{date.day:02d}/{thumbnail_filename}"

                    # 确保缩略图路径使用 /media/ 前缀
                    if not thumbnail_path.startswith('/media/'):
                        thumbnail_path = f"/media{thumbnail_path}"

                    # 原图路径：确保使用 /media/ 前缀
                    original_url = live_moment
                    if not original_url.startswith('/media/'):
                        original_url = f"/media{original_url}"
                    original_url = f"{original_url}{f}"

                    result.append({
                        'url': original_url,
                        'thumbnailUrl': thumbnail_path
                    })
                return result
            return []
        except PathValidationError:
            raise
        except Exception as e:
            logger.error(f'获取截图列表失败: {e}', exc_info=True)
            return []