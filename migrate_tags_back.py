#!/usr/bin/env python
"""
将Tag表中的数据迁移回Songs模型的tag字段
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

def migrate_tags_back():
    """
    将Tag表中的数据迁移回Songs模型的tag字段
    """
    from main.models import Songs, Tag, SongTag
    
    print("开始迁移标签数据回Songs模型...")
    
    # 获取所有歌曲标签关联
    song_tags = SongTag.objects.select_related('song', 'tag')
    print(f"找到 {song_tags.count()} 个歌曲标签关联")
    
    # 按歌曲分组标签
    song_tag_mapping = {}
    for st in song_tags:
        if st.song.id not in song_tag_mapping:
            song_tag_mapping[st.song.id] = []
        song_tag_mapping[st.song.id].append(st.tag.name)
    
    # 更新歌曲的tag字段
    updated_count = 0
    for song_id, tags in song_tag_mapping.items():
        try:
            song = Songs.objects.get(id=song_id)
            song.tag = ','.join(tags)
            song.save()
            updated_count += 1
        except Songs.DoesNotExist:
            print(f"歌曲 ID {song_id} 不存在")
    
    print(f"成功更新 {updated_count} 首歌曲的标签")

if __name__ == "__main__":
    migrate_tags_back()