"""
演唱记录相关视图
"""
from django.core.paginator import Paginator
from rest_framework import generics
from rest_framework.views import APIView
from core.responses import success_response, paginated_response
from core.exceptions import SongNotFoundException
from ..models import SongRecord
from .serializers import SongRecordSerializer
from django.core.cache import cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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

        # 尝试从缓存获取完整的分页数据，处理Redis连接异常
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                # 缓存中存储完整的分页对象
                return success_response(data=cached_data, message="获取演唱记录成功（缓存）")
        except Exception as e:
            logger.warning(f"Cache get failed for song records: {e}")

        # 调用父类方法获取数据
        try:
            queryset = self.get_queryset()
            paginator = Paginator(queryset, page_size)
            page = paginator.get_page(page_num)

            serializer = self.get_serializer(page, many=True)

            # 处理封面URL
            results = []
            for record in serializer.data:
                performed_at = record.get('performed_at')
                if performed_at:
                    date = datetime.strptime(performed_at, "%Y-%m-%d").date()
                    date_str = date.strftime("%Y-%m-%d")
                    year = date.strftime("%Y")
                    month = date.strftime("%m")
                    record["cover_url"] = record.get("cover_url") or f"/covers/{year}/{month}/{date_str}.jpg"
                else:
                    record["cover_url"] = "/covers/default.jpg"
                results.append(record)

            # 构建完整的分页响应对象
            paginated_data = {
                'results': results,
                'total': paginator.count,
                'page': page.number,
                'page_size': page_size
            }

            # 缓存完整的分页对象，处理Redis连接异常
            try:
                cache.set(cache_key, paginated_data, 600)
            except Exception as e:
                logger.warning(f"Cache set failed for song records: {e}")

            return paginated_response(
                data=results,
                total=paginator.count,
                page=page.number,
                page_size=page_size,
                message="获取演唱记录成功"
            )
        except Song.DoesNotExist:
            raise SongNotFoundException(f"歌曲不存在: {song_id}")


class SongRecordsByDateView(APIView):
    """
    获取特定日期的所有演唱记录
    """
    def get(self, request):
        date_str = request.GET.get('date')
        if not date_str:
            return success_response(data=[], message="缺少日期参数")

        try:
            # 验证日期格式
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return success_response(data=[], message="日期格式错误")

        # 构造缓存key
        cache_key = f"records_by_date:{date_str}"

        # 尝试从缓存获取
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return success_response(data=cached_data, message="获取当日演唱记录成功（缓存）")
        except Exception as e:
            logger.warning(f"Cache get failed for records by date: {e}")

        # 查询该日期的所有演唱记录
        queryset = SongRecord.objects.filter(performed_at=date_obj).select_related('song').order_by('id')
        logger.info(f"查询日期 {date_obj} 的演唱记录，共 {queryset.count()} 条")
        serializer = SongRecordSerializer(queryset, many=True)

        # 处理数据，添加歌曲名称等信息
        results = []
        for record in serializer.data:
            logger.debug(f"处理演唱记录: {record}")
            performed_at = record.get('performed_at')
            if performed_at:
                date = datetime.strptime(performed_at, "%Y-%m-%d").date()
                date_str = date.strftime("%Y-%m-%d")
                year = date.strftime("%Y")
                month = date.strftime("%m")
                record["cover_url"] = record.get("cover_url") or f"/covers/{year}/{month}/{date_str}.jpg"
            else:
                record["cover_url"] = "/covers/default.jpg"
            
            # 添加歌曲名称
            song_name = record.get('song', {}).get('song_name', '未知歌曲')
            record['song_name'] = song_name
            
            results.append(record)
        
        logger.info(f"返回 {len(results)} 条演唱记录")

        # 缓存结果
        try:
            cache.set(cache_key, results, 600)
        except Exception as e:
            logger.warning(f"Cache set failed for records by date: {e}")

        return success_response(data=results, message="获取当日演唱记录成功")
