from .models import SongRecord, SongStyle
import requests
import re
from datetime import datetime
from .models import Songs, SongRecord
from collections import defaultdict

def get_datetime(bvid, headers):
    # 从主视频信息中提取发布时间
    info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    resp = requests.get(info_url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    pub_timestamp = data['data']['pubdate']
    return datetime.fromtimestamp(pub_timestamp).date()

def import_bv_song(bvid):
    url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        performed_date = get_datetime(bvid, headers)

        results = []
        cur_song_counts = defaultdict(int)
        if json_data["code"] == 0:
            for page_info in json_data["data"]:
                page = page_info["page"]
                title = page_info["part"]
                parts = title.split("-")

                if len(parts) >= 1:
                    song_name = parts[0].strip()
                    part_url = f"https://www.bilibili.com/video/{bvid}?p={page}"

                    # 查找或创建歌曲
                    song_obj, created_song = Songs.objects.get_or_create(song_name=song_name)

                    if SongRecord.objects.filter(song=song_obj, performed_at= performed_date):
                        results.append({
                            "song_name": song_name,
                            "url": part_url,
                            "note": "❌ 已存在，跳过",
                            "created_song": created_song
                        })
                        continue
                    
                    # 记录当前导入中出现的次数
                    cur_song_counts[song_name] += 1
                    count = cur_song_counts[song_name]
                    note = f"同批版本 {count}" if count > 1 else None

                    # 创建演唱记录
                    SongRecord.objects.create(
                        song=song_obj,
                        performed_at=performed_date,
                        url=part_url,
                        notes=note
                    )

                    results.append({
                        "song_name": song_name,
                        "url": part_url,
                        "note": note,
                        "created_song": created_song
                    })
                else:
                    print(f"[BV:{bvid}] 分P标题格式不符合预期: {title}")
        return results
    except Exception as e:
        print(f"[BV:{bvid}] 导入失败: {e}")
        raise e
                    
        

# def merge_songs_util(keep_song, remove_song):
#     """
#     将 remove_song 的相关记录合并到 keep_song。
#     """
#     # 1. 合并 SongRecord
#     SongRecord.objects.filter(song=remove_song).update(song=keep_song)

#     # 2. 合并 SongStyle，避免重复
#     for ss in SongStyle.objects.filter(song=remove_song):
#         if not SongStyle.objects.filter(song=keep_song, style=ss.style).exists():
#             SongStyle.objects.create(song=keep_song, style=ss.style)

#     # 3. 合并其他字段（如演唱次数、时间）
#     keep_song.perform_count += remove_song.perform_count or 0

#     if remove_song.last_performed:
#         if not keep_song.last_performed or remove_song.last_performed > keep_song.last_performed:
#             keep_song.last_performed = remove_song.last_performed

#     keep_song.save()

#     # 4. 删除 remove_song
#     remove_song.delete()
