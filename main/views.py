from django.http import HttpResponse
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status, generics, filters
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Songs, SongRecord, Style
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.core.cache import cache
from .utils import is_mobile
from .serializers import SongsSerializer, SongRecordSerializer, StyleSerializer

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
        queryset = Songs.objects.all()
        
        # 曲风过滤
        styles = self.request.query_params.getlist('styles', [])
        if not styles:
            style_raw = self.request.query_params.get('styles')
            if style_raw:
                styles = style_raw.split(',')
        styles = [s.strip() for s in styles if s.strip()]
        
        if styles:
            queryset = queryset.filter(songstyle__style__name__in=styles).distinct()
            
        return queryset

    def list(self, request, *args, **kwargs):
        # 获取查询参数
        query = self.request.query_params.get("q", "")
        page_num = self.request.query_params.get("page", 1)
        page_size = self.request.query_params.get("limit", 50)
        ordering = self.request.query_params.get("ordering", "")
        style_list = self.get_queryset()._result_cache if hasattr(self.get_queryset(), '_result_cache') else []
        
        # 构造缓存key
        cache_key = f"song_list_api:{query}:{page_num}:{page_size}:{ordering}:{'-'.join([str(s) for s in style_list])}"
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)
        
        # 调用父类方法获取数据
        response = super().list(request, *args, **kwargs)
        
        # 缓存结果
        cache.set(cache_key, response.data, 600)  # 缓存10分钟
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
        cache_key = f"song_records:{song_id}:{page_num}:{page_size}"
        records = cache.get(cache_key)

        if records is not None:
            return Response(records)

        # 调用父类方法获取数据
        try:
            queryset = self.get_queryset()
            paginator = Paginator(queryset, page_size)
            page = paginator.get_page(page_num)
            
            serializer = self.get_serializer(page, many=True)
            data = {
                "total": paginator.count,
                "page": page.number,
                "page_size": paginator.per_page,
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
            
            cache.set(cache_key, data, 600)
            return Response(data)
        except Songs.DoesNotExist:
            return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)


class StyleListView(generics.ListAPIView):
    """
    获取所有曲风列表
    """
    queryset = Style.objects.all()
    serializer_class = StyleSerializer


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
    return Response(result)

@api_view(['GET'])
def is_mobile_api(request):
    return Response({'is_mobile': is_mobile(request)})