import requests
import re
import os
from datetime import datetime
from django.conf import settings
from .models import Collection, Work

def is_url_valid(url):
    """检测图片 URL 是否有效"""
    try:
        res = requests.head(url, timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def download_and_save_cover(cover_url, collection_name, pubdate):
    """下载并保存封面图片"""
    if not cover_url:
        return None
    
    try:
        # 构建本地保存路径
        date_str = pubdate.strftime("%Y-%m-%d")
        
        # 本地封面目录根（前端public目录）
        BASE_DIR = os.path.join(".", "xxm_fans_frontend", "public", "footprint", "Collection")
        save_dir = os.path.join(BASE_DIR, collection_name)
        os.makedirs(save_dir, exist_ok=True)
        
        filename = f"{date_str}.jpg"
        file_path = os.path.join(save_dir, filename)
        local_path = f"/footprint/Collection/{collection_name}/{filename}"
        
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

def import_bv_work(bvid, collection_name, notes=""):
    """从B站BV号导入作品到指定合集"""
    print(f"[BV:{bvid}] 开始导入到合集: {collection_name}")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        # 获取或创建合集
        collection, created_collection = Collection.objects.get_or_create(name=collection_name)
        if created_collection:
            print(f"✅ 创建新合集: {collection_name}")

        # 获取视频信息
        video_info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        response = requests.get(video_info_url, headers=headers)
        response.raise_for_status()
        video_data = response.json()

        if video_data["code"] != 0:
            raise Exception(f"获取视频信息失败: {video_data['message']}")

        video_info = video_data["data"]
        
        # 提取视频信息
        title = video_info["title"]
        author = video_info["owner"]["name"]
        cover_url = video_info["pic"]
        pubdate_timestamp = video_data["data"]["pubdate"]
        pubdate = datetime.fromtimestamp(pubdate_timestamp)
        
        # 构建观看链接
        view_url = f"https://player.bilibili.com/player.html?bvid={bvid}"
        
        # 检查是否已存在
        if Work.objects.filter(title=title, collection=collection).exists():
            return {
                "success": False,
                "message": f"作品《{title}》已存在于合集《{collection_name}》中",
                "title": title,
                "author": author,
                "cover_url": cover_url
            }
        
        # 下载并保存封面
        final_cover_url = download_and_save_cover(cover_url, collection_name, pubdate)
        
        # 创建作品记录
        work = Work.objects.create(
            collection=collection,
            title=title,
            cover_url=final_cover_url,
            view_url=view_url,
            author=author,
            notes=notes
        )
        
        # 更新合集作品数量
        collection.update_works_count()
        
        print(f"✅ 成功导入作品: {title} - {author}")
        
        return {
            "success": True,
            "message": f"成功导入作品《{title}》到合集《{collection_name}》",
            "title": title,
            "author": author,
            "cover_url": final_cover_url,
            "created_collection": created_collection
        }
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return {
            "success": False,
            "message": f"导入失败: {str(e)}",
            "title": "",
            "author": "",
            "cover_url": ""
        } 