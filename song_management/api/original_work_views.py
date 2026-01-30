"""
原创作品 API 视图
"""
from rest_framework.decorators import api_view
from core.responses import success_response
from ..models import OriginalWork
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def original_works_list_api(request):
    """
    获取所有原创作品列表
    """
    cache_key = "original_works_list"
    try:
        data = cache.get(cache_key)
        if data is not None:
            return success_response(data=data, message="获取原创作品列表成功")
    except Exception as e:
        logger.warning(f"Cache get failed for original works: {e}")

    # 获取所有原创作品
    works = OriginalWork.objects.all().order_by('-featured', '-release_date')

    # 构建返回数据
    result = []
    for work in works:
        work_data = {
            'title': work.title,
            'date': work.date,
            'desc': work.desc,
            'cover': work.cover.url if work.cover else '',
            'neteaseId': work.neteaseId,
            'bilibiliBvid': work.bilibiliBvid,
            'featured': work.featured,
        }
        result.append(work_data)

    # 尝试缓存结果
    try:
        cache.set(cache_key, result, 3600)  # 缓存1小时
    except Exception as e:
        logger.warning(f"Cache set failed for original works: {e}")

    return success_response(data=result, message="获取原创作品列表成功")