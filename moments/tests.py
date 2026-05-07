"""
Moments 模块单元测试
覆盖：模型、API 视图、服务层
"""
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Moment, PlatformCookie, MomentSource
from .services.cookie_service import CookieService
from .services.image_service import ImageService


CACHES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'moments-test',
    }
}


class MomentModelTests(TestCase):
    """动态模型测试"""

    def setUp(self):
        self.moment = Moment.objects.create(
            source='weibo',
            source_id='weibo-test-001',
            content='这是一条测试微博动态内容',
            images=[
                {'original_url': '/media/moments/weibo/weibo_test_001_0.jpg',
                 'thumbnail_url': '/media/moments/thumbnails/weibo/weibo_test_001_0.webp'}
            ],
            publish_time=timezone.make_aware(datetime(2024, 6, 15, 14, 30, 0)),
            like_count=100,
            comment_count=20,
            share_count=5,
            source_url='https://m.weibo.cn/detail/123456',
        )

    def test_moment_creation(self):
        """测试动态创建"""
        self.assertEqual(self.moment.source, 'weibo')
        self.assertEqual(self.moment.source_id, 'weibo-test-001')
        self.assertEqual(self.moment.content, '这是一条测试微博动态内容')
        self.assertEqual(self.moment.like_count, 100)
        self.assertEqual(self.moment.comment_count, 20)
        self.assertEqual(self.moment.share_count, 5)
        self.assertIsNotNone(self.moment.created_at)

    def test_moment_str(self):
        """测试动态字符串表示"""
        expected = '[微博] 这是一条测试微博动态内容'
        self.assertEqual(str(self.moment), expected)

    def test_moment_str_truncated(self):
        """测试长内容字符串截断"""
        long_content = 'A' * 100
        moment = Moment.objects.create(
            source='bilibili',
            source_id='bili-long',
            content=long_content,
            publish_time=timezone.now(),
        )
        self.assertIn('...', str(moment))
        self.assertIn('[B站]', str(moment))

    def test_moment_unique_constraint(self):
        """测试唯一约束 - 同平台同ID不能重复"""
        with self.assertRaises(Exception):
            Moment.objects.create(
                source='weibo',
                source_id='weibo-test-001',
                content='重复内容',
                publish_time=timezone.now(),
            )

    def test_moment_different_source_same_id(self):
        """测试不同平台可以有相同 source_id"""
        moment = Moment.objects.create(
            source='bilibili',
            source_id='weibo-test-001',
            content='B站动态',
            publish_time=timezone.now(),
        )
        self.assertEqual(moment.source, 'bilibili')
        self.assertEqual(moment.source_id, 'weibo-test-001')

    def test_moment_ordering(self):
        """测试按发布时间降序排列"""
        older = Moment.objects.create(
            source='bilibili',
            source_id='bili-old',
            content='旧动态',
            publish_time=timezone.make_aware(datetime(2024, 1, 1)),
        )
        newer = Moment.objects.create(
            source='bilibili',
            source_id='bili-new',
            content='新动态',
            publish_time=timezone.make_aware(datetime(2024, 12, 31)),
        )
        moments = list(Moment.objects.all())
        self.assertEqual(moments[0].source_id, 'bili-new')
        self.assertEqual(moments[1].source_id, 'weibo-test-001')

    def test_moment_source_choices(self):
        """测试来源字段枚举值"""
        moment = Moment.objects.create(
            source='weibo',
            source_id='choice-test',
            content='测试',
            publish_time=timezone.now(),
        )
        self.assertEqual(moment.source, 'weibo')
        moment.source = 'bilibili'
        moment.save()
        moment.refresh_from_db()
        self.assertEqual(moment.source, 'bilibili')

    def test_moment_images_default_empty(self):
        """测试 images 字段默认为空列表"""
        moment = Moment.objects.create(
            source='bilibili',
            source_id='no-images',
            content='无图片动态',
            publish_time=timezone.now(),
        )
        self.assertEqual(moment.images, [])

    def test_moment_default_counts(self):
        """测试互动数据默认值为 0"""
        moment = Moment.objects.create(
            source='weibo',
            source_id='no-stats',
            content='无互动数据',
            publish_time=timezone.now(),
        )
        self.assertEqual(moment.like_count, 0)
        self.assertEqual(moment.comment_count, 0)
        self.assertEqual(moment.share_count, 0)


