import logging
import os
import requests
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from core.thumbnail_generator import ThumbnailGenerator

logger = logging.getLogger(__name__)


class ImageService:
    DOWNLOAD_TIMEOUT = 15
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'}

    @classmethod
    def download_and_generate_thumbnails(cls, source, source_id, image_urls):
        """
        下载图片并生成缩略图

        Args:
            source: 'weibo' 或 'bilibili'
            source_id: 动态的原始平台 ID
            image_urls: 图片 URL 列表

        Returns:
            list: [{"original_url": "/media/moments/...", "thumbnail_url": "/media/moments/..."}]
        """
        result = []
        for idx, url in enumerate(image_urls):
            if not url:
                continue
            try:
                image_path = cls._download_image(source, source_id, url, idx)
                if image_path:
                    thumbnail_path = ThumbnailGenerator.generate_thumbnail(image_path)
                    original_url = f'/media/{image_path}'
                    thumbnail_url = f'/media/{thumbnail_path}' if thumbnail_path != image_path else original_url
                    result.append({
                        'original_url': original_url,
                        'thumbnail_url': thumbnail_url,
                    })
            except Exception as e:
                logger.warning("下载图片失败 [%s:%s] idx=%d: %s", source, source_id, idx, e)

        return result

    @classmethod
    def _download_image(cls, source, source_id, url, idx):
        """
        下载单张图片到 media/moments/ 目录

        Returns:
            str: 图片存储路径，失败返回 None
        """
        try:
            response = requests.get(url, timeout=cls.DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()

            # 校验 Content-Type 是否为图片
            content_type = response.headers.get('content-type', '').split(';')[0].strip().lower()
            if content_type not in cls.ALLOWED_CONTENT_TYPES:
                logger.warning("跳过非图片响应 [%s] content-type=%s", url, content_type)
                return None

            ext = cls._get_extension(url, content_type)
            if ext == 'svg':
                logger.warning("跳过 SVG 文件 [%s]（安全策略禁止）", url)
                return None

            filename = f'{source}_{source_id}_{idx}.{ext}'
            relative_path = f'moments/{source}/{filename}'

            full_path = os.path.join(default_storage.location, relative_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            downloaded_size = 0
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if downloaded_size > cls.MAX_FILE_SIZE:
                        f.close()
                        os.remove(full_path)
                        logger.warning("图片过大，已跳过 [%s] size=%d", url, downloaded_size)
                        return None

            return relative_path

        except Exception as e:
            logger.warning("下载图片异常 [%s]: %s", url, e)
            return None

    @classmethod
    def _get_extension(cls, url, content_type):
        """从 URL 或 Content-Type 推断文件扩展名"""
        path = url.split('?')[0]
        ext = Path(path).suffix.lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'):
            return ext.lstrip('.')
        if 'png' in content_type:
            return 'png'
        if 'gif' in content_type:
            return 'gif'
        if 'webp' in content_type:
            return 'webp'
        return 'jpg'
