from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Search for tables with specific pattern in view_data database'

    def handle(self, *args, **options):
        with connections['view_data_db'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('All tables in view_data database:'))
            for table in tables:
                self.stdout.write(f"- {table[0]}")
                
            # 搜索包含status的表
            status_tables = [table[0] for table in tables if 'status' in table[0].lower()]
            if status_tables:
                self.stdout.write(self.style.SUCCESS('\nTables containing "status":'))
                for table in status_tables:
                    self.stdout.write(f"- {table[0]}")
            else:
                self.stdout.write(self.style.WARNING('\nNo tables containing "status" found.'))