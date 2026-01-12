"""
图片下载器 - 统一的图片下载工具
"""
import os
import requests
from pathlib import Path
from typing import List, Optional, Union
from django.conf import settings


class ImageDownloader:
    """
    统一的图片下载器

    支持单个下载和批量下载，自动处理错误和重复文件
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化图片下载器

        Args:
            base_dir: 基础目录，默认使用 settings.MEDIA_ROOT / 'covers'
        """
        if base_dir is None:
            base_dir = Path(settings.MEDIA_ROOT) / 'covers'
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def download(
        self,
        url: str,
        filename: Optional[str] = None,
        overwrite: bool = False,
        timeout: int = 30,
        verify_ssl: bool = True
    ) -> Optional[str]:
        """
        下载单个图片

        Args:
            url: 图片 URL
            filename: 保存的文件名，如果为 None 则从 URL 提取
            overwrite: 是否覆盖已存在的文件，默认 False
            timeout: 请求超时时间（秒），默认 30 秒
            verify_ssl: 是否验证 SSL 证书，默认 True

        Returns:
            保存的文件路径（相对于 MEDIA_ROOT），失败返回 None

        Example:
            downloader = ImageDownloader()
            path = downloader.download("https://example.com/image.jpg")
        """
        if not filename:
            # 从 URL 提取文件名
            filename = url.split('/')[-1]
            # 移除查询参数
            filename = filename.split('?')[0]

        filepath = self.base_dir / filename

        # 检查文件是否存在
        if filepath.exists() and not overwrite:
            print(f"文件已存在，跳过: {filepath}")
            return str(filepath.relative_to(settings.MEDIA_ROOT))

        try:
            # 发送请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers,
                verify=verify_ssl
            )
            response.raise_for_status()

            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"下载成功: {filepath}")
            return str(filepath.relative_to(settings.MEDIA_ROOT))

        except requests.exceptions.RequestException as e:
            print(f"下载失败 {url}: {e}")
            return None
        except IOError as e:
            print(f"保存文件失败 {filepath}: {e}")
            return None

    def download_batch(
        self,
        urls: List[Union[str, dict]],
        overwrite: bool = False,
        timeout: int = 30,
        verify_ssl: bool = True,
        show_progress: bool = False
    ) -> List[str]:
        """
        批量下载图片

        Args:
            urls: URL 列表或字典列表
                  - 如果是字符串，直接作为 URL
                  - 如果是字典，必须包含 'url' 键，可选包含 'filename' 键
            overwrite: 是否覆盖已存在的文件，默认 False
            timeout: 请求超时时间（秒），默认 30 秒
            verify_ssl: 是否验证 SSL 证书，默认 True
            show_progress: 是否显示进度，默认 False

        Returns:
            成功下载的文件路径列表

        Example:
            urls = [
                'https://example.com/image1.jpg',
                {'url': 'https://example.com/image2.jpg', 'filename': 'custom.jpg'}
            ]
            downloader = ImageDownloader()
            paths = downloader.download_batch(urls)
        """
        results = []
        total = len(urls)

        for index, item in enumerate(urls):
            if isinstance(item, dict):
                url = item['url']
                filename = item.get('filename')
            else:
                url = item
                filename = None

            if show_progress:
                print(f"[{index + 1}/{total}] 下载中: {url}")

            result = self.download(url, filename, overwrite, timeout, verify_ssl)
            if result:
                results.append(result)

        print(f"批量下载完成: 成功 {len(results)}/{total}")
        return results

    def download_with_retry(
        self,
        url: str,
        filename: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 1,
        **kwargs
    ) -> Optional[str]:
        """
        带重试机制的下载

        Args:
            url: 图片 URL
            filename: 保存的文件名
            max_retries: 最大重试次数，默认 3 次
            retry_delay: 重试延迟（秒），默认 1 秒
            **kwargs: 其他参数传递给 download 方法

        Returns:
            保存的文件路径，失败返回 None
        """
        import time

        for attempt in range(max_retries):
            result = self.download(url, filename, **kwargs)
            if result:
                return result

            if attempt < max_retries - 1:
                print(f"重试 {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)

        print(f"下载失败，已达到最大重试次数: {url}")
        return None

    def get_file_size(self, filename: str) -> Optional[int]:
        """
        获取文件大小

        Args:
            filename: 文件名

        Returns:
            文件大小（字节），文件不存在返回 None
        """
        filepath = self.base_dir / filename
        if filepath.exists():
            return filepath.stat().st_size
        return None

    def delete_file(self, filename: str) -> bool:
        """
        删除文件

        Args:
            filename: 文件名

        Returns:
            删除成功返回 True，失败返回 False
        """
        filepath = self.base_dir / filename
        try:
            if filepath.exists():
                filepath.unlink()
                print(f"删除成功: {filepath}")
                return True
            return False
        except Exception as e:
            print(f"删除失败 {filepath}: {e}")
            return False