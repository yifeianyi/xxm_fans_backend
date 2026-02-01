"""
API 序列化器
"""
from rest_framework import serializers
from ..models import WorkStatic, WorkMetricsHour, CrawlSession, Account, FollowerMetrics


class WorkStaticSerializer(serializers.ModelSerializer):
    """作品静态信息序列化器"""

    class Meta:
        model = WorkStatic
        fields = [
            'id',
            'platform',
            'work_id',
            'title',
            'author',
            'publish_time',
            'cover_url',
            'is_valid',
        ]


class WorkMetricsHourSerializer(serializers.ModelSerializer):
    """作品小时指标序列化器"""

    class Meta:
        model = WorkMetricsHour
        fields = [
            'id',
            'platform',
            'work_id',
            'crawl_time',
            'view_count',
            'like_count',
            'coin_count',
            'favorite_count',
            'danmaku_count',
            'comment_count',
            'session_id',
            'ingest_time',
        ]


class CrawlSessionSerializer(serializers.ModelSerializer):
    """爬取会话序列化器"""

    class Meta:
        model = CrawlSession
        fields = [
            'id',
            'source',
            'node_id',
            'start_time',
            'end_time',
            'total_work_count',
            'success_count',
            'fail_count',
            'note',
        ]


class AccountSerializer(serializers.ModelSerializer):
    """账号序列化器"""
    id = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'uid', 'platform', 'is_active']

    def get_id(self, obj):
        return str(obj.id)


class FollowerMetricsSerializer(serializers.ModelSerializer):
    """粉丝指标序列化器"""
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = FollowerMetrics
        fields = ['account', 'account_name', 'follower_count', 'crawl_time', 'ingest_time']


# ==================== 投稿时刻功能序列化器 ====================

class MonthlySubmissionStatsSerializer(serializers.Serializer):
    """月度投稿统计序列化器"""
    month = serializers.IntegerField(min_value=1, max_value=12)
    total = serializers.IntegerField(min_value=0)
    valid = serializers.IntegerField(min_value=0)
    invalid = serializers.IntegerField(min_value=0)
    first_submission = serializers.DateTimeField()
    last_submission = serializers.DateTimeField()


class YearSummarySerializer(serializers.Serializer):
    """年度汇总统计序列化器"""
    total_submissions = serializers.IntegerField(min_value=0)
    valid_submissions = serializers.IntegerField(min_value=0)
    invalid_submissions = serializers.IntegerField(min_value=0)
    active_months = serializers.IntegerField(min_value=0)


class MonthlySubmissionStatsResponseSerializer(serializers.Serializer):
    """月度投稿统计响应序列化器"""
    year = serializers.IntegerField()
    platform = serializers.CharField(allow_null=True)
    monthly_stats = MonthlySubmissionStatsSerializer(many=True)
    year_summary = YearSummarySerializer()


class SubmissionRecordSerializer(serializers.ModelSerializer):
    """投稿记录序列化器"""
    cover_thumbnail_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()

    class Meta:
        model = WorkStatic
        fields = [
            'id', 'platform', 'work_id', 'title', 'author',
            'publish_time', 'cover_url', 'cover_thumbnail_url',
            'is_valid', 'video_url', 'video_embed_url'
        ]

    def get_cover_thumbnail_url(self, obj):
        """获取封面缩略图 URL"""
        if obj.cover_url:
            # 解析原始封面路径
            # 原始路径格式: /media/data_analytics/covers/BV1Pi4y1M74w.jpg
            # 缩略图路径格式: /media/data_analytics/thumbnails/covers/BV1Pi4y1M74w.webp
            parts = obj.cover_url.split('/')
            filename = parts[-1]
            filename_without_ext = filename.rsplit('.', 1)[0]
            
            # 构建缩略图路径
            # 将 covers 替换为 thumbnails/covers
            thumb_url = '/media/data_analytics/thumbnails/covers/' + filename_without_ext + '.webp'
            return thumb_url
        return None

    def get_video_url(self, obj):
        """生成视频播放 URL"""
        platform_lower = obj.platform.lower() if obj.platform else ''
        if 'bilibili' in platform_lower or '哔哩哔哩' in obj.platform:
            return f"https://www.bilibili.com/video/{obj.work_id}"
        elif 'youtube' in platform_lower:
            return f"https://www.youtube.com/watch?v={obj.work_id}"
        return None

    def get_video_embed_url(self, obj):
        """生成视频嵌入 URL"""
        platform_lower = obj.platform.lower() if obj.platform else ''
        if 'bilibili' in platform_lower or '哔哩哔哩' in obj.platform:
            return f"https://player.bilibili.com/player.html?bvid={obj.work_id}"
        elif 'youtube' in platform_lower:
            return f"https://www.youtube.com/embed/{obj.work_id}"
        return None


class MonthlySubmissionRecordsResponseSerializer(serializers.Serializer):
    """月度投稿记录响应序列化器"""
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    platform = serializers.CharField(allow_null=True)
    records = SubmissionRecordSerializer(many=True)
    pagination = serializers.SerializerMethodField()

    def get_pagination(self, obj):
        """获取分页信息"""
        return {
            'total': obj.get('total', 0),
            'page': obj.get('page', 1),
            'page_size': obj.get('page_size', 20),
            'total_pages': obj.get('total_pages', 1)
        }


class YearStatsSerializer(serializers.Serializer):
    """年度统计序列化器"""
    year = serializers.IntegerField()
    total_submissions = serializers.IntegerField(min_value=0)
    valid_submissions = serializers.IntegerField(min_value=0)
    invalid_submissions = serializers.IntegerField(min_value=0)
    active_months = serializers.IntegerField(min_value=0)
    first_submission = serializers.DateTimeField()
    last_submission = serializers.DateTimeField()


class YearsSummarySerializer(serializers.Serializer):
    """年度汇总序列化器"""
    total_years = serializers.IntegerField(min_value=0)
    total_submissions = serializers.IntegerField(min_value=0)
    valid_submissions = serializers.IntegerField(min_value=0)
    invalid_submissions = serializers.IntegerField(min_value=0)


class YearsSubmissionOverviewResponseSerializer(serializers.Serializer):
    """年度投稿概览响应序列化器"""
    platform = serializers.CharField(allow_null=True)
    years = YearStatsSerializer(many=True)
    summary = YearsSummarySerializer()