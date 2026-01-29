"""
通用缩略图生成器 - 支持全站图片缩略图自动生成
"""
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from PIL import Image
from django.core.files.storage import default_storage
from django.conf import settings


class ThumbnailGenerator:
    """通用缩略图生成器 - 支持多模块缩略图管理"""

    # 各模块的缩略图配置
    MODULE_CONFIG = {
        'gallery': {
            'thumbnail_size': (400, 400),  # 最大边 400px
            'keep_aspect_ratio': True,
            'thumbnail_dir': 'gallery/thumbnails/',
        },
        'covers': {
            'thumbnail_size': (300, 300),  # 保持宽高比
            'keep_aspect_ratio': True,
            'thumbnail_dir': 'covers/thumbnails/',
        },
        'footprint': {
            'thumbnail_size': (300, 300),  # 保持宽高比
            'keep_aspect_ratio': True,
            'thumbnail_dir': 'footprint/thumbnails/',
        },
        'songlist': {
            'thumbnail_size': None,  # 不生成缩略图
            'keep_aspect_ratio': True,
            'thumbnail_dir': 'songlist/thumbnails/',
        },
        'settings': {
            'thumbnail_size': None,  # 不生成缩略图
            'keep_aspect_ratio': True,
            'thumbnail_dir': 'settings/thumbnails/',
        },
    }

    QUALITY = 85  # 图片质量

    @classmethod
    def get_module_from_path(cls, file_path: str) -> Optional[str]:
        """
        从文件路径提取模块名称

        Args:
            file_path: 图片文件路径

        Returns:
            模块名称，如果无法识别则返回 None
        """
        file_path = file_path.lstrip('/')
        
        for module in cls.MODULE_CONFIG.keys():
            if file_path.startswith(module + '/'):
                return module
        
        return None

    @classmethod
    def get_thumbnail_size(cls, module: str) -> Optional[Tuple[int, int]]:
        """
        获取指定模块的缩略图尺寸

        Args:
            module: 模块名称

        Returns:
            缩略图尺寸 (width, height)，如果不生成缩略图则返回 None
        """
        config = cls.MODULE_CONFIG.get(module)
        if config:
            return config.get('thumbnail_size')
        return None

    @classmethod
    def get_thumbnail_path(cls, original_path: str) -> str:
        """
        获取缩略图存储路径 - 保持原图的目录结构

        Args:
            original_path: 原图路径

        Returns:
            缩略图路径
        """
        original_path = original_path.lstrip('/')
        module = cls.get_module_from_path(original_path)
        
        if not module:
            return original_path  # 无法识别模块，返回原图路径
        
        config = cls.MODULE_CONFIG.get(module)
        if not config or not config.get('thumbnail_size'):
            return original_path  # 该模块不生成缩略图
        
        thumbnail_dir = config['thumbnail_dir']
        
        # 移除模块前缀，添加缩略图目录前缀
        if original_path.startswith(module + '/'):
            relative_path = original_path[len(module) + 1:]
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
        thumbnail_path = os.path.join(thumbnail_dir, relative_path)
        # 替换文件扩展名
        thumbnail_path = Path(thumbnail_path).with_suffix(output_ext).as_posix()
        
        return thumbnail_path

    @classmethod
    def generate_thumbnail(cls, original_path: str, force: bool = False) -> str:
        """
        生成缩略图（含自动更新检测）

        Args:
            original_path: 原图路径
            force: 是否强制重新生成

        Returns:
            缩略图路径，如果生成失败则返回原图路径
        """
        original_path = original_path.lstrip('/')
        module = cls.get_module_from_path(original_path)
        
        if not module:
            return original_path  # 无法识别模块
        
        config = cls.MODULE_CONFIG.get(module)
        if not config or not config.get('thumbnail_size'):
            return original_path  # 该模块不生成缩略图
        
        thumbnail_path = cls.get_thumbnail_path(original_path)
        thumbnail_size = config['thumbnail_size']
        keep_aspect_ratio = config['keep_aspect_ratio']

        # 检查缩略图是否已存在
        if not force and default_storage.exists(thumbnail_path):
            # 检查是否需要更新（比较修改时间）
            try:
                original_mtime = os.path.getmtime(os.path.join(default_storage.location, original_path))
                thumbnail_mtime = os.path.getmtime(os.path.join(default_storage.location, thumbnail_path))
                
                if original_mtime <= thumbnail_mtime:
                    return thumbnail_path  # 缩略图是最新的，直接返回
            except (OSError, FileNotFoundError):
                pass  # 文件不存在，继续生成

        # 读取原图片
        try:
            with default_storage.open(original_path, 'rb') as f:
                img = Image.open(f)

                # 处理 GIF：只取第一帧
                if getattr(img, 'is_animated', False):
                    img.seek(0)
                    img = img.convert('RGB')

                # 计算缩略图尺寸
                if keep_aspect_ratio:
                    img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                else:
                    # 裁剪到指定尺寸
                    img = cls._crop_to_size(img, thumbnail_size)

                # 创建缩略图目录（保持原图的目录结构）
                thumb_dir = os.path.dirname(thumbnail_path)
                thumb_dir_full = os.path.join(default_storage.location, thumb_dir)
                if not os.path.exists(thumb_dir_full):
                    os.makedirs(thumb_dir_full, exist_ok=True)

                # 保存缩略图
                output_ext = Path(thumbnail_path).suffix.lower()
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
    def _crop_to_size(cls, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        裁剪图片到指定尺寸（居中裁剪）

        Args:
            img: 原始图片
            target_size: 目标尺寸 (width, height)

        Returns:
            裁剪后的图片
        """
        width, height = img.size
        target_width, target_height = target_size

        # 计算缩放比例
        ratio = max(target_width / width, target_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # 缩放图片
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 计算裁剪位置（居中）
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        # 裁剪图片
        img = img.crop((left, top, right, bottom))

        return img

    @classmethod
    def delete_thumbnail(cls, original_path: str) -> bool:
        """
        删除缩略图

        Args:
            original_path: 原图路径

        Returns:
            是否成功删除
        """
        original_path = original_path.lstrip('/')
        thumbnail_path = cls.get_thumbnail_path(original_path)

        if thumbnail_path == original_path:
            return True  # 不生成缩略图，无需删除

        try:
            if default_storage.exists(thumbnail_path):
                default_storage.delete(thumbnail_path)
                return True
            return False
        except Exception as e:
            print(f"删除缩略图失败: {thumbnail_path}, 错误: {e}")
            return False

    @classmethod
    def get_thumbnail_url(cls, original_url: str) -> str:
        """
        获取缩略图 URL

        Args:
            original_url: 原图 URL

        Returns:
            缩略图 URL，如果生成失败则返回原图 URL
        """
        if not original_url:
            return original_url

        original_path = original_url.lstrip('/')
        thumbnail_path = cls.generate_thumbnail(original_path)

        if thumbnail_path == original_path:
            return original_url

        # 转换为 URL
        return f"/media/{thumbnail_path}"

    @classmethod
    def batch_generate_thumbnails(cls, module: Optional[str] = None, force: bool = False) -> Dict[str, any]:
        """
        批量生成缩略图

        Args:
            module: 指定模块，如果为 None 则生成所有模块的缩略图
            force: 是否强制重新生成

        Returns:
            统计信息字典
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        modules_to_process = [module] if module else list(cls.MODULE_CONFIG.keys())

        for mod in modules_to_process:
            config = cls.MODULE_CONFIG.get(mod)
            if not config or not config.get('thumbnail_size'):
                continue  # 跳过不生成缩略图的模块

            module_dir = mod + '/'
            if not default_storage.exists(module_dir):
                continue  # 模块目录不存在

            try:
                # 遍历模块目录下的所有图片
                module_full_path = os.path.join(default_storage.location, module_dir)
                if os.path.exists(module_full_path):
                    for root, dirs, files in os.walk(module_full_path):
                        for file in files:
                            # 检查文件扩展名
                            ext = Path(file).suffix.lower()
                            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                                continue

                            # 构建文件路径（相对于 storage location）
                            rel_path = os.path.relpath(os.path.join(root, file), default_storage.location)
                            file_path = rel_path.replace('\\', '/')
                            stats['total'] += 1

                            try:
                                thumbnail_path = cls.generate_thumbnail(file_path, force)
                                if thumbnail_path == file_path:
                                    stats['skipped'] += 1
                                else:
                                    stats['success'] += 1
                            except Exception as e:
                                stats['failed'] += 1
                                stats['errors'].append(f"{file_path}: {str(e)}")

            except Exception as e:
                stats['errors'].append(f"模块 {mod}: {str(e)}")

        return stats

    @classmethod
    def cleanup_orphan_thumbnails(cls) -> Dict[str, any]:
        """
        清理孤立缩略图（原图已不存在的缩略图）

        Returns:
            统计信息字典
        """
        stats = {
            'total': 0,
            'deleted': 0,
            'errors': []
        }

        for module, config in cls.MODULE_CONFIG.items():
            if not config.get('thumbnail_size'):
                continue  # 跳过不生成缩略图的模块

            thumbnail_dir = config['thumbnail_dir']
            if not default_storage.exists(thumbnail_dir):
                continue  # 缩略图目录不存在

            try:
                # 遍历缩略图目录
                thumbnail_full_path = os.path.join(default_storage.location, thumbnail_dir)
                if os.path.exists(thumbnail_full_path):
                    for root, dirs, files in os.walk(thumbnail_full_path):
                        for file in files:
                            # 构建缩略图路径（相对于 storage location）
                            thumbnail_path = os.path.relpath(os.path.join(root, file), default_storage.location).replace('\\', '/')
                            stats['total'] += 1

                            # 推算原图路径
                            thumbnail_path_relative = thumbnail_path.replace(thumbnail_dir, '')
                            original_path = os.path.join(module, thumbnail_path_relative)
                            
                            # 替换扩展名（从 webp 恢复到原图扩展名）
                            # 简单处理：假设原图存在，则删除缩略图；否则保留
                            # 更精确的做法是记录原图路径，这里简化处理
                            
                            try:
                                # 检查原图是否存在
                                # 这里简化处理：根据文件名查找对应的原图
                                original_file = Path(file).stem
                                original_dir = os.path.dirname(thumbnail_path_relative)
                                
                                # 尝试多种可能的原图扩展名
                                original_found = False
                                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                                    test_original = os.path.join(module, original_dir, original_file + ext)
                                    if default_storage.exists(test_original):
                                        original_found = True
                                        break
                                
                                if not original_found:
                                    # 原图不存在，删除缩略图
                                    default_storage.delete(thumbnail_path)
                                    stats['deleted'] += 1

                            except Exception as e:
                                stats['errors'].append(f"{thumbnail_path}: {str(e)}")

            except Exception as e:
                stats['errors'].append(f"模块 {module}: {str(e)}")

        return stats
