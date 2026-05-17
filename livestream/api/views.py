from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from core.responses import success_response, error_response
from ..services.livestream_service import LivestreamService
from ..exceptions import FileReadError, ParameterValidationError
import logging

logger = logging.getLogger(__name__)


class LivestreamConfigView(APIView):

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

    def get(self, request, *args, **kwargs):
        try:
            year = int(request.query_params.get('year', 2025))
            month = int(request.query_params.get('month', 1))
            include_details = request.query_params.get('include_details', 'false').lower() == 'true'

            if month < 1 or month > 12:
                return error_response(
                    message='月份参数无效，必须在 1-12 之间'
                )

            cache_key = f"livestream_list:{year}:{month}:{include_details}"
            try:
                cached = cache.get(cache_key)
                if cached is not None:
                    return success_response(data=cached, message='获取成功（缓存）')
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            livestreams = LivestreamService.get_livestreams_by_month(
                year, month, include_details=include_details
            )

            try:
                cache.set(cache_key, livestreams, 600)
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return success_response(
                data=livestreams,
                message='获取成功'
            )
        except ValueError:
            return error_response(message='参数格式错误')
        except ParameterValidationError as e:
            return error_response(message=e.message)
        except FileReadError:
            return success_response(
                data=[],
                message='该月份暂无直播记录'
            )
        except Exception as e:
            return error_response(message=f'获取直播记录失败: {str(e)}')


class LivestreamDetailView(APIView):
    """获取指定直播记录详情（主路径按ID，兼容按日期）"""

    def get(self, request, identifier, *args, **kwargs):
        try:
            livestream = LivestreamService.get_livestream_detail(identifier)

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
        except ParameterValidationError as e:
            return error_response(message=e.message)
        except Exception as e:
            return error_response(message=f'获取直播详情失败: {str(e)}')
