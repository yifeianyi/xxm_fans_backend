from django.core.management.base import BaseCommand
from django.db import connection
from songlist.models import Song, SiteSetting


class Command(BaseCommand):
    help = '从db.sqlite3迁移数据到songlist应用，区分youyou和bingjie歌手'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始数据迁移...'))

        # 清空现有数据
        self.stdout.write('清空现有数据...')
        Song.objects.all().delete()
        SiteSetting.objects.all().delete()

        # 迁移youyou数据
        self.stdout.write('迁移youyou数据...')
        youyou_song_count = self.migrate_artist_data(
            'youyou_SongList_you_songs',
            'youyou_SongList_you_site_setting',
            'youyou'
        )
        self.stdout.write(self.style.SUCCESS(f'youyou歌曲迁移完成: {youyou_song_count}首'))

        # 迁移bingjie数据
        self.stdout.write('迁移bingjie数据...')
        bingjie_song_count = self.migrate_artist_data(
            'bingjie_SongList_bingjie_songs',
            'bingjie_SongList_bingjie_site_setting',
            'bingjie'
        )
        self.stdout.write(self.style.SUCCESS(f'bingjie歌曲迁移完成: {bingjie_song_count}首'))

        # 统计总数
        total_songs = Song.objects.count()
        total_settings = SiteSetting.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'数据迁移完成！\n'
            f'总歌曲数: {total_songs}\n'
            f'总设置数: {total_settings}\n'
            f'  - youyou: {youyou_song_count}首\n'
            f'  - bingjie: {bingjie_song_count}首'
        ))

    def migrate_artist_data(self, songs_table, settings_table, artist):
        """迁移指定歌手的数据"""
        cursor = connection.cursor()

        # 迁移歌曲数据
        cursor.execute(f'''
            SELECT song_name, language, singer, style, note
            FROM {songs_table}
        ''')
        songs_data = cursor.fetchall()

        song_count = 0
        for row in songs_data:
            song_name, language, singer, style, note = row
            Song.objects.create(
                song_name=song_name,
                language=language,
                singer=singer,
                style=style,
                note=note,
                artist=artist
            )
            song_count += 1

        # 迁移网站设置数据
        cursor.execute(f'''
            SELECT photoURL, position
            FROM {settings_table}
        ''')
        settings_data = cursor.fetchall()

        for row in settings_data:
            photo_url, position = row
            SiteSetting.objects.create(
                photo_url=photo_url,
                position=position,
                artist=artist
            )

        return song_count