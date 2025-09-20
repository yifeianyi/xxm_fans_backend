from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Songs, SongRecord, Style, Tag, Recommendation
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.core.cache import cache
from .serializers import SongsSerializer, SongRecordSerializer, StyleSerializer
import logging

# 配置日志
logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


class SongListView(generics.ListAPIView):
    """
    获取歌曲列表，支持搜索、分页和排序
    """
    serializer_class = SongsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['song_name', 'singer']
    ordering_fields = ['singer', 'last_performed', 'perform_count']
    ordering = ['-last_performed']

    def get_queryset(self):
        from django.db.models import Q
        
        queryset = Songs.objects.all()
        
        # 添加调试信息
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"请求参数: {self.request.query_params}")
        
        # 处理搜索查询
        query = self.request.query_params.get("q", "")
        if query:
            queryset = queryset.filter(
                Q(song_name__icontains=query) | Q(singer__icontains=query)
            )
        
        # 语言过滤
        language = self.request.query_params.get("language", "")
        if language:
            languages = language.split(',')
            languages = [lang.strip() for lang in languages if lang.strip()]
            if languages:
                queryset = queryset.filter(language__in=languages)
        
        # 收集所有筛选条件
        filters = Q()
        
        # 曲风过滤
        styles = self.request.query_params.getlist('styles', [])
        if not styles:
            style_raw = self.request.query_params.get('styles')
            if style_raw:
                styles = style_raw.split(',')
        styles = [s.strip() for s in styles if s.strip()]
        
        logger.info(f"曲风筛选条件: {styles}")
        
        if styles:
            style_filter = Q()
            for style in styles:
                style_filter |= Q(songstyle__style__name=style)
            filters &= style_filter
            
        # 标签过滤
        tags = self.request.query_params.getlist('tags', [])
        if not tags:
            tags_raw = self.request.query_params.get('tags')
            if tags_raw:
                tags = tags_raw.split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        logger.info(f"标签筛选条件: {tags}")
        
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(songtag__tag__name=tag)
            filters &= tag_filter
            
        # 应用所有筛选条件
        if filters:
            queryset = queryset.filter(filters).distinct()
            
        logger.info(f"最终查询集大小: {queryset.count()}")
        return queryset

    def list(self, request, *args, **kwargs):
        # 获取查询参数
        query = self.request.query_params.get("q", "")
        page_num = int(self.request.query_params.get("page", 1))
        page_size = int(self.request.query_params.get("limit", 50))
        # 限制最大页面大小为50
        page_size = min(page_size, 50)
        ordering = self.request.query_params.get("ordering", "")
        
        # 获取样式过滤条件
        styles = []
        styles_param = self.request.query_params.get('styles')
        if styles_param:
            styles = [s.strip() for s in styles_param.split(',') if s.strip()]
            
        # 获取标签过滤条件
        tags = []
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            
        # 获取语言过滤条件
        languages = []
        language_param = self.request.query_params.get('language')
        if language_param:
            languages = [lang.strip() for lang in language_param.split(',') if lang.strip()]
        
        # 使用Django的Paginator来处理分页
        queryset = self.get_queryset()
        
        # 应用排序
        if ordering:
            # 验证排序字段是否在允许的范围内
            allowed_ordering_fields = ['singer', 'last_performed', 'perform_count']
            # 处理降序字段（以-开头）
            order_field = ordering.lstrip('-')
            if order_field in allowed_ordering_fields:
                queryset = queryset.order_by(ordering)
        
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_num)
        
        # 序列化数据
        serializer = self.get_serializer(page, many=True)
        
        # 构造符合前端要求的响应格式
        data = {
            "total": paginator.count,
            "page": page.number,
            "page_size": page_size,
            "results": serializer.data
        }
        
        # 构造缓存key
        cache_key = f"song_list_api:{query}:{page_num}:{page_size}:{ordering}:{'-'.join(styles)}:{'-'.join(tags)}:{'-'.join(languages)}"
        
        # 尝试缓存结果，处理Redis连接异常
        try:
            cache.set(cache_key, data, 600)  # 缓存10分钟
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            
        response = Response(data)
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response


