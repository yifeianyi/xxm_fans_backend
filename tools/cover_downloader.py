import requests
import os
from datetime import datetime
from django.conf import settings

class CoverDownloader:
    """封面下载器"""
    
    def __init__(self):
        self.headers = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0"
        }
    
    def download_and_save_cover(self, cover_url, performed_date):
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
            response = requests.get(cover_url, headers=self.headers, timeout=10)
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