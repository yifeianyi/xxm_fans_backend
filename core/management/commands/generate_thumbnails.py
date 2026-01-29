"""
Django 管理命令 - 批量生成缩略图
"""
from django.core.management.base import BaseCommand, CommandError
from core.thumbnail_generator import ThumbnailGenerator


class Command(BaseCommand):
    help = '批量生成缩略图'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            choices=['gallery', 'covers', 'footprint'],
            help='指定模块（gallery/covers/footprint），不指定则生成所有模块的缩略图',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成所有缩略图',
        )

    def handle(self, *args, **options):
        module = options.get('module')
        force = options.get('force', False)

        self.stdout.write(self.style.SUCCESS('开始生成缩略图...'))
        
        if module:
            self.stdout.write(f'模块: {module}')
        else:
            self.stdout.write('模块: 全部')
        
        if force:
            self.stdout.write('模式: 强制重新生成')
        else:
            self.stdout.write('模式: 仅生成缺失或过期的缩略图')

        self.stdout.write('')

        # 批量生成缩略图
        stats = ThumbnailGenerator.batch_generate_thumbnails(module=module, force=force)

        # 显示结果
        self.stdout.write(self.style.SUCCESS('生成完成！'))
        self.stdout.write(f'总计: {stats["total"]} 张图片')
        self.stdout.write(self.style.SUCCESS(f'成功: {stats["success"]} 张'))
        self.stdout.write(self.style.WARNING(f'跳过: {stats["skipped"]} 张'))
        if stats['failed'] > 0:
            self.stdout.write(self.style.ERROR(f'失败: {stats["failed"]} 张'))

        # 显示错误详情
        if stats['errors']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('错误详情:'))
            for error in stats['errors'][:10]:  # 只显示前10个错误
                self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if len(stats['errors']) > 10:
                self.stdout.write(self.style.ERROR(f'  ... 还有 {len(stats["errors"]) - 10} 个错误'))

        self.stdout.write('')
        if stats['failed'] == 0:
            self.stdout.write(self.style.SUCCESS('所有缩略图生成成功！'))
        else:
            self.stdout.write(self.style.WARNING(f'部分缩略图生成失败，请检查错误详情'))