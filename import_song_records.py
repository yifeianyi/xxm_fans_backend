import os
import django
import json
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xxm_fans_home.settings")
django.setup()

from main.models import Songs, SongRecord

json_path = 'happy_data.json'

with open(json_path, 'r', encoding='utf-8') as f:
    try:
        data_list = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误：{e}")
        exit(1)

for i, data in enumerate(data_list):
    try:
        song_name = data.get('歌曲名')
        date_str = data.get('时间')
        url = data.get('分P链接')
        notes = data.get('备注', '')

        if not (song_name and date_str and url):
            print(f"⚠️ 跳过第{i + 1}项，字段不完整：{data}")
            continue

        performed_at = datetime.strptime(date_str, '%Y-%m-%d').date()

        # 查找是否已有同名歌曲，取演出时间最早的一条
        song = Songs.objects.filter(song_name=song_name).order_by('last_performed').first()

        if not song:
            # 没有同名歌曲，创建新的
            song = Songs.objects.create(
                song_name=song_name,
                singer=None,
                last_performed=performed_at,
                perform_count=1
            )
        else:
            # 有同名歌曲，更新演出信息
            if not song.last_performed or performed_at > song.last_performed:
                song.last_performed = performed_at
            song.perform_count = (song.perform_count or 0) + 1
            song.save()

        # 检查是否已有这条记录
        exists = SongRecord.objects.filter(
            song=song,
            performed_at=performed_at,
            url=url
        ).exists()

        if exists:
            print(f"⚠️ 已存在记录，跳过《{song_name}》@ {performed_at}")
            continue

        # 插入演出记录
        SongRecord.objects.create(
            song=song,
            performed_at=performed_at,
            url=url,
            notes=notes
        )
        print(f"✅ 导入成功：《{song_name}》@ {performed_at}")

    except Exception as e:
        print(f"❌ 第{i + 1}条导入失败：{e}")
