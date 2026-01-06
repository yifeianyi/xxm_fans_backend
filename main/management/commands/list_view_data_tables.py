from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'List all tables in the view_data database'

    def handle(self, *args, **options):
        with connections['view_data_db'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('View_data database tables:'))
            for table in tables:
                self.stdout.write(f"- {table[0]}")
                
            # 查找包含workstatus的表
            workstatus_tables = [table[0] for table in tables if 'workstatus' in table[0].lower()]
            if workstatus_tables:
                self.stdout.write(self.style.SUCCESS('\nFound WorkStatus tables:'))
                for table in workstatus_tables:
                    self.stdout.write(f"- {table[0]}")
                    
                    # 查看表结构
                    cursor.execute(f"PRAGMA table_info({table[0]});")
                    columns = cursor.fetchall()
                    self.stdout.write(f"  Columns:")
                    for col in columns:
                        self.stdout.write(f"    - {col[1]} ({col[2]})")