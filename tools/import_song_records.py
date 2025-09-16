import os
import django
import json
from datetime import datetime

# 初始化 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xxm_fans_home.settings")
django.setup()

from main.models import Songs, SongRecord

# JSON 文件路径
json_path = 'sqlInit_data/BChicken_url.json'

# 加载 JSON 数据
with open(json_path, 'r', encoding='utf-8') as f:
    try:
        data_list = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误：{e}")
        exit(1)

# 遍历数据并导入
for i, data in enumerate(data_list):
    try:
        song_name = data.get('歌曲名')
        date_str = data.get('时间')
        url = data.get('分P链接')
        cover_url = data.get('封面')  # ✅ 新增：读取封面
        notes = data.get('备注', '')  # 可选字段

        # 基本字段校验
        if not (song_name and date_str and url and cover_url):
            print(f"⚠️ 跳过第{i + 1}项，字段不完整：{data}")
            continue

        performed_at = datetime.strptime(date_str, '%Y-%m-%d').date()

        # 查找是否已有该歌曲
        song = Songs.objects.filter(song_name=song_name).order_by('last_performed').first()

        if not song:
            # 新建歌曲
            song = Songs.objects.create(
                song_name=song_name,
                singer=None,
                last_performed=performed_at,
                perform_count=1
            )
        else:
            # 更新已有歌曲演出信息
            if not song.last_performed or performed_at > song.last_performed:
                song.last_performed = performed_at
            song.perform_count = (song.perform_count or 0) + 1
            song.save()

        # 检查是否已存在该演出记录
        exists = SongRecord.objects.filter(
            song=song,
            performed_at=performed_at,
            url=url
        ).exists()

        if exists:
            print(f"⚠️ 已存在记录，跳过《{song_name}》@ {performed_at}")
            continue

        # ✅ 创建演出记录（包含封面）
        SongRecord.objects.create(
            song=song,
            performed_at=performed_at,
            url=url,
            notes=notes,
            cover_url=cover_url
        )

        print(f"✅ 导入成功：《{song_name}》@ {performed_at}")

    except Exception as e:
        print(f"❌ 第{i + 1}条导入失败：{e}")
