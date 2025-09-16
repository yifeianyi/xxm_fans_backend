#!/usr/bin/env python
"""
批量更新SongRecord中的cover_url字段，去掉/static前缀
使用Django的批量更新功能，更高效
使用方法: python manage.py shell < update_cover_urls_bulk.py
"""

import os
import django
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import SongRecord

def update_cover_urls_bulk():
    """
    使用批量更新功能更新cover_url字段，去掉/static前缀
    """
    # 获取所有以/static开头的cover_url记录
    records_to_update = SongRecord.objects.filter(
        cover_url__isnull=False
    ).exclude(
        cover_url=''
    ).filter(
        cover_url__startswith='/static/'
    )
    
    total_count = records_to_update.count()
    
    if total_count == 0:
        print("没有找到需要更新的记录")
        return
    
    print(f"找到 {total_count} 条需要更新的记录")
    
    # 使用事务确保数据一致性
    with transaction.atomic():
        updated_count = 0
        
        for record in records_to_update:
            old_url = record.cover_url
            new_url = old_url[8:]  # 去掉'/static/'
            
            record.cover_url = new_url
            record.save()
            updated_count += 1
            
            if updated_count % 100 == 0:  # 每100条打印一次进度
                print(f"已处理 {updated_count}/{total_count} 条记录")
        
        print(f"✅ 成功更新了 {updated_count} 条记录")
        print("所有更新已完成!")

def preview_changes():
    """
    预览将要进行的更改，不实际执行更新
    """
    records = SongRecord.objects.filter(
        cover_url__isnull=False
    ).exclude(
        cover_url=''
    ).filter(
        cover_url__startswith='/static/'
    )[:10]  # 只显示前10条作为预览
    
    print("预览将要进行的更改（前10条）:")
    print("-" * 60)
    
    for record in records:
        old_url = record.cover_url
        new_url = old_url[8:]  # 去掉'/static/'
        print(f"ID {record.id}: {old_url} -> {new_url}")
    
    total_count = SongRecord.objects.filter(
        cover_url__isnull=False
    ).exclude(
        cover_url=''
    ).filter(
        cover_url__startswith='/static/'
    ).count()
    
    print(f"\n总共需要更新 {total_count} 条记录")

if __name__ == '__main__':
    # 先预览更改
    print("=== 预览模式 ===")
    preview_changes()
    
    print("\n" + "="*60)
    
    # 询问是否执行更新
    response = input("是否执行更新？(y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n=== 执行更新 ===")
        update_cover_urls_bulk()
    else:
        print("取消更新操作") 