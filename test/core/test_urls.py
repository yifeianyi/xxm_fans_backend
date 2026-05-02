"""
URL 兼容性测试 - Commit #6
覆盖：kebab-case 别名与旧路径兼容
"""
from django.test import TestCase


class APIURLCompatibilityTest(TestCase):
    """API URL 兼容性测试"""

    def test_old_top_songs_url_still_works(self):
        """旧路径 /api/top_songs/ 应正常工作"""
        response = self.client.get('/api/top_songs/')
        self.assertEqual(response.status_code, 200)

    def test_new_kebab_top_songs_url_works(self):
        """新路径 /api/top-songs/ 应正常工作"""
        response = self.client.get('/api/top-songs/')
        self.assertEqual(response.status_code, 200)

    def test_old_fans_diy_url_still_works(self):
        """旧路径 /api/fansDIY/collections/ 应正常工作"""
        response = self.client.get('/api/fansDIY/collections/')
        self.assertEqual(response.status_code, 200)

    def test_new_kebab_fans_diy_url_works(self):
        """新路径 /api/fans-diy/collections/ 应正常工作"""
        response = self.client.get('/api/fans-diy/collections/')
        self.assertEqual(response.status_code, 200)
