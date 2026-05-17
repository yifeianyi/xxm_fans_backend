"""
直播日历测试 - Commit #4
覆盖：列表模式避免隐式查询 SongRecord
"""
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.test.utils import CaptureQueriesContext
from django.db import connection

from livestream.models import Livestream
from song_management.models import SongRecord, Song


CACHES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'livestream-test',
    }
}


@override_settings(CACHES=CACHES_OVERRIDE)
class LivestreamQueryTest(TestCase):
    """直播列表查询测试"""

    def setUp(self):
        cache.clear()
        Livestream.objects.create(
            date="2025-01-15",
            title="测试直播1",
            cover_url="http://example.com/cover1.jpg",
        )
        Livestream.objects.create(
            date="2025-01-20",
            title="测试直播2",
            cover_url="http://example.com/cover2.jpg",
        )

    def test_list_mode_no_songrecord_query(self):
        """列表模式不应触发 SongRecord 相关查询，总查询数应保持在可接受范围内"""
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get('/api/livestreams/?year=2025&month=1&include_details=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data), 2)
        self.assertLessEqual(len(captured), 2)

    def test_list_mode_returns_cover_url(self):
        """列表模式应返回 coverUrl"""
        response = self.client.get('/api/livestreams/?year=2025&month=1&include_details=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        for item in data:
            self.assertIn("coverUrl", item)
            self.assertTrue(item["coverUrl"])

    def test_detail_mode_still_has_song_cuts(self):
        """详情模式应正常返回 songCuts 等详细信息"""
        song = Song.objects.create(song_name="测试歌曲", singer="测试歌手")
        SongRecord.objects.create(song=song, performed_at="2025-01-15")
        target = Livestream.objects.filter(date="2025-01-15").first()
        response = self.client.get(f'/api/livestreams/{target.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("songCuts", data)

    def test_support_multiple_sessions_same_day(self):
        """同一天应支持多场直播记录"""
        Livestream.objects.create(
            date="2025-01-15",
            title="测试直播1-加场",
            cover_url="http://example.com/cover3.jpg",
        )
        response = self.client.get('/api/livestreams/?year=2025&month=1&include_details=false')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        same_day = [item for item in data if item["date"] == "2025-01-15"]
        self.assertEqual(len(same_day), 2)

    def test_detail_mode_returns_same_day_recordings(self):
        """详情模式应聚合同一天的多条录像记录。"""
        target = Livestream.objects.filter(date="2025-01-15").first()
        target.replay_url = "https://www.bilibili.com/video/BV1TestReplay/?p=1"
        target.save(update_fields=["replay_url"])
        Livestream.objects.create(
            date="2025-01-15",
            title="测试直播1-P2",
            replay_url="https://www.bilibili.com/video/BV1TestReplay/?p=2",
            cover_url="http://example.com/cover4.jpg",
        )

        response = self.client.get(f'/api/livestreams/{target.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("recordings", data)
        self.assertEqual(len(data["recordings"]), 2)
        self.assertEqual(data["recordings"][1]["url"], "https://www.bilibili.com/video/BV1TestReplay/?p=2")
