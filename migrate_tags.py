#!/usr/bin/env python
"""
在删除tag字段之前，将Songs模型中的标签数据迁移到Tag模型和SongTag中间表
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

def migrate_tags():
    """
    将Songs模型中的标签数据迁移到Tag模型和SongTag中间表
    """
    from main.models import Songs, Tag, SongTag
    
    print("开始迁移标签数据...")
    
    # 获取所有有标签的歌曲
    songs_with_tags = Songs.objects.exclude(tag__isnull=True).exclude(tag='')
    print(f"找到 {songs_with_tags.count()} 首有标签的歌曲")
    
    # 用于存储已创建的标签对象
    tag_cache = {}
    migrated_count = 0
    
    for song in songs_with_tags:
        if song.tag:
            # 按逗号拆分标签
            tags = [tag.strip() for tag in song.tag.split(',') if tag.strip()]
            for tag_name in tags:
                # 创建或获取标签对象
                if tag_name not in tag_cache:
                    tag_obj, created = Tag.objects.get_or_create(name=tag_name)
                    tag_cache[tag_name] = tag_obj
                    if created:
                        print(f"创建新标签: {tag_name}")
                else:
                    tag_obj = tag_cache[tag_name]
                
                # 创建歌曲标签关联
                song_tag, created = SongTag.objects.get_or_create(song=song, tag=tag_obj)
                if created:
                    print(f"关联歌曲 '{song.song_name}' 和标签 '{tag_name}'")
                    migrated_count += 1
    
    print(f"成功迁移 {migrated_count} 个歌曲标签关联")

if __name__ == "__main__":
    migrate_tags()