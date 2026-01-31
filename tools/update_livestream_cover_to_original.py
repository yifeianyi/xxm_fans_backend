#!/usr/bin/env python
"""
批量修改直播录像封面URL，从使用缩略图改为直接使用原图

使用方法：
    cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
    python manage.py shell < tools/update_livestream_cover_to_original.py

或者：
    python tools/update_livestream_cover_to_original.py
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from livestream.models import Livestream
from django.core.files.storage import default_storage


def update_livestream_covers():
    """
    批量修改直播录像封面URL，从使用缩略图改为直接使用原图
    """
    print("=" * 60)
    print("开始批量修改直播录像封面URL...")
    print("=" * 60)

    # 获取所有直播记录
    livestreams = Livestream.objects.all()
    total_count = livestreams.count()

    print(f"\n找到 {total_count} 条直播记录")

    if total_count == 0:
        print("没有需要修改的记录")
        return

    updated_count = 0
    skipped_count = 0

    for livestream in livestreams:
        old_cover_url = livestream.cover_url

        # 如果没有封面URL，跳过
        if not old_cover_url:
            skipped_count += 1
            continue

        # 检查是否已经是原图（不包含 /thumbnails/）
        if '/thumbnails/' not in old_cover_url:
            skipped_count += 1
            continue

        # 将缩略图URL转换为原图URL
        new_cover_url = convert_thumbnail_to_original(old_cover_url)

        if new_cover_url != old_cover_url:
            # 更新封面URL
            livestream.cover_url = new_cover_url
            livestream.save(update_fields=['cover_url'])
            updated_count += 1

            print(f"✓ 更新: {livestream.date}")
            print(f"  旧URL: {old_cover_url}")
            print(f"  新URL: {new_cover_url}")
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print("修改完成！")
    print(f"总计: {total_count} 条记录")
    print(f"已更新: {updated_count} 条")
    print(f"跳过: {skipped_count} 条")
    print("=" * 60)


def convert_thumbnail_to_original(thumbnail_url):
    """
    将缩略图URL转换为原图URL

    规则：
    - gallery/thumbnails/ -> gallery/
    - covers/thumbnails/ -> covers/
    - footprint/thumbnails/ -> footprint/
    - data_analytics/thumbnails/ -> data_analytics/

    Args:
        thumbnail_url: 缩略图URL

    Returns:
        原图URL
    """
    if not thumbnail_url:
        return thumbnail_url

    # 移除 /media/ 前缀（如果有）
    url = thumbnail_url
    if url.startswith('/media/'):
        url = url[7:]

    # 替换缩略图路径
    thumbnail_patterns = [
        ('gallery/thumbnails/', 'gallery/'),
        ('covers/thumbnails/', 'covers/'),
        ('footprint/thumbnails/', 'footprint/'),
        ('data_analytics/thumbnails/', 'data_analytics/'),
        ('cloud_picture/thumbnails/', 'cloud_picture/'),
    ]

    for pattern, replacement in thumbnail_patterns:
        if pattern in url:
            url = url.replace(pattern, replacement, 1)  # 只替换第一个匹配
            break

    # 恢复 /media/ 前缀
    if thumbnail_url.startswith('/media/'):
        url = f"/media/{url}"

    return url


def main():
    """主函数"""
    try:
        update_livestream_covers()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
