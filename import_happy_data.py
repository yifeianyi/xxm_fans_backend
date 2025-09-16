#!/usr/bin/env python
"""
将happy_data_list_updated.json的数据导入到SongRecord中，并导出错误数据和失败原因。
遇到同名多条Songs时只取第一条，不报错，reason中记录已合并。
使用方法: python manage.py shell < import_happy_data.py
"""

import os
import django
import json
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import Songs, SongRecord

def import_happy_data():
    """
    导入happy_data_list_updated.json的数据到SongRecord，并导出错误数据和失败原因。
    遇到同名多条Songs时只取第一条，不报错，reason中记录已合并。
    """
    json_file = 'happy_data_list_updated.json'
    
    if not os.path.exists(json_file):
        print(f"❌ 找不到文件: {json_file}")
        return
    
    # 读取JSON文件
    print(f"📖 读取JSON文件: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 总共 {len(data)} 条记录")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    error_items = []  # 用于收集出错的数据和原因
    
    for i, item in enumerate(data):
        if i % 100 == 0:
            print(f"⏳ 处理进度: {i}/{len(data)}")
        try:
            song_name = item.get('歌曲名', '').strip()
            time_str = item.get('时间', '').strip()
            video_url = item.get('分P链接', '').strip()
            cover_url = item.get('封面', '').strip()
            
            if not song_name or not time_str:
                skipped_count += 1
                error_items.append({"data": item, "reason": "缺少歌曲名或时间"})
                continue
            try:
                performed_at = datetime.strptime(time_str, '%Y-%m-%d').date()
            except ValueError:
                skipped_count += 1
                error_items.append({"data": item, "reason": f"时间格式错误: {time_str}"})
                continue
            # 查找同名歌曲，若多条只取第一条
            songs_qs = Songs.objects.filter(song_name=song_name)
            if songs_qs.count() == 0:
                song = Songs.objects.create(
                    song_name=song_name,
                    singer='',
                    perform_count=0,
                    last_performed=performed_at
                )
                created = True
            else:
                song = songs_qs.first()
                if songs_qs.count() > 1:
                    error_items.append({"data": item, "reason": f"数据库中有多条同名歌曲，已自动合并，取第一条（共{songs_qs.count()}条）"})
                created = False
            if not song.last_performed or performed_at > song.last_performed:
                song.last_performed = performed_at
                song.save()
            existing_record = SongRecord.objects.filter(
                song=song,
                performed_at=performed_at,
                url=video_url
            ).first()
            if existing_record:
                skipped_count += 1
                error_items.append({"data": item, "reason": "记录已存在"})
                continue
            record = SongRecord.objects.create(
                song=song,
                performed_at=performed_at,
                url=video_url,
                cover_url=cover_url,
                notes=''
            )
            song.perform_count = song.records.count()
            song.save()
            created_count += 1
        except Exception as e:
            error_count += 1
            error_items.append({"data": item, "reason": str(e)})
    # 导出错误数据
    if error_items:
        with open('happy_data_import_error.json', 'w', encoding='utf-8') as f:
            json.dump(error_items, f, ensure_ascii=False, indent=2)
        print(f"❗ 已导出 {len(error_items)} 条错误数据到 happy_data_import_error.json")
    print(f"\n📈 导入完成!")
    print(f"✅ 成功创建: {created_count} 条记录")
    print(f"⏭️  跳过: {skipped_count} 条记录")
    print(f"❌ 错误: {error_count} 条记录")

def preview_data():
    """
    预览将要导入的数据
    """
    json_file = 'happy_data_list_updated.json'
    
    if not os.path.exists(json_file):
        print(f"❌ 找不到文件: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("预览将要导入的数据（前5条）:")
    print("-" * 60)
    
    for i, item in enumerate(data[:5]):
        print(f"{i+1}. {item.get('歌曲名', 'N/A')} - {item.get('时间', 'N/A')}")
    
    print(f"\n总共 {len(data)} 条记录")

if __name__ == '__main__':
    print("=== 预览模式 ===")
    preview_data()
    
    print("\n" + "="*60)
    response = input("是否执行导入？(y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n=== 执行导入 ===")
        import_happy_data()
    else:
        print("取消导入操作") 