import os
import logging
from collections import deque
from django.core.management.base import BaseCommand
from gallery.models import Gallery
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '从文件夹结构自动生成图集树（迭代实现，支持任意深度）'

    # 支持的图片和视频格式
    SUPPORTED_EXTENSIONS = Gallery.SUPPORTED_EXTENSIONS
    COVER_FILENAME = Gallery.COVER_FILENAME

    def handle(self, *args, **options):
        gallery_root = os.path.join(settings.MEDIA_ROOT, 'gallery')

        if not os.path.exists(gallery_root):
            self.stdout.write(self.style.ERROR(f'图集目录不存在: {gallery_root}'))
            return

        # 统计信息
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        # 使用队列进行迭代扫描，避免递归深度限制
        # 队列元素: (文件夹路径, 父图集实例, 层级)
        queue = deque([(gallery_root, None, 0)])
        
        while queue:
            folder_path, parent, level = queue.popleft()
            
            try:
                items = os.listdir(folder_path)
            except OSError as e:
                self.stdout.write(self.style.ERROR(f'无法读取目录 {folder_path}: {e}'))
                stats['errors'] += 1
                continue

            for item in items:
                item_path = os.path.join(folder_path, item)

                if os.path.isdir(item_path):
                    try:
                        result = self._process_gallery_folder(
                            item_path, item, parent, level
                        )
                        if result:
                            if result['created']:
                                stats['created'] += 1
                            else:
                                stats['updated'] += 1
                            # 将子文件夹加入队列，稍后处理（迭代而非递归）
                            queue.append((item_path, result['instance'], level + 1))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'处理文件夹 {item_path} 时出错: {e}'))
                        logger.error(f'同步图集失败: {item_path}', exc_info=True)
                        stats['errors'] += 1

        # 刷新根图集的图片数量（迭代实现会自动处理所有子图集）
        try:
            root_galleries = Gallery.objects.filter(parent__isnull=True)
            for root_gallery in root_galleries:
                root_gallery.refresh_image_count()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'刷新图片数量时出错: {e}'))
            logger.error('刷新图片数量失败', exc_info=True)

        # 输出统计信息
        self.stdout.write(self.style.SUCCESS(
            f'图集同步完成！创建: {stats["created"]}, 更新: {stats["updated"]}, 错误: {stats["errors"]}'
        ))

    def _process_gallery_folder(self, item_path, item_name, parent, level):
        """处理单个图集文件夹"""
        # 计算相对路径
        rel_path = os.path.relpath(item_path, settings.MEDIA_ROOT)
        folder_url = '/' + rel_path.replace('\\', '/') + '/'

        # 检查是否有封面
        cover_path = os.path.join(item_path, self.COVER_FILENAME)
        cover_url = f'{folder_url}{self.COVER_FILENAME}' if os.path.exists(cover_path) else ''

        # 计算图片数量
        try:
            files = os.listdir(item_path)
            image_files = [f for f in files
                         if f.lower().endswith(self.SUPPORTED_EXTENSIONS)
                         and f != self.COVER_FILENAME]
        except OSError:
            image_files = []

        # 生成图集ID：使用相对路径的规范化形式
        gallery_id = rel_path.replace('\\', '-').replace('/', '-')

        # 创建或更新图集
        gallery, created = Gallery.objects.update_or_create(
            id=gallery_id,
            defaults={
                'title': item_name,
                'description': f'{item_name}图集',
                'cover_url': cover_url,
                'parent': parent,
                'level': level,
                'image_count': len(image_files),
                'folder_path': folder_url,
                'tags': [],
                'is_active': True
            }
        )

        action = '创建' if created else '更新'
        self.stdout.write(self.style.SUCCESS(f'{action}图集: {gallery.title} ({len(image_files)} 张图片)'))

        return {'instance': gallery, 'created': created}
