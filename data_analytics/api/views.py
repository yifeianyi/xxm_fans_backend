"""
API 视图
"""
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.responses import success_response, error_response, paginated_response
from core.exceptions import InvalidParameterException
from .serializers import (
    WorkStaticSerializer,
    WorkMetricsHourSerializer,
    CrawlSessionSerializer,
)
from ..models import WorkStatic, WorkMetricsHour, CrawlSession
from ..services import AnalyticsService


class WorkStaticListView(generics.ListAPIView):
    """
    获取作品列表
    """
    serializer_class = WorkStaticSerializer
    pagination_class = None

    def get_queryset(self):
        platform = self.request.query_params.get("platform")
        is_valid = self.request.query_params.get("is_valid")
        limit = int(self.request.query_params.get("limit", 100))
        offset = int(self.request.query_params.get("offset", 0))

        queryset = WorkStatic.objects.all()

        if platform:
            queryset = queryset.filter(platform=platform)

        if is_valid is not None:
            queryset = queryset.filter(is_valid=is_valid.lower() == 'true')

        queryset = queryset.order_by('-publish_time')

        return queryset[offset:offset + limit]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class WorkStaticDetailView(generics.RetrieveAPIView):
    """
    获取作品详情
    """
    serializer_class = WorkStaticSerializer

    def get_object(self):
        platform = self.kwargs['platform']
        work_id = self.kwargs['work_id']
        try:
            return WorkStatic.objects.get(platform=platform, work_id=work_id)
        except WorkStatic.DoesNotExist:
            raise InvalidParameterException(f"作品不存在: {platform}/{work_id}")

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except InvalidParameterException as e:
            return error_response(message=str(e), status_code=404)


class WorkMetricsHourListView(generics.ListAPIView):
    """
    获取作品指标列表
    """
    serializer_class = WorkMetricsHourSerializer
    pagination_class = None

    def get_queryset(self):
        platform = self.kwargs['platform']
        work_id = self.kwargs['work_id']
        start_time = self.request.query_params.get("start_time")
        end_time = self.request.query_params.get("end_time")

        queryset = WorkMetricsHour.objects.filter(
            platform=platform,
            work_id=work_id
        )

        if start_time:
            queryset = queryset.filter(crawl_time__gte=start_time)

        if end_time:
            queryset = queryset.filter(crawl_time__lte=end_time)

        queryset = queryset.order_by('crawl_time')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CrawlSessionListView(generics.ListAPIView):
    """
    获取爬取会话列表
    """
    serializer_class = CrawlSessionSerializer
    pagination_class = None

    def get_queryset(self):
        source = self.request.query_params.get("source")
        limit = int(self.request.query_params.get("limit", 50))
        offset = int(self.request.query_params.get("offset", 0))

        queryset = CrawlSession.objects.all()

        if source:
            queryset = queryset.filter(source=source)

        queryset = queryset.order_by('-start_time')

        return queryset[offset:offset + limit]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


@api_view(['GET'])
def WorkMetricsSummaryView(request, platform, work_id):
    """
    获取作品指标汇总
    """
    start_time = request.query_params.get("start_time")
    end_time = request.query_params.get("end_time")

    try:
        summary = AnalyticsService.get_work_metrics_summary(
            platform=platform,
            work_id=work_id,
            start_time=start_time,
            end_time=end_time
        )
        return success_response(data=summary)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def PlatformStatisticsView(request, platform):
    """
    获取平台统计数据
    """
    days = int(request.query_params.get("days", 7))

    try:
        stats = AnalyticsService.get_platform_statistics(
            platform=platform,
            days=days
        )
        return success_response(data=stats)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def TopWorksView(request, platform):
    """
    获取热门作品
    """
    metric = request.query_params.get("metric", "view_count")
    limit = int(request.query_params.get("limit", 10))
    days = int(request.query_params.get("days", 7))

    try:
        works = AnalyticsService.get_top_works(
            platform=platform,
            metric=metric,
            limit=limit,
            days=days
        )
        return success_response(data=works)
    except InvalidParameterException as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=str(e))