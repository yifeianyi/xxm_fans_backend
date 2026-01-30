"""
URL 配置
"""
from django.urls import path
from .api.views import (
    WorkStaticListView,
    WorkStaticDetailView,
    WorkMetricsHourListView,
    CrawlSessionListView,
    WorkMetricsSummaryView,
    PlatformStatisticsView,
    TopWorksView,
    monthly_submission_stats,
    monthly_submission_records,
    years_submission_overview,
)

app_name = 'data_analytics'

urlpatterns = [
    # 作品静态信息
    path('works/', WorkStaticListView.as_view(), name='work-list'),
    path('works/<str:platform>/<str:work_id>/', WorkStaticDetailView.as_view(), name='work-detail'),

    # 作品指标
    path('works/<str:platform>/<str:work_id>/metrics/', WorkMetricsHourListView.as_view(), name='work-metrics'),
    path('works/<str:platform>/<str:work_id>/metrics/summary/', WorkMetricsSummaryView, name='work-metrics-summary'),

    # 平台统计
    path('platform/<str:platform>/statistics/', PlatformStatisticsView, name='platform-statistics'),
    path('platform/<str:platform>/top-works/', TopWorksView, name='top-works'),

    # 爬取会话
    path('sessions/', CrawlSessionListView.as_view(), name='session-list'),

    # 投稿时刻相关接口
    path('submissions/monthly/', monthly_submission_stats, name='monthly-submission-stats'),
    path('submissions/monthly/<int:year>/<int:month>/', monthly_submission_records, name='monthly-submission-records'),
    path('submissions/years/', years_submission_overview, name='years-submission-overview'),
]