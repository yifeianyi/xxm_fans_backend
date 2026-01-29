"""
图集缩略图生成工具模块
"""
import os
from pathlib import Path
from PIL import Image
from django.core.files.storage import default_storage
from django.conf import settings


class ThumbnailGenerator:
    """缩略图生成器 - 保持原图目录结构"""

    THUMBNAIL_DIR = 'gallery/thumbnails/'
    THUMBNAIL_SIZE = (400, 400)  # 最大宽高
    QUALITY = 85

    @classmethod
    def get_thumbnail_path(cls, original_path: str) -> str:
        """获取缩略图存储路径 - 保持原图的目录结构"""
        original_path = original_path.lstrip('/')
        
        # 移除 'gallery/' 前缀，添加 'gallery/thumbnails/' 前缀
        if original_path.startswith('gallery/'):
            relative_path = original_path[8:]  # 移除 'gallery/'
        else:
            relative_path = original_path
        
        # 解析原文件扩展名
        ext = Path(original_path).suffix.lower()
        
        # 统一使用 webp 格式（除了 GIF）
        if ext == '.gif':
            output_ext = '.gif'
        else:
            output_ext = '.webp'
        
        # 构建缩略图路径：保持原图的目录结构
        thumbnail_path = os.path.join(cls.THUMBNAIL_DIR, relative_path)
        # 替换文件扩展名
        thumbnail_path = Path(thumbnail_path).with_suffix(output_ext).as_posix()
        
        return thumbnail_path

    @classmethod
    def generate_thumbnail(cls, original_path: str) -> str:
        """生成缩略图"""
        original_path = original_path.lstrip('/')
        thumbnail_path = cls.get_thumbnail_path(original_path)

        # 检查缩略图是否已存在
        if default_storage.exists(thumbnail_path):
            return thumbnail_path

        # 读取原图片
        try:
            with default_storage.open(original_path, 'rb') as f:
                img = Image.open(f)

                # 处理 GIF：只取第一帧
                if getattr(img, 'is_animated', False):
                    img.seek(0)
                    img = img.convert('RGB')

                # 计算缩略图尺寸（保持宽高比）
                img.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # 创建缩略图目录（保持原图的目录结构）
                thumb_dir = os.path.dirname(thumbnail_path)
                thumb_dir_full = os.path.join(default_storage.location, thumb_dir)
                if not os.path.exists(thumb_dir_full):
                    os.makedirs(thumb_dir_full, exist_ok=True)

                # 保存缩略图
                output_ext = Path(thumbnail_path).suffix.lower()
                save_kwargs = {}
                thumbnail_full_path = os.path.join(default_storage.location, thumbnail_path)

                if output_ext in ['.jpg', '.jpeg']:
                    img.save(thumbnail_full_path, 'JPEG', quality=cls.QUALITY, optimize=True)
                elif output_ext == '.png':
                    img.save(thumbnail_full_path, 'PNG', optimize=True)
                elif output_ext == '.webp':
                    img.save(thumbnail_full_path, 'WEBP', quality=cls.QUALITY, method=6)
                elif output_ext == '.gif':
                    img.save(thumbnail_full_path, 'GIF')

                return thumbnail_path

        except Exception as e:
            print(f"生成缩略图失败: {original_path}, 错误: {e}")
            return original_path  # 失败时返回原图路径

    @classmethod
    def get_thumbnail_url(cls, original_url: str) -> str:
        """获取缩略图 URL"""
        if not original_url:
            return original_url

        original_path = original_url.lstrip('/')
        thumbnail_path = cls.generate_thumbnail(original_path)

        if thumbnail_path == original_path:
            return original_url

        # 转换为 URL
        return f"/media/{thumbnail_path}"