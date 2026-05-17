from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from core.responses import success_response, error_response, paginated_response
from ..services.fan_ranking_service import FanRankingService
from ..services.guard_service import GuardService
import logging

logger = logging.getLogger(__name__)


class AttendanceRankingView(APIView):
    """出勤率排名"""

    def get(self, request):
        try:
            year = request.query_params.get('year')
            if year:
                year = int(year)
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            page_size = min(page_size, 100)

            cache_key = f"attendance_ranking:{year}:{page}:{page_size}"
            try:
                cached = cache.get(cache_key)
                if cached is not None:
                    return paginated_response(
                        data=cached['data'], total=cached['total'],
                        page=cached['page'], page_size=cached['page_size']
                    )
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            result, total = FanRankingService.get_attendance_ranking(
                year=year, page=page, page_size=page_size
            )
            try:
                cache.set(cache_key, {'data': result, 'total': total, 'page': page, 'page_size': page_size}, 300)
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return paginated_response(
                data=result, total=total, page=page, page_size=page_size
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except Exception as e:
            return error_response(message=f'获取出勤率排名失败: {str(e)}')


class DanmakuRankingView(APIView):
    """弹幕排名"""

    def get(self, request):
        try:
            year = request.query_params.get('year')
            if year:
                year = int(year)
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            page_size = min(page_size, 100)

            cache_key = f"danmaku_ranking:{year}:{page}:{page_size}"
            try:
                cached = cache.get(cache_key)
                if cached is not None:
                    return paginated_response(
                        data=cached['data'], total=cached['total'],
                        page=cached['page'], page_size=cached['page_size']
                    )
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            result, total = FanRankingService.get_danmaku_ranking(
                year=year, page=page, page_size=page_size
            )
            try:
                cache.set(cache_key, {'data': result, 'total': total, 'page': page, 'page_size': page_size}, 300)
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return paginated_response(
                data=result, total=total, page=page, page_size=page_size
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except Exception as e:
            return error_response(message=f'获取弹幕排名失败: {str(e)}')


class FanSearchView(APIView):
    """搜索粉丝"""

    def get(self, request):
        try:
            query = request.query_params.get('q', '').strip()
            if not query:
                return error_response(message='请输入搜索关键词')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            page_size = min(page_size, 100)

            result, total = FanRankingService.search_fans(
                query=query, page=page, page_size=page_size
            )
            return paginated_response(
                data=result, total=total, page=page, page_size=page_size
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except Exception as e:
            return error_response(message=f'搜索失败: {str(e)}')


class FanProfileView(APIView):
    """粉丝详情"""

    def get(self, request, uid):
        try:
            result = FanRankingService.get_fan_profile(uid)
            if result is None:
                return success_response(
                    data=None,
                    message='未找到该粉丝'
                )
            return success_response(data=result, message='获取成功')
        except Exception as e:
            return error_response(message=f'获取粉丝详情失败: {str(e)}')


class FansStatsView(APIView):
    """统计概览"""

    def get(self, request):
        try:
            result = FanRankingService.get_stats()
            return success_response(data=result, message='获取成功')
        except Exception as e:
            return error_response(message=f'获取统计数据失败: {str(e)}')


class GuardListView(APIView):
    """大航海用户列表"""

    def get(self, request):
        try:
            guard_level = request.query_params.get('guard_level')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            page_size = min(page_size, 100)

            if guard_level is not None:
                guard_level = int(guard_level)
                result, total = GuardService.get_guards_by_type(
                    guard_level=guard_level, page=page, page_size=page_size
                )
            else:
                result, total = GuardService.get_all_guards(
                    page=page, page_size=page_size
                )

            return paginated_response(
                data=result, total=total, page=page, page_size=page_size
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except Exception as e:
            return error_response(message=f'获取大航海列表失败: {str(e)}')
