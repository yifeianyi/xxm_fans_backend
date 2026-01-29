"""
批量生成图集缩略图的管理命令
"""
from django.core.management.base import BaseCommand
from gallery.utils import ThumbnailGenerator
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = '批量生成图集缩略图'

    def handle(self, *args, **options):
        self.stdout.write('开始生成缩略图...')

        # 扫描 gallery 目录
        gallery_dir = 'gallery'
        if not default_storage.exists(gallery_dir):
            self.stdout.write(self.style.ERROR('gallery 目录不存在'))
            return

        # 递归扫描所有图片
        total_count = 0
        success_count = 0

        def scan_directory(directory):
            nonlocal total_count, success_count

            try:
                dirs, files = default_storage.listdir(directory)
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        total_count += 1
                        file_path = f"{directory}/{file}"

                        try:
                            thumbnail_path = ThumbnailGenerator.generate_thumbnail(file_path)
                            if thumbnail_path != file_path:
                                success_count += 1
                                self.stdout.write(f'✓ {file_path} -> {thumbnail_path}')
                            else:
                                self.stdout.write(f'- {file_path} (跳过)')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'✗ {file_path}: {e}'))

                for subdir in dirs:
                    scan_directory(f"{directory}/{subdir}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'扫描目录失败 {directory}: {e}'))

        scan_directory(gallery_dir)

        self.stdout.write(
            self.style.SUCCESS(
                f'完成！总共处理 {total_count} 个文件，成功生成 {success_count} 个缩略图'
            )
        )