class PlatformCookieModelTests(TestCase):
    """Cookie 模型测试"""

    def setUp(self):
        self.cookie = PlatformCookie.objects.create(
            platform='weibo',
            cookie_string='SUB=_2A25...; SUBP=_0033...',
        )

    def test_cookie_creation(self):
        """测试 Cookie 创建"""
        self.assertEqual(self.cookie.platform, 'weibo')
        self.assertTrue(self.cookie.is_valid)
        self.assertFalse(self.cookie.expire_notified)

    def test_cookie_unique_platform(self):
        """测试同一平台不能有多个 Cookie"""
        with self.assertRaises(Exception):
            PlatformCookie.objects.create(
                platform='weibo',
                cookie_string='another cookie',
            )

    def test_cookie_bilibili_platform(self):
        """测试 B站平台 Cookie 创建"""
        cookie = PlatformCookie.objects.create(
            platform='bilibili',
            cookie_string='SESSDATA=xxx; bili_jct=yyy',
        )
        self.assertEqual(cookie.platform, 'bilibili')
        self.assertEqual(PlatformCookie.objects.count(), 2)

    def test_cookie_str_valid(self):
        """测试有效 Cookie 字符串表示"""
        self.assertIn('微博', str(self.cookie))
        self.assertIn('有效', str(self.cookie))

    def test_cookie_str_expired(self):
        """测试过期 Cookie 字符串表示"""
        self.cookie.is_valid = False
        self.cookie.save()
        self.assertIn('已过期', str(self.cookie))


