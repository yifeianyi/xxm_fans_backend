from .models import SongRecord, SongStyle
import requests
import re
from datetime import datetime
from .models import Songs, SongRecord
from collections import defaultdict
from django import forms

def get_datetime(bvid, headers):
    # 从主视频信息中提取发布时间
    info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    resp = requests.get(info_url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    pub_timestamp = data['data']['pubdate']
    return datetime.fromtimestamp(pub_timestamp).date()

# def import_bv_song(bvid):
#     url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         json_data = response.json()
#         performed_date = get_datetime(bvid, headers)

#         results = []
#         cur_song_counts = defaultdict(int)
#         if json_data["code"] == 0:
#             for page_info in json_data["data"]:
#                 page = page_info["page"]
#                 title = page_info["part"]
#                 parts = title.split("-")

#                 if len(parts) >= 1:
#                     song_name = parts[0].strip()
#                     part_url = f"https://www.bilibili.com/video/{bvid}?p={page}"

#                     # 查找或创建歌曲
#                     song_obj, created_song = Songs.objects.get_or_create(song_name=song_name)

#                     if SongRecord.objects.filter(song=song_obj, performed_at= performed_date):
#                         results.append({
#                             "song_name": song_name,
#                             "url": part_url,
#                             "note": "❌ 已存在，跳过",
#                             "created_song": created_song
#                         })
#                         continue
                    
#                     # 记录当前导入中出现的次数
#                     cur_song_counts[song_name] += 1
#                     count = cur_song_counts[song_name]
#                     note = f"同批版本 {count}" if count > 1 else None

#                     # 创建演唱记录
#                     SongRecord.objects.create(
#                         song=song_obj,
#                         performed_at=performed_date,
#                         url=part_url,
#                         notes=note
#                     )

#                     results.append({
#                         "song_name": song_name,
#                         "url": part_url,
#                         "note": note,
#                         "created_song": created_song
#                     })
#                 else:
#                     print(f"[BV:{bvid}] 分P标题格式不符合预期: {title}")
#         return results
#     except Exception as e:
#         print(f"[BV:{bvid}] 导入失败: {e}")
#         raise e

def import_bv_song(bvid):
    print(f"[BV:{bvid}] 开始导入")
    url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()

        results = []
        cur_song_counts = defaultdict(int)

        if json_data["code"] == 0:
            for page_info in json_data["data"]:
                page = page_info["page"]
                title = page_info["part"]

                # 提取日期（例如：2025年6月12日）
                match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", title)
                if match:
                    try:
                        year, month, day = map(int, match.groups())
                        performed_date = datetime(year, month, day).date()
                        # 去掉日期部分，提取歌名
                        song_name = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日", "", title).strip("- ").strip()
                        # 可选：只取前段作为歌名
                        song_name = song_name.split("-")[0].strip()
                    except Exception as e:
                        print(f"[BV:{bvid}] 日期解析失败: {e} - 标题: {title}")
                        performed_date = None
                        song_name = title.strip()
                else:
                    print(f"[BV:{bvid}] 分P标题不含时间: {title}")
                    performed_date = None
                    song_name = title.strip()

                part_url = f"https://www.bilibili.com/video/{bvid}?p={page}"

                if performed_date is None:
                    results.append({
                        "song_name": song_name,
                        "url": part_url,
                        "note": "❌ 无法解析日期，跳过",
                        "created_song": False
                    })
                    continue

                # 查找或创建歌曲
                song_obj, created_song = Songs.objects.get_or_create(song_name=song_name)

                if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                    results.append({
                        "song_name": song_name,
                        "url": part_url,
                        "note": "❌ 已存在，跳过",
                        "created_song": created_song
                    })
                    continue

                # 记录同批内的数量
                cur_song_counts[song_name] += 1
                count = cur_song_counts[song_name]
                note = f"同批版本 {count}" if count > 1 else None

                # 创建记录
                SongRecord.objects.create(
                    song=song_obj,
                    performed_at=performed_date,
                    url=part_url,
                    notes=note
                )
                print(f"[BV:{bvid}] 成功创建演唱记录：{song_name} @ {performed_date}")
                results.append({
                    "song_name": song_name,
                    "url": part_url,
                    "note": note,
                    "created_song": created_song
                })

        print(f"[BV:{bvid}] 导入完成，共导入 {len(results)} 条")
        return results

    except Exception as e:
        print(f"[BV:{bvid}] 导入失败: {e}")
        raise e