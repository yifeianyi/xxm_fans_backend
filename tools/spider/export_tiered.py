#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层数据导出模块
根据发布时间将作品分为热数据（7天内）和冷数据（超过7天）

路径: repo/xxm_fans_backend/tools/spider/export_tiered.py
"""

import json
import os
import sys
from datetime import timedelta
from typing import List, Dict, Any, Tuple
from enum import Enum

# Django 设置
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from django.utils import timezone
from data_analytics.models import WorkStatic
from .utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("export_tiered")

# 项目根目录
PROJECT_ROOT = get_project_root()
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "spider")

# 默认热数据时间阈值（7天）
DEFAULT_HOT_DAYS = 7


class WorkTier(Enum):
    """作品分层类型"""
    HOT = "hot"          # 热数据：7天内发布
    COLD = "cold"        # 冷数据：超过7天
    ALL = "all"          # 全部数据


def get_tiered_cutoff_date(hot_days: int = DEFAULT_HOT_DAYS):
    """
    获取分层截止时间
    
    Args:
        hot_days: 热数据天数阈值
        
    Returns:
        datetime: 分层截止时间（带时区，早于该时间的为冷数据）
    """
    return timezone.now() - timedelta(days=hot_days)


def classify_works(
    works: List[WorkStatic], 
    hot_days: int = DEFAULT_HOT_DAYS
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    将作品列表分为热数据和冷数据
    
    Args:
        works: WorkStatic 查询集
        hot_days: 热数据天数阈值
        
    Returns:
        Tuple[List[Dict]], List[Dict]]: (热数据列表, 冷数据列表)
    """
    cutoff_date = get_tiered_cutoff_date(hot_days)
    
    hot_works = []
    cold_works = []
    
    for work in works:
        work_dict = {
            "platform": work.platform,
            "work_id": work.work_id,
            "title": work.title,
            "author": work.author,
            "publish_time": work.publish_time.isoformat() if work.publish_time else None,
            "cover_url": work.cover_url,
            "is_valid": work.is_valid
        }
        
        # 判断发布时间是否在热数据范围内
        if work.publish_time and work.publish_time >= cutoff_date:
            hot_works.append(work_dict)
        else:
            cold_works.append(work_dict)
    
    return hot_works, cold_works


