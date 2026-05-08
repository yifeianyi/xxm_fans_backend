from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.utils import timezone
from ..models import WorkStatic, WorkMetricsHour, Account, FollowerMetrics


class CorrelationService:

    @staticmethod
    def get_correlation_data(
        account_id: int,
        days: int = 90
    ) -> Dict:
        end_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days - 1)

        window_works = WorkStatic.objects.filter(
            is_valid=True,
            publish_time__gte=start_date,
            publish_time__lte=end_date,
        ).order_by('publish_time')

        works_info = []
        work_ids = []
        for w in window_works:
            works_info.append({
                'title': w.title,
                'publishTime': w.publish_time.strftime('%Y-%m-%d'),
                'coverUrl': w.cover_url or '',
                'platform': w.platform,
                'workId': w.work_id,
            })
            work_ids.append((w.platform, w.work_id))

        view_deltas = CorrelationService._compute_view_deltas(work_ids, start_date, end_date)
        follower_deltas = CorrelationService._compute_follower_deltas(account_id, start_date, end_date)

        timeline = []
        current = start_date
        for i in range(days):
            day_str = current.strftime('%Y-%m-%d')
            timeline.append({
                'time': day_str,
                'videoViewDelta': view_deltas.get(day_str, 0),
                'followerDelta': follower_deltas.get(day_str, 0),
            })
            current += timedelta(days=1)

        return {
            'timeline': timeline,
            'works': works_info,
        }

    @staticmethod
    def _compute_view_deltas(
        work_ids: List[tuple],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        view_sums = {}
        current = start_date - timedelta(days=1)
        view_sums[current.strftime('%Y-%m-%d')] = 0

        current = start_date
        while current <= end_date:
            day_end = current + timedelta(days=1) - timedelta(seconds=1)
            day_str = current.strftime('%Y-%m-%d')

            daily_sum = 0
            for platform, wid in work_ids:
                metric = WorkMetricsHour.objects.filter(
                    platform=platform,
                    work_id=wid,
                    crawl_time__lte=day_end
                ).order_by('-crawl_time').first()
                if metric:
                    daily_sum += metric.view_count

            prev_str = (current - timedelta(days=1)).strftime('%Y-%m-%d')
            prev_sum = view_sums.get(prev_str, daily_sum)
            view_sums[day_str] = daily_sum
            view_sums[f"{day_str}_delta"] = daily_sum - prev_sum
            current += timedelta(days=1)

        return {current.strftime('%Y-%m-%d'): view_sums.get(f"{current.strftime('%Y-%m-%d')}_delta", 0)
                for current in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))}

    @staticmethod
    def _compute_follower_deltas(
        account_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        account = Account.objects.filter(id=account_id, is_active=True).first()
        if not account:
            return {}

        previous_count: Optional[int] = None
        deltas = {}
        current = start_date
        while current <= end_date:
            day_end = current + timedelta(days=1) - timedelta(seconds=1)
            day_str = current.strftime('%Y-%m-%d')
            metric = FollowerMetrics.objects.filter(
                account_id=account_id,
                crawl_time__lte=day_end
            ).order_by('-crawl_time').first()
            count = metric.follower_count if metric else 0
            deltas[day_str] = count - previous_count if previous_count is not None else 0
            previous_count = count
            current += timedelta(days=1)
        return deltas
