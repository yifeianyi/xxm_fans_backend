#!/usr/bin/env python3
"""
将 SongRecord 中与直播回放相同日期的封面设置到 livestream.cover_url

运行方法:
    cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
    python3 tools/migrate_livestream_cover.py
"""

import os
import sys

# 添加项目路径到 sys.path
project_path = '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from livestream.models import Livestream
from song_management.models.song import SongRecord


def migrate_livestream_cover():
    """
    将 SongRecord 中与直播回放相同日期的封面设置到 livestream.cover_url
    优先选择当天的第一个有封面的演唱记录的封面
    """
    print("=" * 60)
    print("开始迁移直播回放封面...")
    print("=" * 60)

    # 统计信息
    updated_count = 0
    skipped_count = 0
    no_record_count = 0
    no_cover_count = 0

    # 获取所有直播记录
    livestreams = Livestream.objects.all().order_by('-date')

    print(f"\n找到 {livestreams.count()} 条直播记录\n")

    for livestream in livestreams:
        print(f"处理: {livestream.date} - {livestream.title}")

        # 查找当天的演唱记录（按日期匹配，并优先选择有封面的记录）
        song_records = SongRecord.objects.filter(
            performed_at=livestream.date
        ).exclude(cover_url__isnull=True).exclude(cover_url='').order_by('id')

        if not song_records.exists():
            print(f"  ✗ 当天没有找到演唱记录")
            no_record_count += 1
            continue

        # 取第一个有封面的演唱记录
        first_record = song_records.first()

        # 更新直播记录的封面
        livestream.cover_url = first_record.cover_url
        livestream.save(update_fields=['cover_url'])

        print(f"  ✓ 已设置封面: {first_record.cover_url}")
        updated_count += 1

        if livestream.cover_url is None or livestream.cover_url == '':
            no_cover_count += 1

    # 打印汇总信息
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"成功更新: {updated_count} 条")
    print(f"当天没有演唱记录: {no_record_count} 条")
    print(f"当天没有封面: {no_cover_count} 条")
    print("=" * 60)


if __name__ == '__main__':
    migrate_livestream_cover()