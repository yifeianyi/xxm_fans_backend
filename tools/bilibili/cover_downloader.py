"""
B站封面下载器
提供统一的封面下载功能，支持多种路径配置
"""
import os
import requests
from typing import Optional
from datetime import datetime
from django.conf import settings


class BilibiliCoverDownloader:
    """统一的B站封面下载器"""

    def __init__(
        self,
        base_dir: Optional[str] = None,
        timeout: int = 10,
        max_size: int = 10 * 1024 * 1024  # 10MB
    ):
        """
        初始化封面下载器
        :param base_dir: 基础目录，如果为None则使用Django的MEDIA_ROOT
        :param timeout: 下载超时时间（秒）
        :param max_size: 最大文件大小（字节）
        """
        self.base_dir = base_dir or settings.MEDIA_ROOT
        self.timeout = timeout
        self.max_size = max_size
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }

    def download(
        self,
        cover_url: str,
        sub_path: str,
        filename: str,
        check_exists: bool = True
    ) -> Optional[str]:
        """
        下载封面
        :param cover_url: 封面URL
        :param sub_path: 子路径（如 'covers/2025/01' 或 'views'）
        :param filename: 文件名（如 '2025-01-15.jpg' 或 'BV123456.jpg'）
        :param check_exists: 是否检查文件已存在
        :return: 本地相对路径（如 'covers/2025/01/2025-01-15.jpg'），失败返回None
        """
        if not cover_url:
            print("封面URL为空，跳过下载")
            return None

        try:
            # 构建完整路径
            save_dir = os.path.join(self.base_dir, sub_path)
            file_path = os.path.join(save_dir, filename)
            local_path = os.path.join(sub_path, filename)

            # 检查文件是否已存在
            if check_exists and os.path.exists(file_path):
                print(f"封面已存在: {local_path}")
                return local_path

            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)

            # 下载图片
            print(f"开始下载封面: {cover_url} -> {local_path}")
            response = requests.get(cover_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # 检查文件大小
            content_length = len(response.content)
            if content_length > self.max_size:
                print(f"封面文件过大: {content_length} bytes (最大: {self.max_size} bytes)")
                return None

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"封面已下载: {local_path} ({content_length} bytes)")
            return local_path

        except requests.exceptions.Timeout:
            print(f"封面下载超时: {cover_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"封面下载网络错误: {e}")
            return None
        except Exception as e:
            print(f"封面下载失败: {e}")
            return None

    def download_by_date(
        self,
        cover_url: str,
        performed_date: datetime,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        按日期下载封面（用于歌曲封面）
        :param cover_url: 封面URL
        :param performed_date: 演出日期
        :param filename: 文件名，如果为None则使用日期格式
        :return: 本地相对路径
        """
        date_str = performed_date.strftime("%Y-%m-%d")
        year = performed_date.strftime("%Y")
        month = performed_date.strftime("%m")

        if filename is None:
            filename = f"{date_str}.jpg"

        sub_path = f"covers/{year}/{month}"
        return self.download(cover_url, sub_path, filename)

    def download_by_bvid(
        self,
        cover_url: str,
        bvid: str
    ) -> Optional[str]:
        """
        按BV号下载封面（用于数据分析）
        :param cover_url: 封面URL
        :param bvid: BV号
        :return: 本地相对路径
        """
        filename = f"{bvid}.jpg"
        sub_path = "views"
        return self.download(cover_url, sub_path, filename)

    def download_by_collection(
        self,
        cover_url: str,
        collection_name: str,
        pubdate: datetime
    ) -> Optional[str]:
        """
        按合集下载封面（用于二创作品）
        :param cover_url: 封面URL
        :param collection_name: 合集名称
        :param pubdate: 发布日期
        :return: 本地相对路径
        """
        date_str = pubdate.strftime("%Y-%m-%d")
        filename = f"{date_str}.jpg"
        sub_path = f"footprint/Collection/{collection_name}"
        return self.download(cover_url, sub_path, filename)