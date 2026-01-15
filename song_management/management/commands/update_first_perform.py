"""
管理命令：自动更新所有歌曲的首次演唱时间
"""
from django.core.management.base import BaseCommand
from song_management.models import Song


class Command(BaseCommand):
    help = '根据演唱记录自动更新所有歌曲的首次演唱时间'

    def handle(self, *args, **options):
        self.stdout.write('开始更新歌曲的首次演唱时间...')

        songs = Song.objects.all()
        updated_count = 0
        skipped_count = 0

        for song in songs:
            records = song.records.all()

            if not records.exists():
                skipped_count += 1
                self.stdout.write(f'跳过歌曲 "{song.song_name}"（无演唱记录）')
                continue

            # 获取最早的演唱记录
            earliest_record = records.order_by('performed_at').first()

            if earliest_record:
                # 如果字段为空或者需要更新
                if song.first_perform is None or song.first_perform != earliest_record.performed_at:
                    song.first_perform = earliest_record.performed_at
                    song.save(update_fields=['first_perform'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ 更新歌曲 "{song.song_name}": 首次演唱时间 = {earliest_record.performed_at}'
                        )
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(f'跳过歌曲 "{song.song_name}"（已是最新的）')

        self.stdout.write(self.style.SUCCESS(f'\n完成！'))
        self.stdout.write(f'更新了 {updated_count} 首歌曲')
        self.stdout.write(f'跳过了 {skipped_count} 首歌曲')