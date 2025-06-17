from django.core.management.base import BaseCommand, CommandError
from main.models import Songs, SongRecord, SongStyle
from django.db import transaction

class Command(BaseCommand):
    help = 'Merge two Songs records. Usage: python manage.py merge_songs <from_id> <to_id>'

    def add_arguments(self, parser):
        parser.add_argument('from_id', type=int, help='The ID of the song to merge (will be deleted)')
        parser.add_argument('to_id', type=int, help='The ID of the song to keep (target song)')

    @transaction.atomic
    def handle(self, *args, **options):
        from_id = options['from_id']
        to_id = options['to_id']

        if from_id == to_id:
            raise CommandError('from_id and to_id must be different.')

        try:
            source = Songs.objects.get(id=from_id)
            target = Songs.objects.get(id=to_id)
        except Songs.DoesNotExist:
            raise CommandError('One or both song IDs do not exist.')

        self.stdout.write(f"🔁 正在合并 ID={from_id} → ID={to_id}...")

        # 更新 SongRecord 的 song 外键
        count = SongRecord.objects.filter(song=source).update(song=target)
        self.stdout.write(f"✅ 已更新 {count} 条演唱记录")

        # 合并 SongStyle，避免重复条目
        for ss in SongStyle.objects.filter(song=source):
            if not SongStyle.objects.filter(song=target, style=ss.style).exists():
                ss.song = target
                ss.save()
            else:
                ss.delete()

        # 合并字段
        target.perform_count = (target.perform_count or 0) + (source.perform_count or 0)
        if not target.last_performed or (source.last_performed and source.last_performed > target.last_performed):
            target.last_performed = source.last_performed

        target.save()
        source.delete()

        self.stdout.write(self.style.SUCCESS(f"🎉 合并完成！已删除 ID={from_id}，保留 ID={to_id}"))
