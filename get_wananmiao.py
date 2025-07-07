import os
import re
import requests
from datetime import datetime
from collections import defaultdict

# Django 环境初始化
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')  # 替换为你的 settings 路径
django.setup()

from main.models import SongRecord, Songs

def is_url_valid(url):
    try:
        res = requests.head(url, timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def download_and_save_cover(cover_url, performed_date):
    if not cover_url or not performed_date:
        return None
    date_str = performed_date.strftime("%Y-%m-%d")
    year = performed_date.strftime("%Y")
    month = performed_date.strftime("%m")
    BASE_DIR = os.path.join(".", "xxm_fans_frontend", "public", "covers")
    save_dir = os.path.join(BASE_DIR, year, month)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{date_str}.jpg"
    file_path = os.path.join(save_dir, filename)
    local_path = f"/covers/{year}/{month}/{filename}"
    if os.path.exists(file_path):
        return local_path
    headers = {
        "Referer": "https://www.bilibili.com",
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(cover_url, headers=headers, timeout=10)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"封面已下载: {local_path}")
        return local_path
    except Exception as e:
        print(f"封面下载失败: {e}")
        return cover_url

def import_bv_song(bvid):
    print(f"[BV:{bvid}] 开始导入")
    headers = {"User-Agent": "Mozilla/5.0"}
    pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    response = requests.get(pagelist_url, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    fallback_cover_url = None
    try:
        video_info = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=headers).json()
        if video_info["code"] == 0:
            fallback_cover_url = video_info["data"]["pic"]
    except Exception as e:
        print(f"[BV:{bvid}] 获取总封面失败: {e}")
    results = []
    cur_song_counts = defaultdict(int)
    if json_data["code"] == 0:
        for page_info in json_data["data"]:
            page = page_info["page"]
            cid = page_info["cid"]
            title = page_info["part"]
            match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})(.+)", title)
            if match:
                year, month, day, song_name = match.groups()
                try:
                    performed_date = datetime(int(year), int(month), int(day)).date()
                except Exception as e:
                    print(f"日期解析失败: {e} - 标题: {title}")
                    performed_date = None
                song_name = song_name.strip()
            else:
                print(f"[BV:{bvid}] 分P标题不含时间: {title}")
                performed_date = None
                song_name = title.strip()
            part_url = f"https://player.bilibili.com/player.html?bvid={bvid}&p={page}"
            preferred_cover = f"https://i0.hdslb.com/bfs/frame/{cid}.jpg"
            cover_url = preferred_cover if is_url_valid(preferred_cover) else fallback_cover_url
            final_cover_url = download_and_save_cover(cover_url, performed_date)
            if performed_date is None:
                print(f"跳过：{title}")
                continue
            # 查找或创建歌曲（避免同名多条报错）
            song_qs = Songs.objects.filter(song_name=song_name)
            if song_qs.exists():
                song_obj = song_qs.first()
                created_song = False
            else:
                song_obj = Songs.objects.create(song_name=song_name)
                created_song = True
            # 检查是否已存在
            if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                print(f"已存在：{song_name} {performed_date}")
                continue
            cur_song_counts[song_name] += 1
            count = cur_song_counts[song_name]
            note = f"同批版本 {count}" if count > 1 else None
            SongRecord.objects.create(
                song=song_obj,
                performed_at=performed_date,
                url=part_url,
                notes=note,
                cover_url=final_cover_url
            )
            print(f"已导入：{song_name} {performed_date}")
    print(f"[BV:{bvid}] 导入完成")

if __name__ == "__main__":
    # bv = input("请输入BV号（如BV1xxxxxxx）：").strip()
    bv = "BV1kc3BzxEiQ"
    import_bv_song(bv)