from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Check is_valid values in main_workstatic table'

    def handle(self, *args, **options):
        with connections['view_data_db'].cursor() as cursor:
            # 检查is_valid字段的值分布
            cursor.execute("SELECT is_valid, COUNT(*) FROM main_workstatic GROUP BY is_valid;")
            results = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('is_valid value distribution:'))
            for result in results:
                self.stdout.write(f"- is_valid={result[0]}: {result[1]} records")
                
            # 检查是否有NULL值
            cursor.execute("SELECT COUNT(*) FROM main_workstatic WHERE is_valid IS NULL;")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                self.stdout.write(self.style.WARNING(f"\nFound {null_count} records with NULL is_valid"))
            else:
                self.stdout.write(self.style.SUCCESS('\nNo records with NULL is_valid'))