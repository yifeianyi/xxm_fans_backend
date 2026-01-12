"""
Data Analytics API
"""
from .views import (
    WorkStaticListView,
    WorkStaticDetailView,
    WorkMetricsHourListView,
    CrawlSessionListView,
)

__all__ = [
    'WorkStaticListView',
    'WorkStaticDetailView',
    'WorkMetricsHourListView',
    'CrawlSessionListView',
]