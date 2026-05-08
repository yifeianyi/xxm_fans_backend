from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from song_management.models import Song, SongRecord, SongRecordLike


class ToggleLikeTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            song_name="测试歌曲", singer="测试歌手",
            first_perform="2024-01-01", last_performed="2024-06-01",
            perform_count=10, language="中文"
        )
        self.record = SongRecord.objects.create(
            song=self.song, performed_at="2024-06-01",
            url="https://example.com", notes="测试记录"
        )

    def _like(self, record_id):
        return self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': record_id},
            content_type='application/json'
        )

    def _status(self, ids):
        return self.client.get(
            reverse('song_management:like-status') + f'?ids={",".join(str(i) for i in ids)}'
        )

    def test_like_creates_record(self):
        response = self._like(self.record.id)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 1)

    def test_like_then_unlike(self):
        self._like(self.record.id)
        response = self._like(self.record.id)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['liked'])
        self.assertEqual(data['like_count'], 0)

    def test_like_unlike_relike(self):
        self._like(self.record.id)   # like
        self._like(self.record.id)   # unlike
        response = self._like(self.record.id)   # like again
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 1)

    def test_same_ip_cannot_like_twice(self):
        self._like(self.record.id)
        response = self._like(self.record.id)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(SongRecordLike.objects.filter(song_record_id=self.record.id).count(), 0)

    def test_different_ip_can_like(self):
        self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': self.record.id},
            content_type='application/json',
            REMOTE_ADDR='10.0.0.1'
        )
        response = self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': self.record.id},
            content_type='application/json',
            REMOTE_ADDR='10.0.0.2'
        )
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 2)


class LikeStatusTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            song_name="测试歌曲", singer="测试歌手",
            first_perform="2024-01-01", last_performed="2024-06-01",
            perform_count=10, language="中文"
        )
        self.r1 = SongRecord.objects.create(song=self.song, performed_at="2024-01-01")
        self.r2 = SongRecord.objects.create(song=self.song, performed_at="2024-02-01")
        self.r3 = SongRecord.objects.create(song=self.song, performed_at="2024-03-01")

    def _like_custom(self, record_id, ip=None):
        kwargs = {
            'data': {'song_record_id': record_id},
            'content_type': 'application/json'
        }
        if ip:
            kwargs['REMOTE_ADDR'] = ip
        return self.client.post(reverse('song_management:toggle-like'), **kwargs)

    def test_status_with_no_likes(self):
        response = self.client.get(
            reverse('song_management:like-status') + f'?ids={self.r1.id},{self.r2.id}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data'][str(self.r1.id)]['like_count'], 0)
        self.assertFalse(data['data'][str(self.r1.id)]['user_liked'])

    def test_status_shows_user_like(self):
        self._like_custom(self.r1.id, ip='10.0.0.1')
        response = self.client.get(
            reverse('song_management:like-status') + f'?ids={self.r1.id},{self.r2.id}',
            REMOTE_ADDR='10.0.0.1'
        )
        data = response.json()
        self.assertTrue(data['data'][str(self.r1.id)]['user_liked'])
        self.assertFalse(data['data'][str(self.r2.id)]['user_liked'])

    def test_status_shows_other_ip_not_liked(self):
        self._like_custom(self.r1.id, ip='10.0.0.1')
        response = self.client.get(
            reverse('song_management:like-status') + f'?ids={self.r1.id}',
            REMOTE_ADDR='10.0.0.2'
        )
        data = response.json()
        self.assertEqual(data['data'][str(self.r1.id)]['like_count'], 1)
        self.assertFalse(data['data'][str(self.r1.id)]['user_liked'])

    def test_status_empty_ids(self):
        response = self.client.get(reverse('song_management:like-status'))
        self.assertEqual(response.status_code, 400)

    def test_status_invalid_ids(self):
        response = self.client.get(reverse('song_management:like-status') + '?ids=abc')
        self.assertEqual(response.status_code, 400)

    def test_status_missing_song_record_id(self):
        response = self.client.post(
            reverse('song_management:toggle-like'),
            data={},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)


class RateLimitTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            song_name="限流测试歌曲", singer="测试歌手",
            first_perform="2024-01-01", last_performed="2024-06-01",
            perform_count=1, language="中文"
        )
        self.record = SongRecord.objects.create(
            song=self.song, performed_at="2024-06-01"
        )

    def _like_with_ip(self, record_id, ip):
        return self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': record_id},
            content_type='application/json',
            REMOTE_ADDR=ip
        )

    def test_rate_limit_100_per_hour(self):
        for i in range(100):
            self._like_with_ip(self.record.id, f'10.0.{i // 256}.{i % 256}')

        response = self._like_with_ip(self.record.id, '10.255.255.255')
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('点赞过多', data['error'])
        self.assertEqual(data['like_count'], 100)

    def test_rate_limit_exact_boundary(self):
        for i in range(99):
            self._like_with_ip(self.record.id, f'10.0.{i // 256}.{i % 256}')
        response = self._like_with_ip(self.record.id, '10.0.0.99')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])

    def test_rate_limit_old_likes_not_counted(self):
        old_time = timezone.now() - timedelta(hours=2)
        for i in range(100):
            like = SongRecordLike.objects.create(
                song_record_id=self.record.id,
                ip_address=f'10.0.{i // 256}.{i % 256}'
            )
            SongRecordLike.objects.filter(id=like.id).update(created_at=old_time)

        response = self._like_with_ip(self.record.id, '10.255.255.255')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])


class RecordListViewLikeDataTest(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            song_name="视图测试歌曲", singer="测试歌手",
            first_perform="2024-01-01", last_performed="2024-06-01",
            perform_count=5, language="中文"
        )
        self.r1 = SongRecord.objects.create(song=self.song, performed_at="2024-06-01")
        self.r2 = SongRecord.objects.create(song=self.song, performed_at="2024-05-01")
        self.r3 = SongRecord.objects.create(song=self.song, performed_at="2024-04-01")
        SongRecordLike.objects.create(song_record_id=self.r1.id, ip_address='10.0.0.1')
        SongRecordLike.objects.create(song_record_id=self.r1.id, ip_address='10.0.0.2')
        SongRecordLike.objects.create(song_record_id=self.r2.id, ip_address='10.0.0.1')

    def test_records_include_like_data(self):
        response = self.client.get(
            reverse('song_management:song-record-list', kwargs={'song_id': self.song.id}),
            REMOTE_ADDR='10.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']['results']
        records_by_id = {r['id']: r for r in results}
        self.assertEqual(records_by_id[self.r1.id]['like_count'], 2)
        self.assertTrue(records_by_id[self.r1.id]['user_liked'])
        self.assertEqual(records_by_id[self.r2.id]['like_count'], 1)
        self.assertTrue(records_by_id[self.r2.id]['user_liked'])
        self.assertEqual(records_by_id[self.r3.id]['like_count'], 0)
        self.assertFalse(records_by_id[self.r3.id]['user_liked'])

    def test_records_sort_by_likes(self):
        response = self.client.get(
            reverse('song_management:song-record-list', kwargs={'song_id': self.song.id}) + '?sort_by=likes'
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']['results']
        like_counts = [r['like_count'] for r in results]
        self.assertEqual(like_counts, sorted(like_counts, reverse=True))

    def test_records_default_sort_by_time_desc(self):
        response = self.client.get(
            reverse('song_management:song-record-list', kwargs={'song_id': self.song.id})
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()['data']['results']
        dates = [r['performed_at'] for r in results]
        self.assertEqual(dates, sorted(dates, reverse=True))


class ToggleLikeInvalidInputTest(TestCase):
    def test_invalid_json_body(self):
        response = self.client.post(
            reverse('song_management:toggle-like'),
            data='not json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_non_numeric_record_id(self):
        response = self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': 'abc'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_negative_record_id(self):
        response = self.client.post(
            reverse('song_management:toggle-like'),
            data={'song_record_id': -1},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
