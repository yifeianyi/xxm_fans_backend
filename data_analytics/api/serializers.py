"""
API 序列化器
"""
from rest_framework import serializers
from ..models import WorkStatic, WorkMetricsHour, CrawlSession


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