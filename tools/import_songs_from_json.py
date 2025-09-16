import json
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import Songs, Style, SongStyle

# 载入 JSON 文件
with open('sqlInit_data/songlist_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 开始导入
for item in data:
    song_name = item["歌名"].strip()
    singer = item.get("原唱", "").strip()
    language = item.get("语种", "").strip()
    styles_raw = item.get("风格", "").strip()

    # ✅ 获取或创建歌曲
    song, created = Songs.objects.get_or_create(
        song_name=song_name,
        defaults={
            "singer": singer,
            "language": language
        }
    )

    if not created:
        # 已存在就补充 singer / language（如为空）
        if not song.singer and singer:
            song.singer = singer
        if not song.language and language:
            song.language = language
        song.save()

    # ✅ 处理风格（可能多个）
    styles = [s.strip() for s in styles_raw.split(",") if s.strip()]
    for style_name in styles:
        style_obj, _ = Style.objects.get_or_create(name=style_name)
        SongStyle.objects.get_or_create(song=song, style=style_obj)

print("✅ 所有歌曲已导入完成")
