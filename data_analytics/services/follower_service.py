"""
粉丝数据服务
处理粉丝数据的查询和聚合，支持预生成缓存
"""
from django.db.models import F
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from ..models import Account, FollowerMetrics


class FollowerService:
    """粉丝数据服务类"""

    # 缓存目录
    CACHE_DIR = 'data/cache/followers'
    CACHE_EXPIRY_MINUTES = 60

    @staticmethod
    def get_all_accounts() -> List[Dict]:
        """
        获取所有启用的账号列表

        Returns:
            List[Dict]: 账号列表
        """
        accounts = Account.objects.filter(is_active=True).order_by('id')
        return [
            {
                'id': str(acc.id),
                'name': acc.name,
                'uid': acc.uid,
                'platform': acc.platform
            }
            for acc in accounts
        ]

    @staticmethod
    def get_account_by_id(account_id: int) -> Optional[Account]:
        """
        根据 ID 获取账号

        Args:
            account_id: 账号 ID

        Returns:
            Account: 账号对象
        """
        try:
            return Account.objects.get(id=account_id, is_active=True)
        except Account.DoesNotExist:
            return None

    @staticmethod
    def get_current_follower_count(account_id: int) -> Optional[int]:
        """
        获取账号当前粉丝数

        Args:
            account_id: 账号 ID

        Returns:
            Optional[int]: 当前粉丝数
        """
        try:
            latest = FollowerMetrics.objects.filter(
                account_id=account_id
            ).order_by('-crawl_time').first()
            return latest.follower_count if latest else None
        except Exception:
            return None

    @staticmethod
    def get_follower_history(
        account_id: int,
        granularity: str = 'WEEK',
        days: int = 30
    ) -> List[Dict]:
        """
        获取账号粉丝数历史数据

        Args:
            account_id: 账号 ID
            granularity: 时间粒度 ('DAY', 'WEEK', 'MONTH')
            days: 查询天数

        Returns:
            List[Dict]: 历史数据列表
        """
        account = FollowerService.get_account_by_id(account_id)
        if not account:
            return []

        # 计算时间范围
        end_time = timezone.now()
        if granularity == 'DAY':
            start_time = end_time - timedelta(hours=days)
            trunc_func = TruncHour('crawl_time')
        elif granularity == 'WEEK':
            start_time = end_time - timedelta(days=days)
            trunc_func = TruncDay('crawl_time')
        elif granularity == 'MONTH':
            start_time = end_time - timedelta(days=days)
            trunc_func = TruncDay('crawl_time')
        else:
            raise ValueError(f"Invalid granularity: {granularity}")

        # 查询并聚合数据
        queryset = FollowerMetrics.objects.filter(
            account=account,
            crawl_time__gte=start_time,
            crawl_time__lte=end_time
        ).annotate(
            time_bucket=trunc_func
        ).values('time_bucket').annotate(
            follower_count=F('follower_count')
        ).order_by('time_bucket')

        # 计算增量
        result = []
        prev_value = None

        for item in queryset:
            current_value = item['follower_count']
            delta = current_value - prev_value if prev_value is not None else 0

            # 格式化时间
            time_str = item['time_bucket'].strftime('%Y-%m-%d %H:%M:%S')
            if granularity == 'DAY':
                time_str = item['time_bucket'].strftime('%H:00')
            elif granularity == 'WEEK':
                time_str = item['time_bucket'].strftime('%Y/%m/%d')
            elif granularity == 'MONTH':
                time_str = item['time_bucket'].strftime('%Y/%m/%d')

            result.append({
                'time': time_str,
                'value': current_value,
                'delta': delta
            })

            prev_value = current_value

        return result

    # ==================== 缓存管理方法 ====================

    @staticmethod
    def _get_cache_file_path(granularity: str) -> str:
        """获取缓存文件路径"""
        os.makedirs(FollowerService.CACHE_DIR, exist_ok=True)
        return os.path.join(FollowerService.CACHE_DIR, f'accounts_{granularity.lower()}.json')

    @staticmethod
    def _is_cache_valid(cache_file: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_file):
            return False
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return (datetime.now() - file_time).total_seconds() < FollowerService.CACHE_EXPIRY_MINUTES * 60

    @staticmethod
    def _load_from_cache(cache_file: str) -> Optional[Dict]:
        """从缓存加载数据"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return {
                'data': cache_data,
                'cached_at': datetime.fromtimestamp(os.path.getmtime(cache_file)).isoformat()
            }
        except Exception:
            return None

    @staticmethod
    def _save_to_cache(cache_file: str, data: List[Dict]):
        """保存数据到缓存"""
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def generate_cache(granularity: str = 'WEEK'):
        """生成指定粒度的缓存"""
        # 根据粒度设置默认天数
        days_map = {'DAY': 24, 'WEEK': 7, 'MONTH': 30}
        days = days_map.get(granularity, 30)
        data = FollowerService.get_all_accounts_data(granularity, days=days, use_cache=False)
        cache_file = FollowerService._get_cache_file_path(granularity)
        FollowerService._save_to_cache(cache_file, data)
        print(f"✓ 缓存已生成: {granularity} ({len(data)} 个账号), 天数: {days}")

    @staticmethod
    def generate_all_caches():
        """生成所有粒度的缓存"""
        print("开始预生成所有粒度的缓存...")
        for granularity in ['DAY', 'WEEK', 'MONTH']:
            FollowerService.generate_cache(granularity)
        print("所有缓存预生成完成")

    @staticmethod
    def get_all_accounts_data(
        granularity: str = 'WEEK',
        days: int = 30,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        获取所有账号的完整数据（优先使用缓存）

        Args:
            granularity: 时间粒度
            days: 查询天数
            use_cache: 是否使用缓存

        Returns:
            List[Dict]: 账号数据列表
        """
        # 尝试从缓存读取
        if use_cache:
            cache_file = FollowerService._get_cache_file_path(granularity)
            if FollowerService._is_cache_valid(cache_file):
                cached_data = FollowerService._load_from_cache(cache_file)
                if cached_data:
                    print(f"使用缓存数据: {granularity}")
                    return cached_data['data']

        # 缓存无效或未启用，从数据库查询
        accounts = FollowerService.get_all_accounts()
        result = []

        for acc in accounts:
            account_id = int(acc['id'])
            current_count = FollowerService.get_current_follower_count(account_id)
            history = FollowerService.get_follower_history(
                account_id,
                granularity,
                days
            )

            result.append({
                'id': acc['id'],
                'name': acc['name'],
                'totalFollowers': current_count or 0,
                'history': {
                    granularity: history
                }
            })

        return result

    @staticmethod
    def ingest_from_spider_data(data: Dict) -> Dict:
        """
        从爬虫数据导入粉丝数据

        Args:
            data: 爬虫数据字典

        Returns:
            Dict: 导入结果
        """
        success_count = 0
        error_count = 0
        errors = []

        accounts_data = data.get('accounts', [])
        update_time = data.get('update_time')

        try:
            # 解析时间并转换为 timezone-aware datetime
            naive_time = datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
            crawl_time = timezone.make_aware(naive_time)
        except (ValueError, TypeError):
            crawl_time = timezone.now()

        for acc_data in accounts_data:
            try:
                # 查找或创建账号
                account, created = Account.objects.get_or_create(
                    uid=str(acc_data['uid']),
                    defaults={
                        'name': acc_data.get('name', 'Unknown'),
                        'platform': 'bilibili'
                    }
                )

                # 更新账号名称
                if not created and acc_data.get('name'):
                    account.name = acc_data['name']
                    account.save()

                # 保存粉丝数据
                if acc_data.get('status') == 'success' and acc_data.get('follower') is not None:
                    FollowerMetrics.objects.update_or_create(
                        account=account,
                        crawl_time=crawl_time,
                        defaults={
                            'follower_count': acc_data['follower']
                        }
                    )
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{acc_data.get('name', acc_data['uid'])}: {acc_data.get('message', 'Unknown error')}")

            except Exception as e:
                error_count += 1
                errors.append(f"{acc_data.get('name', acc_data['uid'])}: {str(e)}")

        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }