"""
API 视图
"""
from django.utils import timezone
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


# ==================== 投稿时刻功能 API 视图 ====================

@api_view(['GET'])
def monthly_submission_stats(request):
    """
    获取月度投稿统计

    GET /api/data-analytics/submissions/monthly/?year=2024&platform=bilibili

    Args:
        year: 年份（默认当前年份）
        platform: 平台筛选（可选）

    Returns:
        JSON: 月度统计数据
    """
    from rest_framework import status
    from ..services.submission_service import SubmissionService
    from .serializers import MonthlySubmissionStatsResponseSerializer

    try:
        # 获取查询参数
        year = request.query_params.get('year', timezone.now().year)
        platform = request.query_params.get('platform')

        # 参数验证
        try:
            year = int(year)
        except (ValueError, TypeError):
            return error_response(
                message="参数错误：年份必须为整数",
                status_code=400
            )

        # 调用业务逻辑
        data = SubmissionService.get_monthly_submission_stats(year, platform)

        # 序列化响应
        serializer = MonthlySubmissionStatsResponseSerializer(data)
        return success_response(data=serializer.data)

    except Exception as e:
        return error_response(
            message=f"获取月度投稿统计失败：{str(e)}",
            status_code=500
        )


@api_view(['GET'])
def monthly_submission_records(request, year, month):
    """
    获取月度投稿记录

    GET /api/data-analytics/submissions/monthly/2024/1/?platform=bilibili&page=1&page_size=20

    Args:
        year: 年份（路径参数）
        month: 月份（路径参数）
        platform: 平台筛选（可选）
        is_valid: 是否有效投稿（可选）
        page: 页码（默认 1）
        page_size: 每页数量（默认 20）

    Returns:
        JSON: 月度投稿记录数据
    """
    from rest_framework import status
    from ..services.submission_service import SubmissionService
    from .serializers import MonthlySubmissionRecordsResponseSerializer

    try:
        # 获取查询参数
        platform = request.query_params.get('platform')
        is_valid = request.query_params.get('is_valid')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # 参数验证
        if page < 1:
            return error_response(
                message="参数错误：页码必须大于 0",
                status_code=400
            )

        if page_size < 1 or page_size > 100:
            return error_response(
                message="参数错误：每页数量必须在 1-100 之间",
                status_code=400
            )

        # 处理 is_valid 参数
        if is_valid is not None:
            is_valid = is_valid.lower() in ['true', '1', 'yes']

        # 调用业务逻辑
        data = SubmissionService.get_monthly_submission_records(
            year, month, platform, is_valid, page, page_size
        )

        # 序列化响应
        serializer = MonthlySubmissionRecordsResponseSerializer(data)
        return success_response(data=serializer.data)

    except ValueError as e:
        return error_response(
            message=f"参数错误：{str(e)}",
            status_code=400
        )
    except Exception as e:
        return error_response(
            message=f"获取月度投稿记录失败：{str(e)}",
            status_code=500
        )


@api_view(['GET'])
def years_submission_overview(request):
    """
    获取年度投稿概览

    GET /api/data-analytics/submissions/years/?platform=bilibili&start_year=2021&end_year=2024

    Args:
        platform: 平台筛选（可选）
        start_year: 起始年份（可选）
        end_year: 结束年份（可选）

    Returns:
        JSON: 年度投稿概览数据
    """
    from rest_framework import status
    from ..services.submission_service import SubmissionService
    from .serializers import YearsSubmissionOverviewResponseSerializer

    try:
        # 获取查询参数
        platform = request.query_params.get('platform')
        start_year = request.query_params.get('start_year')
        end_year = request.query_params.get('end_year')

        # 参数验证
        if start_year is not None:
            try:
                start_year = int(start_year)
            except (ValueError, TypeError):
                return error_response(
                    message="参数错误：起始年份必须为整数",
                    status_code=400
                )

        if end_year is not None:
            try:
                end_year = int(end_year)
            except (ValueError, TypeError):
                return error_response(
                    message="参数错误：结束年份必须为整数",
                    status_code=400
                )

        # 调用业务逻辑
        data = SubmissionService.get_years_submission_overview(
            platform, start_year, end_year
        )

        # 序列化响应
        serializer = YearsSubmissionOverviewResponseSerializer(data)
        return success_response(data=serializer.data)

    except Exception as e:
        return error_response(
            message=f"获取年度投稿概览失败：{str(e)}",
            status_code=500
        )


