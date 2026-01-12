"""
Admin 配置
"""
from django.contrib import admin
from ..models import WorkStatic, WorkMetricsHour, CrawlSession


@admin.register(WorkStatic)
class WorkStaticAdmin(admin.ModelAdmin):
    """作品静态信息 Admin"""
    list_display = ['id', 'platform', 'work_id', 'title', 'author', 'publish_time', 'is_valid']
    list_filter = ['platform', 'is_valid', 'publish_time']
    search_fields = ['work_id', 'title', 'author']
    list_per_page = 50
    ordering = ['-publish_time']
    readonly_fields = ['id']


@admin.register(WorkMetricsHour)
class WorkMetricsHourAdmin(admin.ModelAdmin):
    """作品小时指标 Admin"""
    list_display = ['id', 'platform', 'work_id', 'crawl_time', 'view_count', 'like_count', 'coin_count', 'favorite_count']
    list_filter = ['platform', 'crawl_time', 'session_id']
    search_fields = ['work_id']
    list_per_page = 50
    ordering = ['-crawl_time']
    readonly_fields = ['id', 'ingest_time']


@admin.register(CrawlSession)
class CrawlSessionAdmin(admin.ModelAdmin):
    """爬取会话 Admin"""
    list_display = ['id', 'source', 'node_id', 'start_time', 'end_time', 'total_work_count', 'success_count', 'fail_count']
    list_filter = ['source', 'start_time']
    search_fields = ['node_id']
    list_per_page = 50
    ordering = ['-start_time']
    readonly_fields = ['id']