class SongRecordListView(generics.ListAPIView):
    """
    获取特定歌曲的演唱记录列表
    """
    serializer_class = SongRecordSerializer

    def get_queryset(self):
        song_id = self.kwargs['song_id']
        return SongRecord.objects.filter(song_id=song_id).order_by('-performed_at')
    
    def list(self, request, *args, **kwargs):
        song_id = self.kwargs['song_id']
        page_num = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        
        # 构造缓存key
        cache_key = f"song_records:{song_id}:{page_num}:{page_size}"
        
        # 尝试从缓存获取数据，处理Redis连接异常
        try:
            records = cache.get(cache_key)
            if records is not None:
                response = Response(records)
                response['Content-Type'] = 'application/json; charset=utf-8'
                return response
        except Exception as e:
            logger.warning(f"Cache get failed for song records: {e}")

        # 调用父类方法获取数据
        try:
            queryset = self.get_queryset()
            paginator = Paginator(queryset, page_size)
            page = paginator.get_page(page_num)
            
            serializer = self.get_serializer(page, many=True)
            data = {
                "total": paginator.count,
                "page": page.number,
                "page_size": page_size,  # 修复：使用传入的page_size而不是paginator.per_page
                "results": serializer.data
            }
            
            # 处理封面URL
            for record in data['results']:
                performed_at = record.get('performed_at')
                if performed_at:
                    date = datetime.strptime(performed_at, "%Y-%m-%d").date()
                    date_str = date.strftime("%Y-%m-%d")
                    year = date.strftime("%Y")
                    month = date.strftime("%m")
                    record["cover_url"] = record.get("cover_url") or f"/covers/{year}/{month}/{date_str}.jpg"
                else:
                    record["cover_url"] = "/covers/default.jpg"
            
            # 尝试缓存结果，处理Redis连接异常
            try:
                cache.set(cache_key, data, 600)
            except Exception as e:
                logger.warning(f"Cache set failed for song records: {e}")
                
            response = Response(data)
            response['Content-Type'] = 'application/json; charset=utf-8'
            return response
        except Songs.DoesNotExist:
            return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)


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
            response = Response(data)
            response['Content-Type'] = 'application/json; charset=utf-8'
            return response
    except Exception as e:
        logger.warning(f"Cache get failed for styles: {e}")
    
    # 获取所有曲风名称并排序
    style_names = list(Style.objects.values_list('name', flat=True).order_by('name'))
    
    # 尝试缓存结果，处理Redis连接异常
    try:
        cache.set(cache_key, style_names, 3600)  # 缓存1小时
    except Exception as e:
        logger.warning(f"Cache set failed for styles: {e}")
    
    response = Response(style_names)
    response['Content-Type'] = 'application/json; charset=utf-8'
    return response


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
                response = Response(data)
                response['Content-Type'] = 'application/json; charset=utf-8'
                return response
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
        
        response = Response(tag_names)
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        logger.error(f"Database query failed for tags: {e}")
        # 返回空列表而不是错误，确保前端不会崩溃
        response = Response([])
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response


@api_view(['GET'])
def top_songs_api(request):
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
    qs = Songs.objects.all()
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
            'last_performed': s.last_performed,
        }
        for s in qs
    ]
    response = Response(result)
    response['Content-Type'] = 'application/json; charset=utf-8'
    return response



# 随机返回一首歌
@api_view(['GET'])
def random_song_api(request):
    song = Songs.objects.order_by('?').first()
    if song:
        # 导入SongStyle模型
        from .models import SongStyle
        
        styles = [s.style.name for s in SongStyle.objects.filter(song=song)]
        data = {
            "id": song.id,
            "song_name": song.song_name,
            "singer": song.singer,
            "styles": styles,
            "last_performed": song.last_performed,
            "perform_count": song.perform_count,
            "language": song.language,
        }
        response = Response(data)
        response['Content-Type'] = 'application/json; charset=utf-8'
        return response
    else:
        return Response({"error": "No songs available."}, status=404)


@api_view(['GET'])
def recommendation_api(request):
    """
    获取激活的推荐语
    """
    # 尝试从缓存获取数据，处理Redis连接异常
    cache_key = "active_recommendation"
    try:
        data = cache.get(cache_key)
        if data is not None:
            response = Response(data)
            response['Content-Type'] = 'application/json; charset=utf-8'
            return response
    except Exception as e:
        logger.warning(f"Cache get failed for recommendation: {e}")
    
    # 获取激活的推荐语（按更新时间倒序取第一条）
    recommendation = Recommendation.objects.filter(is_active=True).order_by('-updated_at').first()
    
    if recommendation:
        # 获取推荐的歌曲列表
        recommended_songs = []
        for song in recommendation.recommended_songs.all():
            recommended_songs.append({
                "id": song.id,
                "song_name": song.song_name,
                "singer": song.singer,
                "perform_count": song.perform_count
            })
        
        data = {
            "content": recommendation.content,
            "recommended_songs": recommended_songs
        }
    else:
        data = {
            "content": "欢迎来到热歌榜！",
            "recommended_songs": []
        }
    
    # 尝试缓存结果，处理Redis连接异常
    try:
        cache.set(cache_key, data, 300)  # 缓存5分钟
    except Exception as e:
        logger.warning(f"Cache set failed for recommendation: {e}")
    
    response = Response(data)
    response['Content-Type'] = 'application/json; charset=utf-8'
    return response