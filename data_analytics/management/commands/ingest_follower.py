from django.core.management.base import BaseCommand
from data_analytics.services.follower_service import FollowerService
import json
import os


class Command(BaseCommand):
    help = '导入粉丝数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='指定单个 JSON 文件'
        )
        parser.add_argument(
            '--dir',
            type=str,
            default='data/spider/fans_count',
            help='指定数据目录'
        )

    def handle(self, *args, **options):
        file_path = options.get('file')
        dir_path = options.get('dir')

        if file_path:
            self.import_from_file(file_path)
        else:
            self.import_from_directory(dir_path)

    def import_from_file(self, file_path):
        """从单个文件导入"""
        self.stdout.write(f'正在导入文件: {file_path}')

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        result = FollowerService.ingest_from_spider_data(data)

        self.stdout.write(f'\n导入结果:')
        self.stdout.write(f'  成功: {result["success_count"]}')
        self.stdout.write(f'  失败: {result["error_count"]}')

        if result['errors']:
            self.stdout.write(f'\n错误详情:')
            for error in result['errors']:
                self.stdout.write(f'  - {error}')

        # 导入成功后，预生成缓存
        if result['success_count'] > 0:
            self.stdout.write('\n开始预生成缓存...')
            FollowerService.generate_all_caches()
            self.stdout.write(self.style.SUCCESS('✓ 缓存预生成完成'))

    def import_from_directory(self, dir_path):
        """从目录导入所有文件"""
        json_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.startswith('b_fans_count_') and file.endswith('.json'):
                    json_files.append(os.path.join(root, file))

        json_files.sort()

        self.stdout.write(f'找到 {len(json_files)} 个数据文件')
        self.stdout.write('=' * 50)

        for json_file in json_files:
            try:
                self.import_from_file(json_file)
                self.stdout.write('-' * 50)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'导入失败: {str(e)}'))
                self.stdout.write('-' * 50)
