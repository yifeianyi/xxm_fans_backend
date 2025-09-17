#!/usr/bin/env python
"""
为歌曲分配标签
"""

import os
import django
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

def assign_tags_to_songs():
    """
    为歌曲分配标签
    """
    from main.models import Songs, Tag, SongTag
    
    print("开始为歌曲分配标签...")
    
    # 获取所有标签
    tags = list(Tag.objects.all())
    print(f"找到 {len(tags)} 个标签")
    
    # 获取所有歌曲
    songs = list(Songs.objects.all())
    print(f"找到 {len(songs)} 首歌曲")
    
    # 为每首歌曲随机分配1-3个标签
    assigned_count = 0
    for song in songs:
        # 随机选择1-3个标签
        tags_count = random.randint(1, min(3, len(tags)))
        selected_tags = random.sample(tags, tags_count)
        
        # 创建歌曲标签关联
        for tag in selected_tags:
            song_tag, created = SongTag.objects.get_or_create(song=song, tag=tag)
            if created:
                assigned_count += 1
    
    print(f"成功创建 {assigned_count} 个歌曲标签关联")

if __name__ == "__main__":
    assign_tags_to_songs()