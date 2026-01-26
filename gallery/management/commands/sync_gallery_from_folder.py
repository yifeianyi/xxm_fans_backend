import os
from django.core.management.base import BaseCommand
from gallery.models import Gallery
from django.conf import settings


class Command(BaseCommand):
    help = '从文件夹结构自动生成图集树'

    def handle(self, *args, **options):
        gallery_root = os.path.join(settings.MEDIA_ROOT, 'gallery')

        if not os.path.exists(gallery_root):
            self.stdout.write(self.style.ERROR(f'图集目录不存在: {gallery_root}'))
            return

        # 递归扫描文件夹
        def scan_folder(folder_path, parent=None, level=0):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)

                if os.path.isdir(item_path):
                    # 计算相对路径
                    rel_path = os.path.relpath(item_path, settings.MEDIA_ROOT)
                    folder_url = '/' + rel_path.replace('\\', '/') + '/'

                    # 检查是否有封面
                    cover_path = os.path.join(item_path, 'cover.jpg')
                    cover_url = f'{folder_url}cover.jpg' if os.path.exists(cover_path) else ''

                    # 计算图片数量
                    image_files = [f for f in os.listdir(item_path)
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4'))
                                 and f != 'cover.jpg']

                    # 生成图集ID
                    gallery_id = rel_path.replace('\\', '-').replace('/', '-')

                    # 创建或更新图集
                    gallery, created = Gallery.objects.update_or_create(
                        id=gallery_id,
                        defaults={
                            'title': item,
                            'description': f'{item}图集',
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
                    self.stdout.write(self.style.SUCCESS(f'{action}图集: {gallery.title} ({gallery.image_count} 张图片)'))

                    # 递归处理子文件夹
                    scan_folder(item_path, gallery, level + 1)

        # 开始扫描
        scan_folder(gallery_root)

        # 递归刷新所有父图集的图片数量
        def refresh_parent_counts(gallery):
            """递归刷新父图集的图片数量"""
            if gallery.parent:
                gallery.parent.refresh_image_count()
                refresh_parent_counts(gallery.parent)

        # 刷新根图集的图片数量（会递归刷新所有父图集）
        root_galleries = Gallery.objects.filter(parent__isnull=True)
        for root_gallery in root_galleries:
            root_gallery.refresh_image_count()

        self.stdout.write(self.style.SUCCESS('图集同步完成！'))