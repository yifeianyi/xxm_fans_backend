from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'List all tables in the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS('Database tables:'))
            for table in tables:
                self.stdout.write(f"- {table[0]}")