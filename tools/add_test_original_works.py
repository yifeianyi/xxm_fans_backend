"""
添加测试原唱作品数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from song_management.models import OriginalWork
from datetime import date

def add_test_original_works():
    """添加测试原唱作品数据"""
    test_works = [
        {
            'title': '满天星',
            'release_date': date(2024, 1, 15),
            'description': '第一首个人原创单曲，星光点缀梦境。',
            'netease_id': '1330348068',
            'bilibili_bvid': '',
            'featured': True,
        },
        {
            'title': '溯光者',
            'release_date': date(2023, 11, 20),
            'description': '在音符中寻找光亮，致敬不曾放弃的灵魂。',
            'netease_id': '',
            'bilibili_bvid': 'BV1xx411c7mD',
            'featured': True,
        },
        {
            'title': '森林来信',
            'release_date': date(2023, 5, 10),
            'description': '写给所有小满虫的音乐家书，温暖坚定。',
            'netease_id': '1901371647',
            'bilibili_bvid': '',
            'featured': True,
        },
        {
            'title': '月光小夜曲',
            'release_date': date(2023, 2, 28),
            'description': '温柔的夜晚，用音乐诉说心事。',
            'netease_id': '1496089319',
            'bilibili_bvid': '',
            'featured': False,
        },
    ]

    for work_data in test_works:
        # 检查是否已存在
        if not OriginalWork.objects.filter(title=work_data['title']).exists():
            OriginalWork.objects.create(**work_data)
            print(f"✓ 已添加原唱作品: {work_data['title']}")
        else:
            print(f"⊙ 作品已存在: {work_data['title']}")

    print(f"\n当前共有 {OriginalWork.objects.count()} 首原唱作品")

if __name__ == '__main__':
    add_test_original_works()