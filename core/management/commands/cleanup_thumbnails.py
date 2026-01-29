"""
Django 管理命令 - 清理孤立缩略图
"""
from django.core.management.base import BaseCommand
from core.thumbnail_generator import ThumbnailGenerator


class Command(BaseCommand):
    help = '清理孤立缩略图（原图已不存在的缩略图）'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始清理孤立缩略图...'))
        self.stdout.write('')

        # 清理孤立缩略图
        stats = ThumbnailGenerator.cleanup_orphan_thumbnails()

        # 显示结果
        self.stdout.write(self.style.SUCCESS('清理完成！'))
        self.stdout.write(f'总计扫描: {stats["total"]} 个缩略图')
        self.stdout.write(self.style.SUCCESS(f'已删除: {stats["deleted"]} 个'))

        # 显示错误详情
        if stats['errors']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('错误详情:'))
            for error in stats['errors'][:10]:  # 只显示前10个错误
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if len(stats['errors']) > 10:
                self.stdout.write(self.style.ERROR(f'  ... 还有 {len(stats["errors"]) - 10} 个错误'))

        self.stdout.write('')
        if stats['deleted'] == 0:
            self.stdout.write(self.style.SUCCESS('没有发现孤立缩略图'))
        else:
            self.stdout.write(self.style.SUCCESS(f'成功清理 {stats["deleted"]} 个孤立缩略图'))