# ==================== 粉丝数数据分析 API 视图 ====================

@api_view(['GET'])
def accounts_list(request):
    """
    获取所有账号列表

    GET /api/data-analytics/followers/accounts/

    Returns:
        JSON: 账号列表
    """
    from ..services.follower_service import FollowerService

    try:
        accounts = FollowerService.get_all_accounts()
        return success_response(data=accounts)
    except Exception as e:
        return error_response(
            message=f"获取账号列表失败：{str(e)}",
            status_code=500
        )


@api_view(['GET'])
def accounts_data(request):
    """
    获取所有账号的粉丝数据

    GET /api/data-analytics/followers/accounts/data/?granularity=WEEK&days=7

    Query Parameters:
        granularity: 时间粒度 ('DAY', 'WEEK', 'MONTH'), 默认 'WEEK'
        days: 查询天数，默认 30

    Returns:
        JSON: 账号粉丝数据
    """
    from ..services.follower_service import FollowerService

    try:
        granularity = request.query_params.get('granularity', 'WEEK')
        days = int(request.query_params.get('days', 30))

        # 参数验证
        if granularity not in ['DAY', 'WEEK', 'MONTH']:
            return error_response(
                message=f"参数错误：granularity 必须为 'DAY', 'WEEK' 或 'MONTH'",
                status_code=400
            )

        if days < 1 or days > 365:
            return error_response(
                message="参数错误：days 必须在 1-365 之间",
                status_code=400
            )

        data = FollowerService.get_all_accounts_data(granularity, days)
        return success_response(data=data)

    except ValueError as e:
        return error_response(
            message=f"参数错误：{str(e)}",
            status_code=400
        )
    except Exception as e:
        return error_response(
            message=f"获取账号数据失败：{str(e)}",
            status_code=500
        )


@api_view(['GET'])
def account_detail(request, account_id):
    """
    获取单个账号的详细数据

    GET /api/data-analytics/followers/accounts/{account_id}/?granularity=WEEK&days=7

    Path Parameters:
        account_id: 账号 ID

    Query Parameters:
        granularity: 时间粒度 ('DAY', 'WEEK', 'MONTH'), 默认 'WEEK'
        days: 查询天数，默认 30

    Returns:
        JSON: 账号详细数据
    """
    from ..services.follower_service import FollowerService

    try:
        granularity = request.query_params.get('granularity', 'WEEK')
        days = int(request.query_params.get('days', 30))

        # 参数验证
        if granularity not in ['DAY', 'WEEK', 'MONTH']:
            return error_response(
                message=f"参数错误：granularity 必须为 'DAY', 'WEEK' 或 'MONTH'",
                status_code=400
            )

        # 获取账号信息
        account = FollowerService.get_account_by_id(int(account_id))
        if not account:
            return error_response(
                message=f"账号不存在：{account_id}",
                status_code=404
            )

        # 获取数据
        current_count = FollowerService.get_current_follower_count(int(account_id))
        history = FollowerService.get_follower_history(
            int(account_id),
            granularity,
            days
        )

        data = {
            'id': str(account.id),
            'name': account.name,
            'uid': account.uid,
            'platform': account.platform,
            'totalFollowers': current_count or 0,
            'history': {
                granularity: history
            }
        }

        return success_response(data=data)

    except ValueError as e:
        return error_response(
            message=f"参数错误：{str(e)}",
            status_code=400
        )
    except Exception as e:
        return error_response(
            message=f"获取账号详情失败：{str(e)}",
            status_code=500
        )