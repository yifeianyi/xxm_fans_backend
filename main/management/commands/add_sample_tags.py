from django.core.management.base import BaseCommand
from main.models import Songs
import random

class Command(BaseCommand):
    help = '为现有歌曲添加示例标签'

    def handle(self, *args, **options):
        # 定义一些示例标签
        sample_tags = ['热门', '经典', '新歌', '推荐', '怀旧', '流行', '摇滚', '民谣', '电子', '嘻哈']
        
        # 获取所有歌曲
        all_songs = list(Songs.objects.all())
        
        # 为每个歌曲随机分配1-3个标签
        updated = 0
        for song in all_songs:
            # 随机选择1-3个标签
            tags_count = random.randint(1, 3)
            selected_tags = random.sample(sample_tags, min(tags_count, len(sample_tags)))
            
            # 将标签用逗号连接
            song.tag = ','.join(selected_tags)
            song.save()
            updated += 1
            
        self.stdout.write(self.style.SUCCESS(f"成功为 {updated} 首歌曲添加了示例标签"))