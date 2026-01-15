"""
B站视频信息导入服务
"""
import requests
import os
from datetime import datetime
from django.conf import settings
from ..models import WorkStatic


class BilibiliWorkStaticImporter:
    """B站作品静态信息导入器"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }
    
    def import_bv_work_static(self, bvid):
        """
        导入B站视频的静态信息
        :param bvid: BV号
        :return: (success, message, work_static)
        """
        print(f"[BV:{bvid}] 开始导入作品静态信息")
        
        try:
            # 获取视频信息
            video_info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = requests.get(video_info_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            video_data = response.json()
            
            if video_data["code"] != 0:
                return False, f"获取视频信息失败: {video_data['message']}", None
            
            video_info = video_data["data"]
            
            # 提取视频信息
            title = video_info["title"]
            author = video_info["owner"]["name"]
            cover_url = video_info["pic"]
            pubdate_timestamp = video_info["pubdate"]
            publish_time = datetime.fromtimestamp(pubdate_timestamp)
            
            # 检查是否已存在
            if WorkStatic.objects.filter(platform="bilibili", work_id=bvid).exists():
                return False, f"作品《{title}》已存在", None
            
            # 下载并保存封面
            final_cover_url = self.download_and_save_cover(cover_url, bvid)
            
            # 创建WorkStatic记录
            work_static = WorkStatic.objects.create(
                platform="bilibili",
                work_id=bvid,
                title=title,
                author=author,
                publish_time=publish_time,
                cover_url=final_cover_url,
                is_valid=True
            )
            
            print(f"✅ 成功导入作品静态信息: {title} - {author}")
            
            return True, f"成功导入作品《{title}》", work_static
            
        except requests.exceptions.Timeout:
            return False, "请求超时，请重试", None
        except requests.exceptions.RequestException as e:
            return False, f"网络错误: {str(e)}", None
        except Exception as e:
            return False, f"导入失败: {str(e)}", None
    
    def download_and_save_cover(self, cover_url, bvid):
        """
        下载并保存封面图片到/media/views/目录
        :param cover_url: 封面URL
        :param bvid: BV号
        :return: 封面本地路径
        """
        if not cover_url:
            return None
        
        try:
            # 使用Django的MEDIA_ROOT配置
            BASE_DIR = os.path.join(settings.MEDIA_ROOT, "views")
            os.makedirs(BASE_DIR, exist_ok=True)
            
            # 使用BV号作为文件名
            filename = f"{bvid}.jpg"
            file_path = os.path.join(BASE_DIR, filename)
            local_path = f"views/{filename}"
            
            # 如果文件已存在，直接返回本地路径
            if os.path.exists(file_path):
                print(f"封面已存在: {local_path}")
                return local_path
            
            # 下载图片
            print(f"开始下载封面: {cover_url}")
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