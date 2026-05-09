from django.core.paginator import Paginator
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.responses import success_response, error_response, paginated_response
from moments.models import Moment
from .serializers import MomentSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def moment_list_api(request):
    source = request.GET.get('source', '').strip()

    try:
        page_num = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page_num = 1

    try:
        page_size = int(request.GET.get('limit', 20))
    except (ValueError, TypeError):
        page_size = 20

    # 限制最大页面大小，防止一次查询过多
    page_size = min(page_size, 100)
    page_num = max(page_num, 1)

    # 尝试从缓存获取
    cache_key = f"moments_list:{source}:{page_num}:{page_size}"
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return paginated_response(
                data=cached['results'],
                total=cached['total'],
                page=cached['page'],
                page_size=cached['page_size'],
            )
    except Exception as e:
        logger.warning(f"Cache get failed for moments: {e}")

    queryset = Moment.objects.all()
    if source in ('weibo', 'bilibili'):
        queryset = queryset.filter(source=source)

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_num)

    serializer = MomentSerializer(page.object_list, many=True)

    # 缓存结果
    cache_payload = {
        'results': serializer.data,
        'total': paginator.count,
        'page': page_num,
        'page_size': page_size,
    }
    try:
        cache.set(cache_key, cache_payload, 300)
    except Exception as e:
        logger.warning(f"Cache set failed for moments: {e}")

    return paginated_response(
        data=serializer.data,
        total=paginator.count,
        page=page_num,
        page_size=page_size,
    )


@api_view(['GET'])
def moment_detail_api(request, moment_id):
    try:
        moment = Moment.objects.get(id=moment_id)
    except Moment.DoesNotExist:
        return error_response(message='动态不存在', code=404)

    serializer = MomentSerializer(moment)
    return success_response(data=serializer.data)
