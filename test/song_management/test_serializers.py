"""
歌曲管理序列化器测试 - Commit #1
覆盖：SimpleSongSerializer 引入、嵌套字段精简
"""
from django.test import TestCase

from song_management.models import Song, SongRecord, Style, Tag, SongStyle, SongTag
from song_management.api.serializers import (
    SongSerializer,
    SimpleSongSerializer,
    SongRecordSerializer,
)


class SongSerializerTest(TestCase):
    """序列化器结构测试"""

    def setUp(self):
        self.song = Song.objects.create(
            song_name="测试歌曲",
            singer="测试歌手",
            first_perform="2024-01-01",
            last_performed="2024-01-01",
            perform_count=5,
            language="中文"
        )
        self.style = Style.objects.create(name="流行")
        self.tag = Tag.objects.create(name="经典")
        SongStyle.objects.create(song=self.song, style=self.style)
        SongTag.objects.create(song=self.song, tag=self.tag)

        self.record = SongRecord.objects.create(
            song=self.song,
            performed_at="2024-01-01",
            cover_url="http://example.com/cover.jpg"
        )

    def test_simple_song_serializer_has_only_three_fields(self):
        """SimpleSongSerializer 仅包含 id, song_name, singer"""
        serializer = SimpleSongSerializer(instance=self.song)
        data = serializer.data
        self.assertEqual(set(data.keys()), {"id", "song_name", "singer"})

    def test_song_serializer_remains_complete(self):
        """SongSerializer 仍包含完整字段"""
        serializer = SongSerializer(instance=self.song)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("song_name", data)
        self.assertIn("singer", data)
        self.assertIn("styles", data)
        self.assertIn("tags", data)
        self.assertIn("first_perform", data)
        self.assertIn("last_performed", data)
        self.assertIn("perform_count", data)
        self.assertIn("language", data)

    def test_record_serializer_uses_lightweight_song(self):
        """SongRecordSerializer 中的 song 字段应为精简结构"""
        serializer = SongRecordSerializer(instance=self.record)
        data = serializer.data
        song_data = data.get("song")
        self.assertIsNotNone(song_data)
        self.assertEqual(set(song_data.keys()), {"id", "song_name", "singer"})
        self.assertNotIn("styles", song_data)
        self.assertNotIn("tags", song_data)
        self.assertNotIn("first_perform", song_data)

    def test_api_response_matches_serializer(self):
        """通过 API 请求验证 records 接口中 song 字段为精简结构"""
        response = self.client.get(f'/api/songs/{self.song.id}/records/')
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        song_data = data["results"][0]["song"]
        self.assertEqual(set(song_data.keys()), {"id", "song_name", "singer"})
