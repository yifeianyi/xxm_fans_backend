from rest_framework.views import APIView
from rest_framework.response import Response
from core.responses import success_response, error_response, paginated_response
from ..services.fan_ranking_service import FanRankingService


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

            result, total = FanRankingService.get_attendance_ranking(
                year=year, page=page, page_size=page_size
            )
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

            result, total = FanRankingService.get_danmaku_ranking(
                year=year, page=page, page_size=page_size
            )
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
