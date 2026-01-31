"""
Django 管理命令 - 清理缓存

使用方法:
    python manage.py clear_cache                    # 清理所有缓存
    python manage.py clear_cache pattern            # 清理匹配指定模式的缓存
    python manage.py clear_cache song_detail:1      # 清理 song_detail:1 缓存
    python manage.py clear_cache top_songs          # 清理所有 top_songs 缓存
    python manage.py clear_cache original_works_list # 清理原创作品列表缓存
"""
from django.core.management.base import BaseCommand
from core.cache import clear_cache_pattern, clear_all_cache


class Command(BaseCommand):
    help = '精细化清理缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            'pattern',
            type=str,
            nargs='?',
            help='缓存键模式（支持通配符），不指定则清理所有缓存'
        )

    def handle(self, *args, **options):
        pattern = options.get('pattern')

        if pattern:
            self.stdout.write(self.style.WARNING(f'清理匹配模式 *{pattern}* 的缓存...'))
            clear_cache_pattern(pattern)
            self.stdout.write(self.style.SUCCESS(f'✓ 匹配模式 *{pattern}* 的缓存已清理'))
        else:
            self.stdout.write(self.style.WARNING('清理所有缓存...'))
            clear_all_cache()
            self.stdout.write(self.style.SUCCESS('✓ 所有缓存已清理'))