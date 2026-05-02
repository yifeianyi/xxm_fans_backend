"""
Site Settings 视图测试 - Commit #4
覆盖：Sitemap 缓存
"""
from django.test import TestCase, override_settings
from django.core.cache import cache

from gallery.models import Gallery


CACHES_OVERRIDE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sitemap-test',
    }
}


@override_settings(CACHES=CACHES_OVERRIDE)
class SitemapCacheTest(TestCase):
    """Sitemap 缓存测试"""

    def setUp(self):
        cache.clear()

    def test_sitemap_returns_xml_content(self):
        """Sitemap 应返回 XML 格式内容"""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response.get('Content-Type', ''))
        content = response.content.decode('utf-8')
        self.assertIn("<urlset", content)
        self.assertIn("<url>", content)

    def test_sitemap_includes_gallery_urls(self):
        """Sitemap 应包含图集 URL"""
        Gallery.objects.create(
            id="test-gallery",
            title="测试图集",
            folder_path="/gallery/test/",
            is_active=True,
        )
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("/albums/", content)