@override_settings(CACHES=CACHES_OVERRIDE)
class MomentsAPITests(APITestCase):
    """动态 API 视图测试"""

    def setUp(self):
        self.weibo_moment = Moment.objects.create(
            source='weibo',
            source_id='weibo-api-001',
            content='微博动态内容',
            images=[{'original_url': '/media/moments/weibo/img.jpg',
                     'thumbnail_url': '/media/moments/thumbnails/weibo/img.webp'}],
            publish_time=timezone.make_aware(datetime(2024, 6, 15, 14, 30)),
            like_count=50,
            comment_count=10,
            share_count=3,
            source_url='https://m.weibo.cn/detail/111',
        )
        self.bili_moment = Moment.objects.create(
            source='bilibili',
            source_id='bili-api-001',
            content='B站动态内容',
            images=[],
            publish_time=timezone.make_aware(datetime(2024, 6, 15, 16, 0)),
            like_count=200,
            comment_count=30,
            share_count=15,
            source_url='https://t.bilibili.com/222',
        )

    def test_moments_list_empty_when_no_data(self):
        """测试空数据库返回空列表"""
        url = reverse('moment_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['total'], 2)

    def test_moments_list_correct_structure(self):
        """测试返回数据结构正确"""
        url = reverse('moment_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertIn('results', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('page_size', data)

    def test_moments_list_ordered_by_publish_time(self):
        """测试按发布时间降序返回"""
        url = reverse('moment_list')
        response = self.client.get(url)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['source_id'], 'bili-api-001')

    def test_moments_list_filter_by_weibo(self):
        """测试按微博来源筛选"""
        url = reverse('moment_list') + '?source=weibo'
        response = self.client.get(url)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], 'weibo')

    def test_moments_list_filter_by_bilibili(self):
        """测试按B站来源筛选"""
        url = reverse('moment_list') + '?source=bilibili'
        response = self.client.get(url)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], 'bilibili')

    def test_moments_list_filter_invalid_source(self):
        """测试无效来源筛选返回空"""
        url = reverse('moment_list') + '?source=invalid'
        response = self.client.get(url)
        results = response.data['data']['results']
        self.assertEqual(len(results), 2)

    def test_moments_list_pagination(self):
        """测试分页功能"""
        for i in range(25):
            Moment.objects.create(
                source='weibo',
                source_id=f'pagination-test-{i}',
                content=f'分页测试动态 {i}',
                publish_time=timezone.make_aware(datetime(2024, 1, 1) + timedelta(hours=i)),
            )
        url = reverse('moment_list') + '?page=1&limit=10'
        response = self.client.get(url)
        data = response.data['data']
        self.assertEqual(len(data['results']), 10)
        self.assertEqual(data['total'], 27)

    def test_moment_detail(self):
        """测试获取单条动态详情"""
        url = reverse('moment_detail', args=[self.weibo_moment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['source'], 'weibo')
        self.assertEqual(response.data['data']['source_id'], 'weibo-api-001')
        self.assertEqual(response.data['data']['content'], '微博动态内容')
        self.assertIn('images', response.data['data'])
        self.assertIn('source_url', response.data['data'])

    def test_moment_detail_not_found(self):
        """测试获取不存在的动态"""
        url = reverse('moment_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.data['code'], 404)

    def test_moment_detail_includes_all_fields(self):
        """测试详情包含所有必要字段"""
        url = reverse('moment_detail', args=[self.weibo_moment.id])
        response = self.client.get(url)
        fields = ['id', 'source', 'source_id', 'content', 'images',
                  'publish_time', 'like_count', 'comment_count', 'share_count',
                  'source_url', 'created_at']
        for field in fields:
            self.assertIn(field, response.data['data'])


@override_settings(
    CACHES=CACHES_OVERRIDE,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='test@example.com',
    ADMIN_EMAIL='admin@example.com',
)
class CookieServiceTests(TestCase):
    """Cookie 服务层测试"""

    def setUp(self):
        self.weibo_cookie = PlatformCookie.objects.create(
            platform='weibo',
            cookie_string='weibo_cookie_value',
        )
        self.bili_cookie = PlatformCookie.objects.create(
            platform='bilibili',
            cookie_string='bili_cookie_value',
        )

    def test_get_valid_cookie(self):
        """测试获取有效 Cookie"""
        cookie = CookieService.get_cookie('weibo')
        self.assertEqual(cookie, 'weibo_cookie_value')

    def test_get_expired_cookie_returns_none(self):
        """测试获取已过期 Cookie 返回 None"""
        self.weibo_cookie.is_valid = False
        self.weibo_cookie.save()
        cookie = CookieService.get_cookie('weibo')
        self.assertIsNone(cookie)

    def test_get_nonexistent_platform_returns_none(self):
        """测试获取不存在的平台返回 None"""
        cookie = CookieService.get_cookie('unknown')
        self.assertIsNone(cookie)

    def test_mark_expired_sets_invalid(self):
        """测试标记过期"""
        self.assertTrue(self.weibo_cookie.is_valid)
        CookieService.mark_expired('weibo')
        self.weibo_cookie.refresh_from_db()
        self.assertFalse(self.weibo_cookie.is_valid)
        self.assertIsNotNone(self.weibo_cookie.last_checked)

    def test_mark_expired_sends_email(self):
        """测试过期时发送邮件"""
        self.assertEqual(len(mail.outbox), 0)
        CookieService.mark_expired('weibo')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('微博', mail.outbox[0].subject)
        self.assertIn('admin@example.com', mail.outbox[0].to)

    def test_mark_expired_only_notifies_once(self):
        """测试过期邮件只发送一次"""
        CookieService.mark_expired('weibo')
        self.assertEqual(len(mail.outbox), 1)
        self.weibo_cookie.refresh_from_db()
        self.assertTrue(self.weibo_cookie.expire_notified)

        # 再次标记过期，不应再发邮件
        mail.outbox = []
        CookieService.mark_expired('weibo')
        self.assertEqual(len(mail.outbox), 0)

    def test_mark_expired_nonexistent_platform(self):
        """测试标记不存在的平台不抛异常"""
        CookieService.mark_expired('unknown')
        self.assertEqual(len(mail.outbox), 0)

    def test_mark_valid_resets_state(self):
        """测试标记有效重置过期状态"""
        self.weibo_cookie.is_valid = False
        self.weibo_cookie.expire_notified = True
        self.weibo_cookie.save()

        CookieService.mark_valid('weibo')
        self.weibo_cookie.refresh_from_db()
        self.assertTrue(self.weibo_cookie.is_valid)
        self.assertFalse(self.weibo_cookie.expire_notified)
        self.assertIsNotNone(self.weibo_cookie.last_checked)

    def test_no_email_without_admin_email(self):
        """测试无管理员邮箱时不发送邮件"""
        with override_settings(ADMIN_EMAIL=''):
            self.assertEqual(len(mail.outbox), 0)
            CookieService.mark_expired('bilibili')
            self.assertEqual(len(mail.outbox), 0)


class ImageServiceTests(TestCase):
    """图片服务层测试"""

    @patch('moments.services.image_service.requests.get')
    def test_download_image_success(self, mock_get):
        """测试图片下载成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'fake-image-data']
        mock_get.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()

        result = ImageService.download_and_generate_thumbnails(
            'weibo', 'test-001', ['http://example.com/img.jpg']
        )
        self.assertEqual(len(result), 1)
        self.assertIn('original_url', result[0])
        self.assertIn('thumbnail_url', result[0])
        self.assertIn('/media/moments/weibo/', result[0]['original_url'])

    @patch('moments.services.image_service.requests.get')
    def test_download_image_failure(self, mock_get):
        """测试图片下载失败返回空列表"""
        mock_get.side_effect = Exception('Network error')

        result = ImageService.download_and_generate_thumbnails(
            'weibo', 'test-fail', ['http://example.com/bad.jpg']
        )
        self.assertEqual(len(result), 0)

    @patch('moments.services.image_service.requests.get')
    def test_download_multiple_images(self, mock_get):
        """测试多张图片批量下载"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/png'}
        mock_response.iter_content.return_value = [b'fake-data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = ImageService.download_and_generate_thumbnails(
            'bilibili', 'multi-test',
            ['http://1.jpg', 'http://2.jpg', 'http://3.jpg']
        )
        self.assertEqual(len(result), 3)

    @patch('moments.services.image_service.requests.get')
    def test_empty_url_list(self, mock_get):
        """测试空 URL 列表"""
        result = ImageService.download_and_generate_thumbnails(
            'weibo', 'empty', []
        )
        self.assertEqual(result, [])
        mock_get.assert_not_called()

    @patch('moments.services.image_service.requests.get')
    def test_mixed_urls_with_none(self, mock_get):
        """测试包含 None 的 URL 列表"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = ImageService.download_and_generate_thumbnails(
            'weibo', 'mixed', ['http://valid.jpg', None, '']
        )
        self.assertEqual(len(result), 1)


class MomentsIntegrationTests(TestCase):
    """集成测试 - 完整数据流"""

    def setUp(self):
        self.weibo = Moment.objects.create(
            source='weibo',
            source_id='integration-001',
            content='集成测试微博',
            publish_time=timezone.now(),
        )
        self.bili = Moment.objects.create(
            source='bilibili',
            source_id='integration-002',
            content='集成测试B站',
            publish_time=timezone.now() - timedelta(hours=1),
        )

    def test_full_list_pipeline(self):
        """测试完整列表查询管道"""
        url = reverse('moment_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data['data']
        self.assertEqual(data['total'], 2)

    def test_filter_then_detail_pipeline(self):
        """测试筛选后查看详情管道"""
        url = reverse('moment_list') + '?source=bilibili'
        response = self.client.get(url)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)

        detail_url = reverse('moment_detail', args=[results[0]['id']])
        detail_resp = self.client.get(detail_url)
        self.assertEqual(detail_resp.data['data']['source'], 'bilibili')