class TieredViewsExporter:
    """分层作品数据导出器"""

    def __init__(self, hot_days: int = DEFAULT_HOT_DAYS):
        """
        初始化导出器
        
        Args:
            hot_days: 热数据天数阈值（默认7天）
        """
        self.hot_days = hot_days
        self.cutoff_date = get_tiered_cutoff_date(hot_days)
        logger.info(f"分层导出器初始化: 热数据阈值={hot_days}天, 截止时间={self.cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

    def fetch_all_works(self) -> List[WorkStatic]:
        """从数据库获取所有有效作品数据"""
        queryset = WorkStatic.objects.filter(is_valid=True).order_by('-publish_time')
        works = list(queryset)
        logger.info(f"从数据库获取了 {len(works)} 条有效作品记录")
        return works

    def export_by_tier(self, tier: WorkTier) -> Tuple[bool, str, Dict[str, Any]]:
        """
        按分层导出数据
        
        Args:
            tier: 分层类型 (HOT/COLD/ALL)
            
        Returns:
            Tuple[bool, str, dict]: (是否成功, 输出文件路径, 导出信息)
        """
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # 获取所有有效作品
            all_works = self.fetch_all_works()
            
            if not all_works:
                logger.warning("数据库中没有有效作品")
                return False, "", {"error": "没有有效作品"}

            # 分类作品
            hot_works, cold_works = classify_works(all_works, self.hot_days)
            
            export_info = {
                "export_time": timezone.now().isoformat(),
                "tier": tier.value,
                "hot_days_threshold": self.hot_days,
                "cutoff_date": self.cutoff_date.isoformat(),
            }

            # 根据分层类型选择要导出的作品
            if tier == WorkTier.HOT:
                works_to_export = hot_works
                output_file = os.path.join(OUTPUT_DIR, "views_hot.json")
                export_info.update({
                    "total_count": len(hot_works),
                    "description": f"热数据：最近{self.hot_days}天内发布的作品",
                })
                logger.info(f"导出热数据: {len(hot_works)} 条作品 (发布时间 >= {self.cutoff_date.date()})")
                
            elif tier == WorkTier.COLD:
                works_to_export = cold_works
                output_file = os.path.join(OUTPUT_DIR, "views_cold.json")
                export_info.update({
                    "total_count": len(cold_works),
                    "description": f"冷数据：{self.hot_days}天前发布的作品",
                })
                logger.info(f"导出冷数据: {len(cold_works)} 条作品 (发布时间 < {self.cutoff_date.date()})")
                
            else:  # ALL
                works_to_export = hot_works + cold_works
                output_file = os.path.join(OUTPUT_DIR, "views.json")
                export_info.update({
                    "total_count": len(all_works),
                    "hot_count": len(hot_works),
                    "cold_count": len(cold_works),
                    "description": "全部有效作品",
                })
                logger.info(f"导出全部数据: {len(all_works)} 条作品 (热数据:{len(hot_works)}, 冷数据:{len(cold_works)})")

            # 构建输出数据
            output_data = {
                **export_info,
                "works": works_to_export
            }

            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logger.info(f"成功导出到 {output_file}")
            return True, output_file, export_info

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False, "", {"error": str(e)}

    def export_hot(self) -> Tuple[bool, str, Dict[str, Any]]:
        """导出热数据"""
        return self.export_by_tier(WorkTier.HOT)

    def export_cold(self) -> Tuple[bool, str, Dict[str, Any]]:
        """导出冷数据"""
        return self.export_by_tier(WorkTier.COLD)

    def export_all(self) -> Tuple[bool, str, Dict[str, Any]]:
        """导出全部数据"""
        return self.export_by_tier(WorkTier.ALL)

    def get_tier_stats(self) -> Dict[str, Any]:
        """
        获取分层统计信息
        
        Returns:
            dict: 分层统计信息
        """
        all_works = self.fetch_all_works()
        hot_works, cold_works = classify_works(all_works, self.hot_days)
        
        # 获取最新的热数据和最旧的冷数据
        newest_hot = hot_works[0] if hot_works else None
        oldest_hot = hot_works[-1] if hot_works else None
        newest_cold = cold_works[0] if cold_works else None
        oldest_cold = cold_works[-1] if cold_works else None
        
        return {
            "hot_days_threshold": self.hot_days,
            "cutoff_date": self.cutoff_date.isoformat(),
            "total_works": len(all_works),
            "hot_works": {
                "count": len(hot_works),
                "newest": newest_hot,
                "oldest": oldest_hot,
            },
            "cold_works": {
                "count": len(cold_works),
                "newest": newest_cold,
                "oldest": oldest_cold,
            },
            "crawl_schedule": {
                "hot": "每小时爬取",
                "cold": "每天3次 (00:00, 08:00, 16:00)",
            }
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='分层数据导出工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 导出热数据（7天内发布的作品）
  python export_tiered.py --hot
  
  # 导出冷数据（7天前发布的作品）
  python export_tiered.py --cold
  
  # 导出全部数据
  python export_tiered.py --all
  
  # 自定义热数据天数阈值
  python export_tiered.py --hot --days 14
  
  # 查看分层统计信息
  python export_tiered.py --stats
        """
    )
    
    parser.add_argument('--hot', action='store_true', help='导出热数据（最近7天）')
    parser.add_argument('--cold', action='store_true', help='导出冷数据（7天前）')
    parser.add_argument('--all', action='store_true', help='导出全部数据')
    parser.add_argument('--stats', action='store_true', help='显示分层统计信息')
    parser.add_argument('--days', type=int, default=DEFAULT_HOT_DAYS, 
                        help=f'热数据天数阈值（默认{DEFAULT_HOT_DAYS}天）')
    
    args = parser.parse_args()
    
    exporter = TieredViewsExporter(hot_days=args.days)
    
    if args.stats:
        stats = exporter.get_tier_stats()
        print("\n" + "=" * 60)
        print("分层统计信息")
        print("=" * 60)
        print(f"热数据阈值: {stats['hot_days_threshold']} 天")
        print(f"分层截止时间: {stats['cutoff_date'][:10]}")
        print(f"总作品数: {stats['total_works']}")
        print(f"\n热数据（最近{args.days}天）: {stats['hot_works']['count']} 条")
        if stats['hot_works']['newest']:
            print(f"  最新: {stats['hot_works']['newest']['title'][:40]}...")
        if stats['hot_works']['oldest']:
            print(f"  最旧: {stats['hot_works']['oldest']['title'][:40]}...")
        print(f"\n冷数据（{args.days}天前）: {stats['cold_works']['count']} 条")
        if stats['cold_works']['newest']:
            print(f"  最新: {stats['cold_works']['newest']['title'][:40]}...")
        if stats['cold_works']['oldest']:
            print(f"  最旧: {stats['cold_works']['oldest']['title'][:40]}...")
        print("\n爬取策略:")
        print(f"  热数据: {stats['crawl_schedule']['hot']}")
        print(f"  冷数据: {stats['crawl_schedule']['cold']}")
        print("=" * 60)
        sys.exit(0)
    
    # 确定导出类型
    if args.hot:
        success, filepath, info = exporter.export_hot()
    elif args.cold:
        success, filepath, info = exporter.export_cold()
    elif args.all:
        success, filepath, info = exporter.export_all()
    else:
        # 默认导出全部
        success, filepath, info = exporter.export_all()
    
    if success:
        print(f"\n✓ 导出成功: {filepath}")
        print(f"  类型: {info.get('description')}")
        print(f"  数量: {info.get('total_count')} 条")
        sys.exit(0)
    else:
        print(f"\n✗ 导出失败: {info.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
