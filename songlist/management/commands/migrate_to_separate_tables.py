from django.core.management.base import BaseCommand
from django.db import connection
from songlist.models import YouyouSong, BingjieSong, YouyouSiteSetting, BingjieSiteSetting


class Command(BaseCommand):
    help = '从db.sqlite3迁移数据到独立的歌手表'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始数据迁移到独立表...'))

        # 清空现有数据
        self.stdout.write('清空现有数据...')
        YouyouSong.objects.all().delete()
        BingjieSong.objects.all().delete()
        YouyouSiteSetting.objects.all().delete()
        BingjieSiteSetting.objects.all().delete()

        # 迁移youyou数据
        self.stdout.write('迁移youyou数据...')
        youyou_song_count = self.migrate_youyou_data()
        self.stdout.write(self.style.SUCCESS(f'youyou歌曲迁移完成: {youyou_song_count}首'))

        # 迁移bingjie数据
        self.stdout.write('迁移bingjie数据...')
        bingjie_song_count = self.migrate_bingjie_data()
        self.stdout.write(self.style.SUCCESS(f'bingjie歌曲迁移完成: {bingjie_song_count}首'))

        # 统计总数
        total_youyou_songs = YouyouSong.objects.count()
        total_bingjie_songs = BingjieSong.objects.count()
        total_youyou_settings = YouyouSiteSetting.objects.count()
        total_bingjie_settings = BingjieSiteSetting.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'数据迁移完成！\n'
            f'总歌曲数: {total_youyou_songs + total_bingjie_songs}\n'
            f'  - youyou: {total_youyou_songs}首\n'
            f'  - bingjie: {total_bingjie_songs}首\n'
            f'总设置数: {total_youyou_settings + total_bingjie_settings}\n'
            f'  - youyou: {total_youyou_settings}条\n'
            f'  - bingjie: {total_bingjie_settings}条'
        ))

    def migrate_youyou_data(self):
        """迁移youyou数据"""
        cursor = connection.cursor()

        # 迁移歌曲数据
        cursor.execute('''
            SELECT song_name, language, singer, style, note
            FROM youyou_SongList_you_songs
        ''')
        songs_data = cursor.fetchall()

        song_count = 0
        for row in songs_data:
            song_name, language, singer, style, note = row
            YouyouSong.objects.create(
                song_name=song_name,
                language=language,
                singer=singer,
                style=style,
                note=note
            )
            song_count += 1

        # 迁移网站设置数据
        cursor.execute('''
            SELECT photoURL, position
            FROM youyou_SongList_you_site_setting
        ''')
        settings_data = cursor.fetchall()

        for row in settings_data:
            photo_url, position = row
            YouyouSiteSetting.objects.create(
                photo_url=photo_url,
                position=position
            )

        return song_count

    def migrate_bingjie_data(self):
        """迁移bingjie数据"""
        cursor = connection.cursor()

        # 迁移歌曲数据
        cursor.execute('''
            SELECT song_name, language, singer, style, note
            FROM bingjie_SongList_bingjie_songs
        ''')
        songs_data = cursor.fetchall()

        song_count = 0
        for row in songs_data:
            song_name, language, singer, style, note = row
            BingjieSong.objects.create(
                song_name=song_name,
                language=language,
                singer=singer,
                style=style,
                note=note
            )
            song_count += 1

        # 迁移网站设置数据
        cursor.execute('''
            SELECT photoURL, position
            FROM bingjie_SongList_bingjie_site_setting
        ''')
        settings_data = cursor.fetchall()

        for row in settings_data:
            photo_url, position = row
            BingjieSiteSetting.objects.create(
                photo_url=photo_url,
                position=position
            )

        return song_count
