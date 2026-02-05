"""
歌曲相关视图
"""
from django.core.paginator import Paginator
from rest_framework import generics, filters
from core.responses import paginated_response
from core.cache_utils import cached, CacheTimeout, CacheKeys
from ..models import Song
from .serializers import SongSerializer
from django.db.models import Q
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class SongListView(generics.ListAPIView):
    """
    获取歌曲列表，支持搜索、分页和排序
    """
    serializer_class = SongSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['song_name', 'singer']
    ordering_fields = ['singer', 'last_performed', 'perform_count', 'first_perform']
    ordering = ['-last_performed']

    def get_queryset(self):
        # 优化: 使用 prefetch_related 预取多对多关系，避免 N+1 查询
        queryset = Song.objects.prefetch_related(
            'song_styles__style',
            'song_tags__tag'
        )

        # 添加调试信息
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
                style_filter |= Q(song_styles__style__name=style)
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
                tag_filter |= Q(song_tags__tag__name=tag)
            filters &= tag_filter

        # 应用所有筛选条件
        if filters:
            queryset = queryset.filter(filters).distinct()

        # 优化: 使用 count() 缓存或直接返回，避免重复计算
        # 注意: 这里不再调用 count()，让 paginator 去处理
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
            allowed_ordering_fields = ['singer', 'last_performed', 'perform_count', 'first_perform']
            # 处理降序字段（以-开头）
            order_field = ordering.lstrip('-')
            if order_field in allowed_ordering_fields:
                queryset = queryset.order_by(ordering)

        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_num)

        # 序列化数据
        serializer = self.get_serializer(page, many=True)

        # 构造缓存key
        cache_key = f"song_list_api:{query}:{page_num}:{page_size}:{ordering}:{'-'.join(styles)}:{'-'.join(tags)}:{'-'.join(languages)}"

        # 尝试缓存结果，处理Redis连接异常
        try:
            cache.set(cache_key, serializer.data, 600)  # 缓存10分钟
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

        return paginated_response(
            data=serializer.data,
            total=paginator.count,
            page=page.number,
            page_size=page_size,
            message="获取歌曲列表成功"
        )
