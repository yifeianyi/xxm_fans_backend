from django.db.models import Count, Sum, Q, F
from django.db.models.functions import Cast, Coalesce
from django.db.models import FloatField, IntegerField
from ..models import FanProfile, LiveAttendance
from livestream.models import Livestream
from typing import Optional, Tuple

try:
    from django.core.cache import cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class FanRankingService:
    """粉丝排名计算服务 - 排名从2026年开始，之前年份数据未收录"""

    RANKING_START_YEAR = 2026
    ROOM_ID = '8777'
    RANK_CACHE_TTL = 300

    @classmethod
    def _get_bilibili_livestreams(cls, year: Optional[int] = None):
        """获取B站直播场次，仅2026年及之后"""
        qs = Livestream.objects.filter(
            is_active=True
        ).exclude(
            Q(room_id='') | Q(room_id__isnull=True)
        ).filter(date__year__gte=cls.RANKING_START_YEAR)
        if year and year >= cls.RANKING_START_YEAR:
            qs = qs.filter(date__year=year)
        elif year and year < cls.RANKING_START_YEAR:
            return Livestream.objects.none()
        return qs

    @classmethod
    def get_total_livestream_count(cls, year: Optional[int] = None) -> int:
        """获取统计期内的B站直播总场数"""
        return cls._get_bilibili_livestreams(year).count()

    @classmethod
    def get_attendance_ranking(
        cls,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[list, int]:
        """
        出勤率排名
        出勤率 = 该用户 is_attended=True 的直播数 / 统计期内总直播数 × 100%
        同一排名允许多人并列
        """
        total_livestreams = cls.get_total_livestream_count(year)
        if total_livestreams == 0:
            return [], 0

        attendance_filter = Q(attendances__is_attended=True)
        if year:
            attendance_filter &= Q(attendances__livestream__date__year=year)

        queryset = (
            FanProfile.objects
            .annotate(
                attended_count=Count(
                    'attendances',
                    filter=attendance_filter
                )
            )
            .annotate(
                total_danmaku=Coalesce(
                    Sum(
                        'attendances__danmaku_count',
                        filter=Q(attendances__is_attended=True)
                        & (Q(attendances__livestream__date__year=year) if year else Q())
                    ),
                    0
                )
            )
            .annotate(
                attendance_rate=Cast(
                    F('attended_count') * 100.0 / total_livestreams,
                    FloatField()
                )
            )
            .filter(attended_count__gt=0)
            .order_by('-attendance_rate')
        )

        total = queryset.count()
        start = (page - 1) * page_size
        profiles = queryset[start:start + page_size]

        result = []
        current_rank = 0
        last_rate = None

        for idx, profile in enumerate(profiles, start=start):
            rate = round(profile.attendance_rate, 2)
            if rate != last_rate:
                current_rank = idx + 1
                last_rate = rate

            result.append({
                'rank': current_rank,
                'uid': profile.bilibili_uid,
                'username': profile.username,
                'avatar_url': profile.avatar_url or '',
                'attendance_rate': rate,
                'attended_count': profile.attended_count,
                'total_livestreams': total_livestreams,
                'total_danmaku': profile.total_danmaku,
            })

        return result, total

    @classmethod
    def get_danmaku_ranking(
        cls,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[list, int]:
        """
        弹幕排名
        按弹幕数量降序排列，同一排名只有一个人
        """
        danmaku_filter = Q(attendances__danmaku_count__gt=0)
        if year:
            danmaku_filter &= Q(attendances__livestream__date__year=year)

        queryset = (
            FanProfile.objects
            .annotate(
                total_danmaku=Coalesce(
                    Sum('attendances__danmaku_count', filter=danmaku_filter),
                    0
                )
            )
            .filter(total_danmaku__gt=0)
            .order_by('-total_danmaku')
        )

        total = queryset.count()

        all_danmaku_sum = queryset.aggregate(
            s=Coalesce(Sum('total_danmaku'), 0)
        )['s']

        start = (page - 1) * page_size
        profiles = queryset[start:start + page_size]

        result = []
        for idx, profile in enumerate(profiles, start=start):
            percentage = (
                round(profile.total_danmaku * 100.0 / all_danmaku_sum, 2)
                if all_danmaku_sum > 0
                else 0
            )
            result.append({
                'rank': idx + 1,
                'uid': profile.bilibili_uid,
                'username': profile.username,
                'avatar_url': profile.avatar_url or '',
                'danmaku_count': profile.total_danmaku,
                'percentage': percentage,
            })

        return result, total

    @classmethod
    def _build_rank_map(cls, queryset, key_field='bilibili_uid'):
        rank_map = {}
        for idx, profile in enumerate(queryset):
            uid = getattr(profile, key_field)
            if uid not in rank_map:
                rank_map[uid] = idx + 1
        return rank_map

    @classmethod
    def _cache_get(cls, key):
        if not CACHE_AVAILABLE:
            return None
        try:
            return cache.get(key)
        except Exception:
            return None

    @classmethod
    def _cache_set(cls, key, value, ttl):
        if not CACHE_AVAILABLE:
            return
        try:
            cache.set(key, value, ttl)
        except Exception:
            pass

    @classmethod
    def _get_cached_rank_maps(cls, year):
        cache_key = 'livefans:rank_maps'
        cached = cls._cache_get(cache_key)
        if cached is not None:
            return cached

        year_attendance_ranked = (
            FanProfile.objects
            .annotate(
                year_attended=Count(
                    'attendances',
                    filter=Q(attendances__is_attended=True, attendances__livestream__date__year=year)
                )
            )
            .filter(year_attended__gt=0)
            .order_by('-year_attended')
        )
        year_attendance_rank_map = cls._build_rank_map(year_attendance_ranked)

        year_danmaku_ranked = (
            FanProfile.objects
            .annotate(
                year_danmaku=Coalesce(
                    Sum('attendances__danmaku_count',
                        filter=Q(attendances__danmaku_count__gt=0, attendances__livestream__date__year=year)),
                    0
                )
            )
            .filter(year_danmaku__gt=0)
            .order_by('-year_danmaku')
        )
        year_danmaku_rank_map = cls._build_rank_map(year_danmaku_ranked)

        overall_attendance_ranked = (
            FanProfile.objects
            .annotate(
                overall_attended=Count(
                    'attendances',
                    filter=Q(attendances__is_attended=True)
                )
            )
            .filter(overall_attended__gt=0)
            .order_by('-overall_attended')
        )
        overall_attendance_rank_map = cls._build_rank_map(overall_attendance_ranked)

        rank_maps = {
            'year_attendance': year_attendance_rank_map,
            'year_danmaku': year_danmaku_rank_map,
            'overall_attendance': overall_attendance_rank_map,
        }
        cls._cache_set(cache_key, rank_maps, cls.RANK_CACHE_TTL)
        return rank_maps

    @classmethod
    def search_fans(
        cls,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[list, int]:
        """搜索粉丝（按用户名或UID），返回年度+综合排名数据"""
        year = cls.RANKING_START_YEAR
        overall_livestreams = cls.get_total_livestream_count()
        year_livestreams = cls.get_total_livestream_count(year)

        rank_maps = cls._get_cached_rank_maps(year)
        year_attendance_rank_map = rank_maps['year_attendance']
        year_danmaku_rank_map = rank_maps['year_danmaku']
        overall_attendance_rank_map = rank_maps['overall_attendance']

        queryset = (
            FanProfile.objects
            .annotate(
                overall_attended=Count(
                    'attendances',
                    filter=Q(attendances__is_attended=True)
                )
            )
            .annotate(
                overall_danmaku=Coalesce(
                    Sum('attendances__danmaku_count'),
                    0
                )
            )
            .annotate(
                year_attended=Count(
                    'attendances',
                    filter=Q(attendances__is_attended=True, attendances__livestream__date__year=year)
                )
            )
            .annotate(
                year_danmaku=Coalesce(
                    Sum('attendances__danmaku_count',
                        filter=Q(attendances__livestream__date__year=year)),
                    0
                )
            )
            .filter(
                Q(username__icontains=query) | Q(bilibili_uid__icontains=query)
            )
            .order_by('-overall_attended')
        )

        total = queryset.count()
        start = (page - 1) * page_size
        profiles = queryset[start:start + page_size]

        result = []
        for p in profiles:
            uid = p.bilibili_uid
            result.append({
                'uid': uid,
                'username': p.username,
                'avatar_url': p.avatar_url or '',
                'fan_badge_level': p.fan_badge_level,
                'year_attendance_rate': round(p.year_attended * 100.0 / year_livestreams, 2) if year_livestreams > 0 else 0,
                'year_attendance_rank': year_attendance_rank_map.get(uid),
                'year_danmaku_count': p.year_danmaku,
                'year_danmaku_rank': year_danmaku_rank_map.get(uid),
                'overall_attendance_rate': round(p.overall_attended * 100.0 / overall_livestreams, 2) if overall_livestreams > 0 else 0,
                'overall_attendance_rank': overall_attendance_rank_map.get(uid),
            })

        return result, total

    @classmethod
    def get_fan_profile(cls, uid: str) -> Optional[dict]:
        """获取粉丝详情（含各场直播记录）"""
        try:
            profile = (
                FanProfile.objects
                .prefetch_related('attendances__livestream')
                .get(bilibili_uid=uid)
            )
        except FanProfile.DoesNotExist:
            return None

        total_livestreams = cls._get_bilibili_livestreams().count()
        attended_count = profile.attendances.filter(is_attended=True).count()

        attendance_records = [
            {
                'date': a.livestream.date.strftime('%Y-%m-%d'),
                'title': a.livestream.title,
                'is_attended': a.is_attended,
                'has_danmaku': a.has_danmaku,
                'danmaku_count': a.danmaku_count,
                'has_gift': a.has_gift,
                'has_sc': a.has_sc,
                'has_guard': a.has_guard,
                'watch_duration_minutes': a.watch_duration_minutes,
            }
            for a in profile.attendances.select_related('livestream').order_by('-livestream__date')
        ]

        return {
            'uid': profile.bilibili_uid,
            'username': profile.username,
            'avatar_url': profile.avatar_url or '',
            'first_seen_at': profile.first_seen_at.strftime('%Y-%m-%d %H:%M') if profile.first_seen_at else None,
            'attended_count': attended_count,
            'total_livestreams': total_livestreams,
            'attendance_rate': round(attended_count * 100.0 / total_livestreams, 2) if total_livestreams > 0 else 0,
            'total_danmaku': sum(a.danmaku_count for a in profile.attendances.all()),
            'records': attendance_records,
        }

    @classmethod
    def get_stats(cls) -> dict:
        """获取统计概览（仅B站直播相关）"""
        bilibili_livestreams = cls._get_bilibili_livestreams()
        total_fans = FanProfile.objects.count()
        total_livestreams = bilibili_livestreams.count()
        total_attendances = (
            LiveAttendance.objects
            .filter(is_attended=True, livestream__in=bilibili_livestreams)
            .count()
        )
        total_danmaku = (
            LiveAttendance.objects
            .filter(livestream__in=bilibili_livestreams)
            .aggregate(s=Coalesce(Sum('danmaku_count'), 0))['s']
        )

        return {
            'total_fans': total_fans,
            'total_livestreams': total_livestreams,
            'total_attendances': total_attendances,
            'total_danmaku': total_danmaku,
            'fans_label': '出勤粉丝',
        }

    @classmethod
    def invalidate_rank_cache(cls):
        if not CACHE_AVAILABLE:
            return
        try:
            cache.delete('livefans:rank_maps')
        except Exception:
            pass
