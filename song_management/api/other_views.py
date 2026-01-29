"""
其他辅助视图（曲风、标签、排行榜、随机歌曲）
"""
from rest_framework.decorators import api_view
from core.responses import success_response
from core.exceptions import SongNotFoundException
from ..models import Song, Style, Tag, SongStyle
from django.db.models import Count
from django.core.cache import cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def style_list_api(request):
    """
    获取所有曲风列表，返回简单的名称数组
    """
    # 尝试从缓存获取数据，处理Redis连接异常
    cache_key = "style_list_simple"
    try:
        data = cache.get(cache_key)
        if data is not None:
            return success_response(data=data, message="获取曲风列表成功")
    except Exception as e:
        logger.warning(f"Cache get failed for styles: {e}")

    # 获取所有曲风名称并排序
    style_names = list(Style.objects.values_list('name', flat=True).order_by('name'))

    # 尝试缓存结果，处理Redis连接异常
    try:
        cache.set(cache_key, style_names, 3600)  # 缓存1小时
    except Exception as e:
        logger.warning(f"Cache set failed for styles: {e}")

    return success_response(data=style_names, message="获取曲风列表成功")


@api_view(['GET'])
def tag_list_api(request):
    """
    获取所有标签列表，返回简单的名称数组
    """
    # 尝试从缓存获取数据，处理Redis连接异常
    cache_key = "tag_list_simple"
    try:
        data = cache.get(cache_key)
        if data is not None:
            # 确保返回的数据不是空列表
            if isinstance(data, list) and len(data) > 0:
                return success_response(data=data, message="获取标签列表成功")
            else:
                logger.warning("Cache data is empty or invalid for tags")
    except Exception as e:
        logger.warning(f"Cache get failed for tags: {e}")

    # 获取所有标签名称并排序
    try:
        tag_names = list(Tag.objects.values_list('name', flat=True).order_by('name'))

        # 检查是否有标签数据
        if not tag_names:
            logger.warning("No tags found in database")
            # 返回空列表而不是None
            tag_names = []

        # 尝试缓存结果，处理Redis连接异常
        try:
            cache.set(cache_key, tag_names, 3600)  # 缓存1小时
        except Exception as e:
            logger.warning(f"Cache set failed for tags: {e}")

        return success_response(data=tag_names, message="获取标签列表成功")
    except Exception as e:
        logger.error(f"Database query failed for tags: {e}")
        # 返回空列表而不是错误，确保前端不会崩溃
        return success_response(data=[], message="获取标签列表成功")


@api_view(['GET'])
def top_songs_api(request):
    """
    获取热歌榜
    """
    range_map = {
        'all': None,
        '1m': 30,
        '3m': 90,
        '1y': 365,
        '10d': 10,
        '20d': 20,
        '30d': 30,
    }
    range_key = request.GET.get('range', 'all')
    days = range_map.get(range_key, None)
    limit = int(request.GET.get('limit', 10))  # 新增limit参数，默认10
    qs = Song.objects.all()
    if days:
        since = datetime.now().date() - timedelta(days=days)
        qs = qs.filter(records__performed_at__gte=since)
    # annotate 统计演唱次数
    qs = qs.annotate(recent_count=Count('records')).order_by('-recent_count', '-last_performed')[:limit]
    result = [
        {
            'id': s.id,
            'song_name': s.song_name,
            'singer': s.singer,
            'perform_count': s.recent_count,
            'first_perform': s.first_perform,
            'last_perform': s.last_performed,
        }
        for s in qs
    ]
    return success_response(data=result, message="获取排行榜成功")


@api_view(['GET'])
def random_song_api(request):
    """
    随机返回一首歌
    """
    song = Song.objects.order_by('?').first()
    if song:
        styles = [s.style.name for s in SongStyle.objects.filter(song=song)]
        data = {
            "id": song.id,
            "song_name": song.song_name,
            "singer": song.singer,
            "styles": styles,
            "first_perform": song.first_perform,
            "last_perform": song.last_performed,
            "perform_count": song.perform_count,
            "language": song.language,
        }
        return success_response(data=data, message="获取随机歌曲成功")
    else:
        raise SongNotFoundException("暂无可用歌曲")
