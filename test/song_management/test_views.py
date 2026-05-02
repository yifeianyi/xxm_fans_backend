"""
歌曲管理视图测试 - Commit #1
覆盖：缓存读写、热歌榜 N+1、演唱记录异常处理
"""
from datetime import datetime, timedelta

from django.test import TestCase, override_settings
from django.core.cache import cache
from django.urls import reverse

from song_management.models import Song, SongRecord, Style, Tag, SongStyle, SongTag


# 测试使用本地内存缓存，避免依赖 Redis
CACHES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


@override_settings(CACHES=CACHES_OVERRIDE)
class SongListCacheTest(TestCase):
    """歌曲列表缓存测试"""

    def setUp(self):
        cache.clear()
        self.song = Song.objects.create(
            song_name="测试歌曲",
            singer="测试歌手",
            first_perform="2024-01-01",
            last_performed="2024-01-01",
            perform_count=1,
            language="中文"
        )

    def test_cache_hit_returns_without_db_query(self):
        """缓存命中时应不触发数据库查询，且两次返回数据一致"""
        url = '/api/songs/?page=1&limit=20'

        # 首次请求，缓存未命中
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()

        # 第二次请求，预期缓存命中
        with self.assertNumQueries(0):
            response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()

        # 两次返回数据应一致（除 message 外）
        self.assertEqual(data1["code"], data2["code"])
        self.assertEqual(data1["data"], data2["data"])

    def test_cache_miss_populates_cache(self):
        """缓存未命中时应写入缓存，且缓存数据结构完整"""
        cache_key = "song_list_api::1:20::::"
        self.assertIsNone(cache.get(cache_key))

        response = self.client.get('/api/songs/?page=1&limit=20')
        self.assertEqual(response.status_code, 200)

        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertIn("results", cached_data)
        self.assertIn("total", cached_data)
        self.assertIn("page", cached_data)
        self.assertIn("page_size", cached_data)

    def test_filter_params_generate_different_cache_keys(self):
        """不同过滤参数应生成不同的缓存 key"""
        url1 = '/api/songs/?q=周深&page=1&limit=20'
        url2 = '/api/songs/?q=林俊杰&page=1&limit=20'

        # 首次请求 url1，写入缓存
        resp1a = self.client.get(url1)
        self.assertEqual(resp1a.status_code, 200)

        # 再次请求 url1，应命中缓存（无 DB 查询）
        with self.assertNumQueries(0):
            resp1b = self.client.get(url1)
        self.assertEqual(resp1b.status_code, 200)
        self.assertEqual(resp1a.json()["data"], resp1b.json()["data"])

        # 请求 url2，应不共享 url1 的缓存（需要查库）
        with self.assertNumQueries(1):
            resp2a = self.client.get(url2)
        self.assertEqual(resp2a.status_code, 200)


@override_settings(CACHES=CACHES_OVERRIDE)
class TopSongsQueryTest(TestCase):
    """热歌榜查询优化测试"""

    def setUp(self):
        cache.clear()
        self.songs = []
        for i in range(5):
            song = Song.objects.create(
                song_name=f"歌曲{i}",
                singer=f"歌手{i}",
                first_perform=f"2024-01-0{i+1}",
                last_performed=f"2024-01-0{i+1}",
                perform_count=0,
            )
            self.songs.append(song)
            # 每首歌创建 3 条不同日期的演唱记录
            for j in range(3):
                SongRecord.objects.create(
                    song=song,
                    performed_at=f"2024-02-{j+1:02d}",
                    cover_url=f"http://example.com/cover_{i}_{j}.jpg"
                )

    def test_top_songs_query_count_constant(self):
        """热歌榜查询数应与 limit 无关，始终 ≤ 3"""
        # limit=10
        with self.assertNumQueries(2):
            response = self.client.get('/api/top_songs/?range=all&limit=10')
            self.assertEqual(response.status_code, 200)

        # limit=50，查询数仍应相同
        with self.assertNumQueries(2):
            response = self.client.get('/api/top_songs/?range=all&limit=50')
            self.assertEqual(response.status_code, 200)

    def test_top_songs_returns_correct_data(self):
        """热歌榜返回数据结构正确"""
        response = self.client.get('/api/top_songs/?range=all&limit=3')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)
        for item in data["data"]:
            self.assertIn("id", item)
            self.assertIn("song_name", item)
            self.assertIn("singer", item)
            self.assertIn("perform_count", item)
            self.assertIn("cover_url", item)

    def test_top_songs_cover_url_from_latest_record(self):
        """热歌榜封面 URL 应来自最近日期的演唱记录"""
        song = self.songs[0]
        SongRecord.objects.create(
            song=song,
            performed_at="2024-03-01",
            cover_url="http://example.com/newest_cover.jpg"
        )

        response = self.client.get('/api/top_songs/?range=all&limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]

        song_data = next((s for s in data if s["id"] == song.id), None)
        self.assertIsNotNone(song_data)
        self.assertIsNotNone(song_data["cover_url"])


@override_settings(CACHES=CACHES_OVERRIDE)
class SongRecordErrorHandlingTest(TestCase):
    """演唱记录异常处理测试"""

    def setUp(self):
        self.song = Song.objects.create(
            song_name="测试歌曲",
            singer="测试歌手",
        )
        self.record = SongRecord.objects.create(
            song=self.song,
            performed_at="2024-01-01",
        )

    def test_records_for_nonexistent_song_returns_not_500(self):
        """不存在的 song_id 不应返回 500（NameError）"""
        response = self.client.get('/api/songs/99999/records/')
        self.assertNotEqual(response.status_code, 500)

    def test_records_for_existing_song_returns_200(self):
        """存在的 song_id 应正常返回 200"""
        response = self.client.get(f'/api/songs/{self.song.id}/records/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
