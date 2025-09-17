import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import Songs, Style, Tag

def create_test_data():
    # 创建测试歌曲
    song, created = Songs.objects.get_or_create(
        song_name="测试歌曲",
        defaults={
            'singer': '测试歌手',
            'perform_count': 0,
            'language': '中文'
        }
    )
    if created:
        print(f"创建测试歌曲: {song.song_name}")
    else:
        print(f"测试歌曲已存在: {song.song_name}")
    
    # 创建测试曲风
    style, created = Style.objects.get_or_create(name="流行")
    if created:
        print(f"创建测试曲风: {style.name}")
    else:
        print(f"测试曲风已存在: {style.name}")
    
    # 创建测试标签
    tag, created = Tag.objects.get_or_create(name="热门")
    if created:
        print(f"创建测试标签: {tag.name}")
    else:
        print(f"测试标签已存在: {tag.name}")

if __name__ == "__main__":
    create_test_data()