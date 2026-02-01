#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
粉丝数据导入脚本
从爬虫 JSON 文件导入数据到数据库，并预生成缓存
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from data_analytics.services.follower_service import FollowerService


def import_from_file(file_path: str):
    """
    从 JSON 文件导入数据

    Args:
        file_path: JSON 文件路径
    """
    print(f"正在导入文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = FollowerService.ingest_from_spider_data(data)

    print(f"\n导入结果:")
    print(f"  成功: {result['success_count']}")
    print(f"  失败: {result['error_count']}")

    if result['errors']:
        print(f"\n错误详情:")
        for error in result['errors']:
            print(f"  - {error}")

    # 导入成功后，预生成缓存
    if result['success_count'] > 0:
        print("\n开始预生成缓存...")
        FollowerService.generate_all_caches()
        print("✓ 缓存预生成完成")


def import_from_directory(dir_path: str):
    """
    从目录导入所有 JSON 文件

    Args:
        dir_path: 目录路径
    """
    json_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.startswith('b_fans_count_') and file.endswith('.json'):
                json_files.append(os.path.join(root, file))

    json_files.sort()

    print(f"找到 {len(json_files)} 个数据文件")
    print("=" * 50)

    for json_file in json_files:
        try:
            import_from_file(json_file)
            print("-" * 50)
        except Exception as e:
            print(f"导入失败: {str(e)}")
            print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description='导入粉丝数据')
    parser.add_argument(
        '--file',
        type=str,
        help='指定单个 JSON 文件'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default='data/spider/fans_count',
        help='指定数据目录'
    )

    args = parser.parse_args()

    if args.file:
        import_from_file(args.file)
    else:
        import_from_directory(args.dir)


if __name__ == '__main__':
    main()