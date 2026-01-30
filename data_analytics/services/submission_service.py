"""
投稿时刻功能业务逻辑服务
"""
from django.db.models import Count, Q, Min, Max
from django.utils import timezone
from data_analytics.models.work_static import WorkStatic


class SubmissionService:
    """投稿业务逻辑服务"""

    @staticmethod
    def get_monthly_submission_stats(year, platform=None):
        """
        获取月度投稿统计

        Args:
            year: 年份
            platform: 平台筛选（可选）

        Returns:
            dict: 月度统计数据
        """
        # 构建查询条件
        queryset = WorkStatic.objects.filter(
            publish_time__year=year
        )

        if platform:
            queryset = queryset.filter(platform=platform)

        # 按月聚合统计
        stats = queryset.values('publish_time__month').annotate(
            total=Count('id'),
            valid=Count('id', filter=Q(is_valid=True)),
            invalid=Count('id', filter=Q(is_valid=False)),
            first_submission=Min('publish_time'),
            last_submission=Max('publish_time')
        ).order_by('publish_time__month')

        # 转换为字典格式
        monthly_stats = []
        for stat in stats:
            monthly_stats.append({
                'month': stat['publish_time__month'],
                'total': stat['total'],
                'valid': stat['valid'],
                'invalid': stat['invalid'],
                'first_submission': stat['first_submission'],
                'last_submission': stat['last_submission']
            })

        # 计算年度汇总
        year_summary = {
            'total_submissions': queryset.count(),
            'valid_submissions': queryset.filter(is_valid=True).count(),
            'invalid_submissions': queryset.filter(is_valid=False).count(),
            'active_months': len(monthly_stats)
        }

        return {
            'year': year,
            'platform': platform,
            'monthly_stats': monthly_stats,
            'year_summary': year_summary
        }

    @staticmethod
    def get_monthly_submission_records(year, month, platform=None, is_valid=None, page=1, page_size=20):
        """
        获取月度投稿记录

        Args:
            year: 年份
            month: 月份
            platform: 平台筛选（可选）
            is_valid: 是否有效投稿（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            dict: 月度投稿记录数据
        """
        # 构建查询条件
        queryset = WorkStatic.objects.filter(
            publish_time__year=year,
            publish_time__month=month
        )

        if platform:
            queryset = queryset.filter(platform=platform)

        if is_valid is not None:
            queryset = queryset.filter(is_valid=is_valid)

        # 获取总数
        total = queryset.count()

        # 计算分页
        page_size = min(page_size, 100)  # 限制最大每页数量
        offset = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size

        # 分页查询
        records = queryset.order_by('publish_time')[offset:offset + page_size]

        return {
            'year': year,
            'month': month,
            'platform': platform,
            'records': records,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    @staticmethod
    def get_years_submission_overview(platform=None, start_year=None, end_year=None):
        """
        获取年度投稿概览

        Args:
            platform: 平台筛选（可选）
            start_year: 起始年份（可选，不传则自动从最早投稿年份开始）
            end_year: 结束年份（可选，不传则自动到当前年份）

        Returns:
            dict: 年度投稿概览数据
        """
        # 构建查询条件
        queryset = WorkStatic.objects.all()

        if platform:
            queryset = queryset.filter(platform=platform)

        # 如果没有指定年份范围，则自动确定
        if not start_year or not end_year:
            # 获取数据库中的最早和最晚投稿年份
            year_range = queryset.aggregate(
                min_year=Min('publish_time__year'),
                max_year=Max('publish_time__year')
            )
            if not start_year:
                start_year = year_range['min_year'] or timezone.now().year
            if not end_year:
                end_year = year_range['max_year'] or timezone.now().year

        # 应用年份范围筛选
        queryset = queryset.filter(
            publish_time__year__gte=start_year,
            publish_time__year__lte=end_year
        )

        # 按年聚合统计
        stats = queryset.values('publish_time__year').annotate(
            total_submissions=Count('id'),
            valid_submissions=Count('id', filter=Q(is_valid=True)),
            invalid_submissions=Count('id', filter=Q(is_valid=False)),
            active_months=Count('publish_time__month', distinct=True),
            first_submission=Min('publish_time'),
            last_submission=Max('publish_time')
        ).order_by('publish_time__year')

        # 转换为字典格式
        years = []
        for stat in stats:
            years.append({
                'year': stat['publish_time__year'],
                'total_submissions': stat['total_submissions'],
                'valid_submissions': stat['valid_submissions'],
                'invalid_submissions': stat['invalid_submissions'],
                'active_months': stat['active_months'],
                'first_submission': stat['first_submission'],
                'last_submission': stat['last_submission']
            })

        # 计算总体汇总
        summary = {
            'total_years': len(years),
            'total_submissions': queryset.count(),
            'valid_submissions': queryset.filter(is_valid=True).count(),
            'invalid_submissions': queryset.filter(is_valid=False).count()
        }

        return {
            'platform': platform,
            'years': years,
            'summary': summary
        }