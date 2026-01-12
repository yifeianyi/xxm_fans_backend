"""
数据分析服务
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Sum, Max, Min, Count
from django.core.cache import cache
from core.cache import cache_result
from core.exceptions import InvalidParameterException
from ..models import WorkStatic, WorkMetricsHour, CrawlSession


class AnalyticsService:
    """数据分析服务类"""

    @staticmethod
    def get_work_list(
        platform: Optional[str] = None,
        is_valid: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取作品列表

        Args:
            platform: 平台筛选
            is_valid: 是否有效筛选
            limit: 返回数量
            offset: 偏移量

        Returns:
            作品列表
        """
        queryset = WorkStatic.objects.all()

        if platform:
            queryset = queryset.filter(platform=platform)

        if is_valid is not None:
            queryset = queryset.filter(is_valid=is_valid)

        queryset = queryset.order_by('-publish_time')

        return list(queryset[offset:offset + limit].values())

    @staticmethod
    @cache_result(timeout=300, key_prefix="work_detail")
    def get_work_detail(platform: str, work_id: str) -> Optional[Dict[str, Any]]:
        """
        获取作品详情

        Args:
            platform: 平台
            work_id: 作品ID

        Returns:
            作品详情
        """
        try:
            work = WorkStatic.objects.get(platform=platform, work_id=work_id)
            return {
                'platform': work.platform,
                'work_id': work.work_id,
                'title': work.title,
                'author': work.author,
                'publish_time': work.publish_time,
                'cover_url': work.cover_url,
                'is_valid': work.is_valid,
            }
        except WorkStatic.DoesNotExist:
            return None

    @staticmethod
    def get_work_metrics(
        platform: str,
        work_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        获取作品指标数据

        Args:
            platform: 平台
            work_id: 作品ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            指标数据列表
        """
        queryset = WorkMetricsHour.objects.filter(
            platform=platform,
            work_id=work_id
        )

        if start_time:
            queryset = queryset.filter(crawl_time__gte=start_time)

        if end_time:
            queryset = queryset.filter(crawl_time__lte=end_time)

        queryset = queryset.order_by('crawl_time')

        return list(queryset.values())

    @staticmethod
    @cache_result(timeout=600, key_prefix="work_metrics_summary")
    def get_work_metrics_summary(
        platform: str,
        work_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取作品指标汇总

        Args:
            platform: 平台
            work_id: 作品ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            指标汇总数据
        """
        queryset = WorkMetricsHour.objects.filter(
            platform=platform,
            work_id=work_id
        )

        if start_time:
            queryset = queryset.filter(crawl_time__gte=start_time)

        if end_time:
            queryset = queryset.filter(crawl_time__lte=end_time)

        summary = queryset.aggregate(
            max_view=Max('view_count'),
            max_like=Max('like_count'),
            max_coin=Max('coin_count'),
            max_favorite=Max('favorite_count'),
            max_danmaku=Max('danmaku_count'),
            max_comment=Max('comment_count'),
            avg_view=Avg('view_count'),
            avg_like=Avg('like_count'),
            avg_coin=Avg('coin_count'),
            avg_favorite=Avg('favorite_count'),
            avg_danmaku=Avg('danmaku_count'),
            avg_comment=Avg('comment_count'),
            count=Count('id'),
        )

        return summary

    @staticmethod
    def get_crawl_sessions(
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取爬取会话列表

        Args:
            source: 数据源筛选
            limit: 返回数量
            offset: 偏移量

        Returns:
            爬取会话列表
        """
        queryset = CrawlSession.objects.all()

        if source:
            queryset = queryset.filter(source=source)

        queryset = queryset.order_by('-start_time')

        return list(queryset[offset:offset + limit].values())

    @staticmethod
    @cache_result(timeout=300, key_prefix="crawl_session_detail")
    def get_crawl_session_detail(session_id: int) -> Optional[Dict[str, Any]]:
        """
        获取爬取会话详情

        Args:
            session_id: 会话ID

        Returns:
            会话详情
        """
        try:
            session = CrawlSession.objects.get(id=session_id)
            return {
                'id': session.id,
                'source': session.source,
                'node_id': session.node_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'total_work_count': session.total_work_count,
                'success_count': session.success_count,
                'fail_count': session.fail_count,
                'note': session.note,
            }
        except CrawlSession.DoesNotExist:
            return None

    @staticmethod
    def get_platform_statistics(
        platform: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取平台统计数据

        Args:
            platform: 平台
            days: 统计天数

        Returns:
            平台统计数据
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # 作品统计
        work_stats = WorkStatic.objects.filter(
            platform=platform,
            publish_time__gte=start_time
        ).aggregate(
            total_works=Count('id'),
            valid_works=Count('id', filter=Q(is_valid=True)),
        )

        # 指标统计
        metrics_stats = WorkMetricsHour.objects.filter(
            platform=platform,
            crawl_time__gte=start_time
        ).aggregate(
            total_views=Sum('view_count'),
            total_likes=Sum('like_count'),
            total_coins=Sum('coin_count'),
            total_favorites=Sum('favorite_count'),
            avg_views=Avg('view_count'),
            avg_likes=Avg('like_count'),
        )

        # 爬取会话统计
        session_stats = CrawlSession.objects.filter(
            source=platform,
            start_time__gte=start_time
        ).aggregate(
            total_sessions=Count('id'),
            total_success=Sum('success_count'),
            total_fail=Sum('fail_count'),
        )

        return {
            'platform': platform,
            'period': f'{days} days',
            'works': work_stats,
            'metrics': metrics_stats,
            'sessions': session_stats,
        }

    @staticmethod
    def get_top_works(
        platform: str,
        metric: str = 'view_count',
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取热门作品

        Args:
            platform: 平台
            metric: 指标类型 (view_count, like_count, coin_count, favorite_count)
            limit: 返回数量
            days: 统计天数

        Returns:
            热门作品列表
        """
        valid_metrics = ['view_count', 'like_count', 'coin_count', 'favorite_count']
        if metric not in valid_metrics:
            raise InvalidParameterException(f"无效的指标类型: {metric}")

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # 获取最新指标数据
        metrics = WorkMetricsHour.objects.filter(
            platform=platform,
            crawl_time__gte=start_time
        ).values('work_id').annotate(
            max_value=Max(metric)
        ).order_by('-max_value')[:limit]

        # 获取作品详情
        work_ids = [m['work_id'] for m in metrics]
        works = WorkStatic.objects.filter(
            platform=platform,
            work_id__in=work_ids
        ).values()

        # 合并数据
        work_dict = {w['work_id']: w for w in works}
        result = []
        for m in metrics:
            work = work_dict.get(m['work_id'])
            if work:
                result.append({
                    **work,
                    metric: m['max_value'],
                })

        return result