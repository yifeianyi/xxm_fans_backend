"""
清除 livefans 中的假数据（测试/开发阶段导入的模拟粉丝数据）。

使用方式：
    python manage.py clear_fake_fans_data [--dry-run] [--keep-profiles]

在 咻咻满 尚未在 B站开播前，所有 FanProfile 和 LiveAttendance 数据均为假数据，
此命令用于清理这些假数据，使 API 返回空结果（前端会显示 "暂无数据" 状态）。
"""
from django.core.management.base import BaseCommand
from livefans.models import FanProfile, LiveAttendance


class Command(BaseCommand):
    help = '清除 livefans 中所有假数据（粉丝画像 + 出勤记录）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅预览将要删除的数据数量，不实际删除',
        )
        parser.add_argument(
            '--keep-profiles',
            action='store_true',
            help='仅清除出勤记录，保留粉丝画像（用于重新开始统计）',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        keep_profiles = options['keep_profiles']

        attendance_count = LiveAttendance.objects.count()
        profile_count = FanProfile.objects.count()

        self.stdout.write(f'当前假数据统计：')
        self.stdout.write(f'  粉丝画像 (FanProfile): {profile_count} 条')
        self.stdout.write(f'  出勤记录 (LiveAttendance): {attendance_count} 条')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] 以上数据将被删除，但未实际执行。'))
            return

        # 先删出勤记录（外键约束）
        deleted_attendance, _ = LiveAttendance.objects.all().delete()
        self.stdout.write(f'\n已删除出勤记录: {deleted_attendance} 条')

        if not keep_profiles:
            deleted_profiles, _ = FanProfile.objects.all().delete()
            self.stdout.write(f'已删除粉丝画像: {deleted_profiles} 条')
        else:
            self.stdout.write(f'已保留粉丝画像: {profile_count} 条（--keep-profiles 模式）')

        self.stdout.write(self.style.SUCCESS('\n✓ 假数据清理完成'))
