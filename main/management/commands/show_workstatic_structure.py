from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Show structure of main_workstatic table'

    def handle(self, *args, **options):
        with connections['view_data_db'].cursor() as cursor:
            # 查看表结构
            cursor.execute("PRAGMA table_info(main_workstatic);")
            columns = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('Structure of main_workstatic table:'))
            for col in columns:
                self.stdout.write(f"- {col[1]} ({col[2]}) - NOT NULL: {col[3]} - DEFAULT: {col[4]}")
                
            # 查看表中的数据条数
            cursor.execute("SELECT COUNT(*) FROM main_workstatic;")
            count = cursor.fetchone()[0]
            self.stdout.write(f"\nTotal records: {count}")