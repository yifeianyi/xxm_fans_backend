"""
API 视图
"""
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from core.responses import success_response, error_response, paginated_response
from core.exceptions import SongNotFoundException, InvalidParameterException
from .serializers import SongSerializer, SongRecordSerializer, StyleSerializer, TagSerializer
from ..services import SongService, SongRecordService, RankingService
from ..models import Song, SongRecord, Style, Tag


class SongListView(generics.ListAPIView):
    """
    获取歌曲列表，支持搜索、分页和排序
    """
    serializer_class = SongSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['song_name', 'singer']
    ordering_fields = ['singer', 'last_performed', 'perform_count']
    ordering = ['-last_performed']
    pagination_class = None  # 禁用默认分页

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        language = self.request.query_params.get("language", "")
        styles = self.request.query_params.getlist('styles', [])
        tags = self.request.query_params.getlist('tags', [])
        ordering = self.request.query_params.get("ordering", "")

        return SongService.get_songs(
            query=query,
            language=language,
            styles=styles,
            tags=tags,
            ordering=ordering
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("limit", 50))
        page_size = min(page_size, 50)

        # 序列化数据
        serializer = self.get_serializer(queryset, many=True)

        # 使用统一响应格式
        from rest_framework.response import Response
        response_data = {
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': len(queryset),
                'page': page,
                'page_size': page_size,
                'results': serializer.data
            }
        }
        return Response(response_data)


class SongDetailView(generics.RetrieveAPIView):
    """
    获取单个歌曲详情
    """
    serializer_class = SongSerializer

    def get_object(self):
        song_id = self.kwargs['song_id']
        return SongService.get_song_by_id(song_id)

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except SongNotFoundException as e:
            return error_response(message=str(e), status_code=404)


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
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        try:
            data = SongRecordService.get_records_by_song(song_id, page, page_size)
            return success_response(data=data)
        except SongNotFoundException as e:
            return error_response(message=str(e), status_code=404)


class StyleListView(generics.ListAPIView):
    """
    获取所有曲风列表
    """
    serializer_class = StyleSerializer
    queryset = Style.objects.all().order_by('name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class TagListView(generics.ListAPIView):
    """
    获取所有标签列表
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


@api_view(['GET'])
def TopSongsView(request):
    """
    获取热门歌曲排行榜
    """
    range_key = request.query_params.get('range', 'all')
    limit = int(request.query_params.get('limit', 10))

    try:
        songs = RankingService.get_top_songs(range_key, limit)
        return success_response(data=songs)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def RandomSongView(request):
    """
    获取随机歌曲
    """
    song = SongService.get_random_song()
    if song:
        serializer = SongSerializer(song)
        return success_response(data=serializer.data)
    else:
        return error_response(message="暂无歌曲数据", status_code=404)


@api_view(['GET'])
def LanguageListView(request):
    """
    获取所有语言列表
    """
    languages = SongService.get_all_languages()
    return success_response(data=languages)