#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出模块
将 WorkStatic 表数据导出为 views.json
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Django 设置
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from data_analytics.models import WorkStatic
from .utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("export_views")

# 项目根目录
PROJECT_ROOT = get_project_root()
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "spider", "views.json")


class ViewsExporter:
    """作品数据导出器"""

    def __init__(self):
        self.works = []

    def fetch_works(self) -> List[Dict[str, Any]]:
        """从数据库获取作品数据"""
        works = []
        queryset = WorkStatic.objects.all().order_by('-publish_time')

        for work in queryset:
            works.append({
                "platform": work.platform,
                "work_id": work.work_id,
                "title": work.title,
                "author": work.author,
                "publish_time": work.publish_time.isoformat() if work.publish_time else None,
                "cover_url": work.cover_url,
                "is_valid": work.is_valid
            })

        logger.info(f"从数据库获取了 {len(works)} 条作品记录")
        return works

    def export(self) -> bool:
        """导出数据到 JSON 文件"""
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

            works = self.fetch_works()
            valid_count = sum(1 for w in works if w['is_valid'])

            output_data = {
                "export_time": datetime.now().isoformat(),
                "total_count": len(works),
                "valid_count": valid_count,
                "works": works
            }

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logger.info(f"成功导出到 {OUTPUT_FILE}，总计 {len(works)} 条记录，有效 {valid_count} 条")
            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False


def main():
    exporter = ViewsExporter()
    success = exporter.export()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
