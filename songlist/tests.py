from django.test import TestCase
from .models import Song, SiteSetting


class SongModelTest(TestCase):
    """Song模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.song = Song.objects.create(
            song_name='测试歌曲',
            singer='测试歌手',
            language='中文',
            style='流行',
            note='测试备注'
        )

    def test_song_creation(self):
        """测试歌曲创建"""
        self.assertEqual(self.song.song_name, '测试歌曲')
        self.assertEqual(self.song.singer, '测试歌手')
        self.assertEqual(self.song.language, '中文')
        self.assertEqual(self.song.style, '流行')
        self.assertEqual(self.song.note, '测试备注')

    def test_song_str(self):
        """测试歌曲字符串表示"""
        self.assertEqual(str(self.song), '测试歌曲')

    def test_song_ordering(self):
        """测试歌曲排序"""
        song2 = Song.objects.create(
            song_name='A歌曲',
            singer='歌手A',
            language='英文',
            style='摇滚'
        )
        songs = list(Song.objects.all())
        self.assertEqual(songs[0].song_name, 'A歌曲')
        self.assertEqual(songs[1].song_name, '测试歌曲')


class SiteSettingModelTest(TestCase):
    """SiteSetting模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.setting = SiteSetting.objects.create(
            photo_url='https://example.com/photo.jpg',
            position=1
        )

    def test_site_setting_creation(self):
        """测试网站设置创建"""
        self.assertEqual(self.setting.photo_url, 'https://example.com/photo.jpg')
        self.assertEqual(self.setting.position, 1)

    def test_site_setting_str(self):
        """测试网站设置字符串表示"""
        self.assertEqual(str(self.setting), '设置 - 位置: 头像图标')

    def test_position_choices(self):
        """测试位置选择项"""
        self.assertEqual(self.setting.get_position_display(), '头像图标')