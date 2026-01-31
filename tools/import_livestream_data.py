import os
import sys
import django
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

# 初始化 Django
django.setup()

from livestream.models import Livestream


def import_livestream_data(json_file_path: str):
    """
    从 live_final.json 导入直播数据到数据库

    Args:
        json_file_path: JSON 文件路径
    """
    print(f"开始导入直播数据: {json_file_path}")

    # 读取 JSON 文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"错误: JSON 格式错误 - {json_file_path}")
        return

    # 统计信息
    total_count = len(data)
    created_count = 0
    updated_count = 0
    skipped_count = 0

    # 导入数据
    for item in data:
        date_str = item.get('date', '')
        bvid = item.get('bvid', '')
        title = item.get('title', '')
        describe = item.get('describe', '')
        duration = item.get('duration', 0)
        duration_formatted = item.get('duration_formatted', '')
        parts = item.get('parts', 1)
        danmaku_count = item.get('danmaku_count', 0)

        # 解析日期
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"跳过无效日期: {date_str}")
            skipped_count += 1
            continue

        # 检查是否已存在
        try:
            livestream = Livestream.objects.get(date=date_obj)
            # 更新现有记录
            livestream.bvid = bvid
            livestream.title = title
            livestream.summary = describe
            livestream.duration_seconds = duration
            livestream.duration_formatted = duration_formatted
            livestream.parts = parts
            livestream.danmaku_count = str(danmaku_count) if danmaku_count else 'N/A'
            # 生成 live_moment 目录路径
            livestream.live_moment = f'/gallery/LiveMoment/{date_obj.year}/{date_obj.month:02d}/{date_obj.day:02d}/'
            livestream.save()
            updated_count += 1
            print(f"✓ 更新: {date_str} - {title}")
        except Livestream.DoesNotExist:
            # 创建新记录
            live_moment = f'/gallery/LiveMoment/{date_obj.year}/{date_obj.month:02d}/{date_obj.day:02d}/'
            Livestream.objects.create(
                date=date_obj,
                bvid=bvid,
                title=title,
                summary=describe,
                duration_seconds=duration,
                duration_formatted=duration_formatted,
                parts=parts,
                danmaku_count=str(danmaku_count) if danmaku_count else 'N/A',
                live_moment=live_moment,
            )
            created_count += 1
            print(f"+ 创建: {date_str} - {title}")

    # 输出统计信息
    print("\n" + "=" * 50)
    print("导入完成！")
    print(f"总记录数: {total_count}")
    print(f"创建记录: {created_count}")
    print(f"更新记录: {updated_count}")
    print(f"跳过记录: {skipped_count}")
    print("=" * 50)


if __name__ == '__main__':
    # JSON 文件路径
    json_file = '/home/yifeianyi/Desktop/xxm_fans_home/live_final.json'

    # 执行导入
    import_livestream_data(json_file)