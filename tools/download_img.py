import os
import django
import requests
import hashlib
from urllib.parse import urlparse
from tqdm import tqdm

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xxm_fans_home.settings")
django.setup()

from song_management.models import SongRecord
from django.conf import settings

# 本地封面目录根 - 使用 MEDIA_ROOT 下的 covers
BASE_DIR = os.path.join(settings.MEDIA_ROOT, "covers")
os.makedirs(BASE_DIR, exist_ok=True)

# 哈希表：图片内容哈希 -> 封面路径
hash_to_path = {}

# 获取所有唯一 cover_url
cover_urls = (
    SongRecord.objects.exclude(cover_url__isnull=True)
    .exclude(cover_url__exact="")
    .values_list("cover_url", flat=True)
    .distinct()
)

print(f"共提取到 {len(cover_urls)} 个唯一封面链接，开始处理...")

for url in tqdm(cover_urls):
    try:
        # 获取所有使用该 URL 的记录
        records = SongRecord.objects.filter(cover_url=url)
        earliest = records.order_by("performed_at").first()

        if not earliest or not earliest.performed_at:
            print(f"[跳过] 无演出日期：{url}")
            continue

        date = earliest.performed_at
        date_str = date.strftime("%Y-%m-%d")
        year = date.strftime("%Y")
        month = date.strftime("%m")

        # 构建保存路径
        save_dir = os.path.join(BASE_DIR, year, month)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{date_str}.jpg"
        file_path = os.path.join(save_dir, filename)
        local_path = f"/covers/{year}/{month}/{filename}"

        # 下载图片内容
        headers = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        image_data = response.content

        # 哈希去重
        image_hash = hashlib.sha256(image_data).hexdigest()
        if image_hash in hash_to_path:
            reused_path = hash_to_path[image_hash]
            records.update(cover_url=reused_path)
        else:
            # 保存图片
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(image_data)
            records.update(cover_url=local_path)
            hash_to_path[image_hash] = local_path

    except Exception as e:
        print(f"[跳过] 处理失败：{url}\n原因：{e}")
