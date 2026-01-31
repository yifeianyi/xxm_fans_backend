from rest_framework.views import APIView
from rest_framework.response import Response
from core.responses import success_response, error_response
from ..services.livestream_service import LivestreamService
from ..exceptions import FileReadError


class LivestreamConfigView(APIView):
    """获取直播配置信息（最小年份等）"""

    def get(self, request, *args, **kwargs):
        try:
            config = {
                'minYear': LivestreamService._get_min_year(),
            }
            return success_response(
                data=config,
                message='获取配置成功'
            )
        except Exception as e:
            return error_response(message=f'获取配置失败: {str(e)}')


class LivestreamListView(APIView):
    """获取指定月份的直播记录列表（默认只返回基本信息）"""

    def get(self, request, *args, **kwargs):
        try:
            year = int(request.query_params.get('year', 2025))
            month = int(request.query_params.get('month', 1))
            # 查询参数：是否包含详细信息（截图、歌切等），默认 false
            include_details = request.query_params.get('include_details', 'false').lower() == 'true'

            # 参数校验
            if month < 1 or month > 12:
                return error_response(
                    message='月份参数无效，必须在 1-12 之间'
                )

            livestreams = LivestreamService.get_livestreams_by_month(
                year, month, include_details=include_details
            )

            return success_response(
                data=livestreams,
                message='获取成功'
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except FileReadError:
            # JSON 文件不存在时返回空数组（数据库中也没有数据）
            return success_response(
                data=[],
                message='该月份暂无直播记录'
            )
        except Exception as e:
            return error_response(message=f'获取直播记录失败: {str(e)}')


class LivestreamDetailView(APIView):
    """获取指定日期的直播记录详情（包含所有详细信息）"""

    def get(self, request, date_str, *args, **kwargs):
        try:
            livestream = LivestreamService.get_livestream_by_date(date_str)

            if not livestream:
                return success_response(
                    data=None,
                    message='该日期无直播记录'
                )

            return success_response(
                data=livestream,
                message='获取成功'
            )
        except FileReadError:
            # JSON 文件不存在时返回 None
            return success_response(
                data=None,
                message='该日期无直播记录'
            )
        except Exception as e:
            return error_response(message=f'获取直播详情失败: {str(e)}')