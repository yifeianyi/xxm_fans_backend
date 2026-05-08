from django.core.paginator import Paginator
from rest_framework import generics
from core.responses import success_response, paginated_response
from core.exceptions import SongNotFoundException
from ..models import SongRecord, Song
from .serializers import SongRecordSerializer
from django.core.cache import cache
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SongRecordListView(generics.ListAPIView):
    serializer_class = SongRecordSerializer

    def get_queryset(self):
        song_id = self.kwargs['song_id']
        return SongRecord.objects.filter(
            song_id=song_id
        ).select_related('song').order_by('-performed_at')

    def _enrich_with_likes(self, results, request):
        record_ids = [r['id'] for r in results]
        if not record_ids:
            return results

        from ..models import SongRecordLike
        from django.db.models import Count

        like_counts = dict(
            SongRecordLike.objects.filter(song_record_id__in=record_ids)
            .values('song_record_id')
            .annotate(count=Count('id'))
            .values_list('song_record_id', 'count')
        )

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '')
        user_likes = set(
            SongRecordLike.objects.filter(song_record_id__in=record_ids, ip_address=ip)
            .values_list('song_record_id', flat=True)
        )

        for record in results:
            rid = record['id']
            record['like_count'] = like_counts.get(rid, 0)
            record['user_liked'] = rid in user_likes

        return results

    def list(self, request, *args, **kwargs):
        song_id = self.kwargs['song_id']
        page_num = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        sort_by = request.GET.get("sort_by", "time")

        cache_key = f"song_records:{song_id}:{page_num}:{page_size}:{sort_by}"

        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return success_response(data=cached_data, message="获取演唱记录成功（缓存）")
        except Exception as e:
            logger.warning(f"Cache get failed for song records: {e}")

        try:
            queryset = self.get_queryset()

            if sort_by == 'likes':
                page_num = 1  # likes排序不支持分页缓存，返回第一页
                all_records = list(queryset)
                serializer = self.get_serializer(all_records, many=True)
                results = list(serializer.data)
                results = self._enrich_with_likes(results, request)
                results.sort(key=lambda r: r.get('like_count', 0), reverse=True)

                total = len(results)
                start = (page_num - 1) * page_size
                end = start + page_size
                results = results[start:end]
            else:
                paginator = Paginator(queryset, page_size)
                page = paginator.get_page(page_num)
                serializer = self.get_serializer(page, many=True)
                results = list(serializer.data)
                results = self._enrich_with_likes(results, request)
                total = paginator.count

            for record in results:
                performed_at = record.get('performed_at')
                if performed_at:
                    date = datetime.strptime(performed_at, "%Y-%m-%d").date()
                    date_str = date.strftime("%Y-%m-%d")
                    year = date.strftime("%Y")
                    month = date.strftime("%m")
                    record["cover_url"] = record.get("cover_url") or f"/covers/{year}/{month}/{date_str}.jpg"
                else:
                    record["cover_url"] = "/covers/default.jpg"

            paginated_data = {
                'results': results,
                'total': total,
                'page': page_num,
                'page_size': page_size
            }

            try:
                cache.set(cache_key, paginated_data, 600)
            except Exception as e:
                logger.warning(f"Cache set failed for song records: {e}")

            return paginated_response(
                data=results,
                total=total,
                page=page_num,
                page_size=page_size,
                message="获取演唱记录成功"
            )
        except Song.DoesNotExist:
            raise SongNotFoundException(f"歌曲不存在: {song_id}")
