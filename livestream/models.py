from django.db import models


class Livestream(models.Model):
    """直播记录模型 - 存储直播基本信息"""

    # 基础信息
    date = models.DateField(
        unique=True,
        verbose_name='直播日期',
        help_text='直播日期，格式：YYYY-MM-DD'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='直播标题',
        help_text='直播标题，如：咻咻满-2025年11月30日-录播'
    )
    summary = models.TextField(
        blank=True,
        verbose_name='直播简介',
        help_text='直播简介或描述'
    )

    # B站视频信息
    bvid = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='B站视频BV号',
        help_text='B站视频的BV号'
    )
    duration_seconds = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='直播时长（秒）',
        help_text='直播总时长，单位：秒'
    )
    duration_formatted = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='直播时长（格式化）',
        help_text='格式化后的时长，如：3h4m50s'
    )
    parts = models.IntegerField(
        default=1,
        verbose_name='视频分段数',
        help_text='B站视频的分段数，用于前端生成播放链接'
    )

    # LiveMoment 图册目录
    live_moment = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='LiveMoment 图册目录',
        help_text='LiveMoment 图册目录路径，如：/gallery/LiveMoment/2025/11/30/'
    )

    # 回放封面
    cover_url = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='回放封面URL',
        help_text='直播回放的封面图片URL'
    )

    # 统计数据（预留字段）
    view_count = models.CharField(
        max_length=50,
        blank=True,
        default='N/A',
        verbose_name='观看人数',
        help_text='观看人数，如：1.2万'
    )
    danmaku_count = models.CharField(
        max_length=50,
        blank=True,
        default='N/A',
        verbose_name='弹幕数',
        help_text='弹幕总数，如：3.5万'
    )

    # 时间信息（预留字段）
    start_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='开播时间',
        help_text='开播时间，如：20:00:00'
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='下播时间',
        help_text='下播时间，如：23:30:00'
    )

    # 弹幕云图（预留字段）
    danmaku_cloud_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='弹幕云图URL',
        help_text='弹幕云图分析结果图片URL'
    )

    # 元数据
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='是否在直播日历中显示'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序',
        help_text='排序字段，数字越小越靠前'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'livestream'
        verbose_name = '直播记录'
        verbose_name_plural = '直播记录'
        ordering = ['-date', '-sort_order']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        return f"{self.date} - {self.title}"

    def get_bilibili_url(self):
        """获取 B站视频 URL"""
        if self.bvid:
            return f'https://www.bilibili.com/video/{self.bvid}'
        return ''

    def _generate_recordings(self):
        """生成分段视频列表（包含完整的视频链接）"""
        if not self.bvid:
            return []

        recordings = []

        if self.parts == 1:
            recordings.append({
                'title': self.title,
                'url': f'https://www.bilibili.com/video/{self.bvid}'
            })
        else:
            for i in range(1, self.parts + 1):
                recordings.append({
                    'title': f'{self.title} - P{i}',
                    'url': f'https://www.bilibili.com/video/{self.bvid}?p={i}'
                })

        return recordings

    def get_song_cuts(self):
        """获取当日歌切列表"""
        from song_management.models import SongRecord

        song_records = SongRecord.objects.filter(
            performed_at=self.date
        ).select_related('song').order_by('song__song_name')

        return [{
            'performed_at': record.performed_at.strftime('%Y-%m-%d'),
            'song_name': record.song.song_name,
            'url': record.url or '',
            'coverThumbnailUrl': record.get_cover_thumbnail_url() or '',
        } for record in song_records]

    def get_screenshots(self):
        """获取直播截图列表（从 live_moment 目录）"""
        from django.core.files.storage import default_storage
        import os

        if not self.live_moment:
            return []

        folder_path = self.live_moment.lstrip('/')

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
                return [f"{self.live_moment}{f}" for f in image_files]
            return []
        except Exception:
            return []

    def to_dict(self, include_details: bool = False):
        """
        转换为字典格式（用于 API 返回）

        Args:
            include_details: 是否包含详细信息（截图、歌切等）
        """
        from .services.livestream_service import LivestreamService

        # 基础信息
        result = {
            'id': self.date.strftime('%Y-%m-%d'),
            'date': self.date.strftime('%Y-%m-%d'),
            'title': self.title,
            'summary': self.summary or f'{self.date} 的精彩直播时刻',
            'viewCount': self.view_count,
            'danmakuCount': self.danmaku_count,
            'startTime': self.start_time.strftime('%H:%M') if self.start_time else 'N/A',
            'endTime': self.end_time.strftime('%H:%M') if self.end_time else 'N/A',
            'duration': self.duration_formatted or 'N/A',
            'bvid': self.bvid or '',
            'parts': self.parts,
        }

        # 只有在需要时才加载详细信息
        if include_details:
            # 调用服务层的方法获取截图列表（包含缩略图）
            screenshots_with_thumbnails = LivestreamService._get_screenshots_by_date(
                self.date,
                self.live_moment
            )

            # 生成完整的 recordings 数组（包含完整视频链接）
            recordings = self._generate_recordings()

            # 优先使用数据库中的封面URL，再fallback到演唱记录封面或截图缩略图
            cover_url = self.cover_url if self.cover_url else ''
            if not cover_url:
                cover_url = LivestreamService._get_first_song_cover_thumbnail(self.date)
            if not cover_url and screenshots_with_thumbnails:
                cover_url = screenshots_with_thumbnails[0]['thumbnailUrl']

            result.update({
                'recordings': recordings,  # 后端生成的完整视频链接列表
                'songCuts': self.get_song_cuts(),
                'screenshots': screenshots_with_thumbnails,  # 现在返回包含缩略图的数组
                'danmakuCloudUrl': self.danmaku_cloud_url or '',
                'coverUrl': cover_url,  # 优先使用数据库中的封面URL
            })
        else:
            # 优先使用数据库中的封面URL，再fallback到演唱记录封面或截图缩略图
            cover_url = self.cover_url if self.cover_url else ''
            if not cover_url:
                cover_url = LivestreamService._get_first_song_cover_thumbnail(self.date)
            if not cover_url:
                screenshots_with_thumbnails = LivestreamService._get_screenshots_by_date(
                    self.date,
                    self.live_moment
                )
                if screenshots_with_thumbnails:
                    cover_url = screenshots_with_thumbnails[0]['thumbnailUrl']
            result['coverUrl'] = cover_url

        return result