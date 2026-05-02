"""
歌曲管理模型测试 - Commit #3
覆盖：Song 排序字段索引、SongRecord 索引注释
"""
import os

from django.test import TestCase

from song_management.models import Song, SongRecord


class SongModelIndexTest(TestCase):
    """Song 模型索引测试"""

    def test_migration_file_contains_add_index(self):
        """验证生成的 migration 文件包含 AddIndex 操作"""
        migration_dir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'song_management', 'migrations'
        )
        # 找到最新的 migration 文件（通常是编号最大的）
        migration_files = [
            f for f in os.listdir(migration_dir)
            if f.startswith('0005') and f.endswith('.py') and not f.endswith('.pyc')
        ]
        self.assertTrue(
            len(migration_files) > 0,
            "应存在包含索引变更的 migration 文件"
        )
        migration_path = os.path.join(migration_dir, migration_files[0])
        with open(migration_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("AddIndex", content)
        self.assertIn("last_performed", content)
        self.assertIn("perform_count", content)

    def test_song_ordering_by_last_performed_executes(self):
        """按 last_performed 排序应正常执行（不报错）"""
        Song.objects.bulk_create([
            Song(
                song_name=f"歌曲{i}",
                last_performed=f"2024-01-{i+1:02d}",
                perform_count=i,
            )
            for i in range(10)
        ])
        songs = list(Song.objects.order_by('-last_performed'))
        self.assertEqual(len(songs), 10)

    def test_song_ordering_by_perform_count_executes(self):
        """按 perform_count 排序应正常执行（不报错）"""
        Song.objects.bulk_create([
            Song(
                song_name=f"歌曲{i}",
                last_performed=f"2024-01-{i+1:02d}",
                perform_count=i,
            )
            for i in range(10)
        ])
        songs = list(Song.objects.order_by('-perform_count'))
        self.assertEqual(len(songs), 10)


class SongRecordIndexDocsTest(TestCase):
    """SongRecord 索引文档测试"""

    def test_index_comment_exists(self):
        """验证模型源码中包含索引相关注释"""
        import inspect
        source = inspect.getsource(SongRecord)
        self.assertIn("DESC", source)
        self.assertIn("反向扫描", source)
        self.assertIn("PostgreSQL", source)

    def test_index_migration_runnable(self):
        """验证 migrate --plan 可正常执行"""
        from django.core.management import call_command
        # 调用 migrate --plan 不应抛出异常
        call_command('migrate', '--plan', verbosity=0)
