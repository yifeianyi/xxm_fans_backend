from django.core.management.base import BaseCommand
from main.models import Songs, SongRecord
from django.db.models import Max, Count

class Command(BaseCommand):
    help = "重新计算 Songs 表中的 perform_count 和 last_performed 字段"

    def handle(self, *args, **options):
        updated = 0
        for song in Songs.objects.all():
            records = SongRecord.objects.filter(song=song)

            if records.exists():
                count = records.count()
                last_date = records.aggregate(Max('performed_at'))['performed_at__max']

                song.perform_count = count
                song.last_performed = last_date
                song.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ 成功更新 {updated} 首歌曲"))
