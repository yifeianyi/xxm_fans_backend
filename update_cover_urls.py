#!/usr/bin/env python
"""
批量更新SongRecord中的cover_url字段，去掉/static前缀
使用方法: python manage.py shell < update_cover_urls.py
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import SongRecord

def update_cover_urls():
    """
    批量更新cover_url字段，去掉/static前缀
    """
    # 获取所有有cover_url的记录
    records = SongRecord.objects.filter(cover_url__isnull=False).exclude(cover_url='')
    
    updated_count = 0
    skipped_count = 0
    
    print(f"开始处理 {records.count()} 条记录...")
    
    for record in records:
        old_url = record.cover_url
        
        # 检查是否以/static开头
        if old_url.startswith('/static/'):
            # 去掉/static前缀
            new_url = old_url[8:]  # 去掉'/static/'
            record.cover_url = new_url
            record.save()
            updated_count += 1
            print(f"✅ 更新: {old_url} -> {new_url}")
        else:
            skipped_count += 1
            print(f"⏭️  跳过: {old_url} (不以/static开头)")
    
    print(f"\n更新完成!")
    print(f"✅ 更新了 {updated_count} 条记录")
    print(f"⏭️  跳过了 {skipped_count} 条记录")
    print(f"📊 总计处理 {updated_count + skipped_count} 条记录")

if __name__ == '__main__':
    update_cover_urls() 