from .models import SongRecord, Songs
import requests
import re
import os
from datetime import datetime
from collections import defaultdict
from django.conf import settings
import hashlib
from urllib.parse import urlparse

def is_url_valid(url):
    """检测图片 URL 是否有效"""
    try:
        res = requests.head(url, timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def download_and_save_cover(cover_url, performed_date):
    """下载并保存封面图片"""
    if not cover_url:
        return None
    
    try:
        # 构建本地保存路径
        date_str = performed_date.strftime("%Y-%m-%d")
        year = performed_date.strftime("%Y")
        month = performed_date.strftime("%m")
        
        # 本地封面目录根（已迁移到前端public目录）
        BASE_DIR = os.path.join(".", "xxm_fans_frontend", "public", "covers")
        save_dir = os.path.join(BASE_DIR, year, month)
        os.makedirs(save_dir, exist_ok=True)
        
        filename = f"{date_str}.jpg"
        file_path = os.path.join(save_dir, filename)
        local_path = f"/covers/{year}/{month}/{filename}"
        
        # 如果文件已存在，直接返回本地路径
        if os.path.exists(file_path):
            return local_path
        
        # 下载图片
        headers = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(cover_url, headers=headers, timeout=10)
        response.raise_for_status()
        image_data = response.content
        
        # 保存图片
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        print(f"封面已下载: {local_path}")
        return local_path
        
    except Exception as e:
        print(f"封面下载失败: {e}")
        return cover_url  # 返回原始URL作为备选

def import_bv_song(bvid):
    print(f"[BV:{bvid}] 开始导入")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Step 1: 获取分P信息
    pagelist_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    response = requests.get(pagelist_url, headers=headers)
    response.raise_for_status()
    json_data = response.json()

    # Step 2: 获取视频总封面（用于 fallback）
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

            # ✅ 优先尝试分P封面图（截图）
            preferred_cover = f"https://i0.hdslb.com/bfs/frame/{cid}.jpg"
            cover_url = preferred_cover if is_url_valid(preferred_cover) else fallback_cover_url

            # 提取日期（例如：2025年6月12日）
            match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", title)
            if match:
                try:
                    year, month, day = map(int, match.groups())
                    performed_date = datetime(year, month, day).date()
                    song_name = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日", "", title).strip("- ").strip()
                    song_name = song_name.split("-")[0].strip()
                except Exception as e:
                    print(f"[BV:{bvid}] 日期解析失败: {e} - 标题: {title}")
                    performed_date = None
                    song_name = title.strip()
            else:
                print(f"[BV:{bvid}] 分P标题不含时间: {title}")
                performed_date = None
                song_name = title.strip()

            part_url = f"https://player.bilibili.com/player.html?bvid={bvid}&p={page}"

            if performed_date is None:
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": "❌ 无法解析日期，跳过",
                    "created_song": False,
                    "cover_url": cover_url,
                })
                continue

            # 查找或创建歌曲
            song_obj, created_song = Songs.objects.get_or_create(song_name=song_name)

            if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": "❌ 已存在，跳过",
                    "created_song": created_song,
                    "cover_url": cover_url,
                })
                continue

            cur_song_counts[song_name] += 1
            count = cur_song_counts[song_name]
            note = f"同批版本 {count}" if count > 1 else None

            # ✅ 下载并保存封面
            final_cover_url = download_and_save_cover(cover_url, performed_date)

            # ✅ 创建记录
            SongRecord.objects.create(
                song=song_obj,
                performed_at=performed_date,
                url=part_url,
                notes=note,
                cover_url=final_cover_url
            )

            print(f"[BV:{bvid}] 成功创建演唱记录：{song_name} @ {performed_date}")
            results.append({
                "song_name": song_name,
                "url": part_url,
                "note": note,
                "created_song": created_song,
                "cover_url": final_cover_url
            })

    print(f"[BV:{bvid}] 导入完成，共导入 {len(results)} 条")
    return results
