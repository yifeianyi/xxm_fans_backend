"""
Gallery 模块单元测试
"""
import os
import tempfile
import shutil
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Gallery


User = get_user_model()


class GalleryModelTests(TestCase):
    """图集模型测试"""

    def setUp(self):
        """测试准备"""
        self.parent_gallery = Gallery.objects.create(
            id='test-parent',
            title='测试父图集',
            description='这是一个测试父图集',
            cover_url='/media/gallery/test-parent/cover.jpg',
            folder_path='/gallery/test-parent/',
            level=0
        )
        self.child_gallery = Gallery.objects.create(
            id='test-parent-child',
            title='测试子图集',
            description='这是一个测试子图集',
            cover_url='/media/gallery/test-parent/child/cover.jpg',
            folder_path='/gallery/test-parent/child/',
            parent=self.parent_gallery,
            level=1
        )

    def test_gallery_creation(self):
        """测试图集创建"""
        self.assertEqual(self.parent_gallery.id, 'test-parent')
        self.assertEqual(self.parent_gallery.title, '测试父图集')
        self.assertEqual(self.parent_gallery.level, 0)
        self.assertTrue(self.parent_gallery.is_active)

    def test_gallery_str(self):
        """测试图集字符串表示"""
        self.assertEqual(str(self.parent_gallery), '测试父图集')

    def test_is_leaf(self):
        """测试叶子节点判断"""
        # 父图集有子图集，不是叶子节点
        self.parent_gallery.refresh_from_db()
        self.assertFalse(self.parent_gallery.is_leaf())
        
        # 子图集没有子图集，是叶子节点
        self.assertTrue(self.child_gallery.is_leaf())

    def test_get_breadcrumbs(self):
        """测试面包屑路径"""
        breadcrumbs = self.child_gallery.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 2)
        self.assertEqual(breadcrumbs[0]['id'], 'test-parent')
        self.assertEqual(breadcrumbs[0]['title'], '测试父图集')
        self.assertEqual(breadcrumbs[1]['id'], 'test-parent-child')
        self.assertEqual(breadcrumbs[1]['title'], '测试子图集')

    def test_get_breadcrumbs_root(self):
        """测试根图集面包屑路径"""
        breadcrumbs = self.parent_gallery.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 1)
        self.assertEqual(breadcrumbs[0]['id'], 'test-parent')

    def test_parent_child_relationship(self):
        """测试父子关系"""
        self.parent_gallery.refresh_from_db()
        children = self.parent_gallery.children.all()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first().id, 'test-parent-child')

    def test_gallery_ordering(self):
        """测试图集排序"""
        gallery2 = Gallery.objects.create(
            id='test-parent-2',
            title='测试父图集2',
            folder_path='/gallery/test-parent-2/',
            sort_order=1
        )
        gallery1 = Gallery.objects.create(
            id='test-parent-1',
            title='测试父图集1',
            folder_path='/gallery/test-parent-1/',
            sort_order=0
        )
        galleries = list(Gallery.objects.filter(id__in=['test-parent', 'test-parent-1', 'test-parent-2']))
        ids = [g.id for g in galleries]
        # 按 sort_order 和 id 排序
        self.assertEqual(ids, ['test-parent', 'test-parent-1', 'test-parent-2'])


class GalleryViewTests(APITestCase):
    """图集 API 视图测试"""

    def setUp(self):
        """测试准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
        # 创建测试图集结构
        self.root_gallery = Gallery.objects.create(
            id='root-gallery',
            title='根图集',
            folder_path='/gallery/root/',
            level=0
        )
        self.child_gallery = Gallery.objects.create(
            id='root-child',
            title='子图集',
            folder_path='/gallery/root/child/',
            parent=self.root_gallery,
            level=1
        )
        self.grandchild_gallery = Gallery.objects.create(
            id='root-child-grandchild',
            title='孙图集',
            folder_path='/gallery/root/child/grandchild/',
            parent=self.child_gallery,
            level=2
        )

    def test_gallery_tree(self):
        """测试获取图集树"""
        url = reverse('gallery:tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        
        # 验证数据结构
        data = response.data['data']
        self.assertIsInstance(data, list)
        
        # 找到根图集
        root = next((g for g in data if g['id'] == 'root-gallery'), None)
        self.assertIsNotNone(root)
        self.assertEqual(root['title'], '根图集')
        self.assertIn('children', root)
        
        # 验证子图集
        child = next((g for g in root['children'] if g['id'] == 'root-child'), None)
        self.assertIsNotNone(child)
        self.assertEqual(child['title'], '子图集')

    def test_gallery_detail(self):
        """测试获取图集详情"""
        url = reverse('gallery:detail', args=['root-gallery'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        
        data = response.data['data']
        self.assertEqual(data['id'], 'root-gallery')
        self.assertEqual(data['title'], '根图集')
        self.assertIn('breadcrumbs', data)
        self.assertIn('is_leaf', data)
        self.assertIn('children', data)

    def test_gallery_detail_not_found(self):
        """测试获取不存在的图集"""
        url = reverse('gallery:detail', args=['non-existent'])
        response = self.client.get(url)
        
        # 不存在的图集返回 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gallery_detail_inactive(self):
        """测试获取禁用的图集"""
        self.root_gallery.is_active = False
        self.root_gallery.save()
        
        url = reverse('gallery:detail', args=['root-gallery'])
        response = self.client.get(url)
        
        # 禁用图集返回 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_gallery_images_empty(self):
        """测试获取空图集图片列表"""
        url = reverse('gallery:images', args=['root-gallery'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['images'], [])
        self.assertEqual(response.data['data']['total'], 0)

    def test_gallery_children_images_leaf(self):
        """测试获取叶子图集的子图集图片"""
        url = reverse('gallery:children_images', args=['root-child-grandchild'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('gallery', response.data['data'])
        self.assertIn('images', response.data['data'])

    def test_thumbnail_missing_path(self):
        """测试缩略图接口缺少路径参数"""
        url = reverse('gallery:thumbnail')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GalleryModelMethodsTests(TestCase):
    """图集模型方法测试"""

    def setUp(self):
        """测试准备"""
        self.gallery = Gallery.objects.create(
            id='test-gallery',
            title='测试图集',
            folder_path='/gallery/test/',
            level=0
        )

    def test_refresh_image_count_leaf(self):
        """测试刷新叶子图集图片数量"""
        # 叶子节点没有实际图片文件，数量为 0
        self.gallery.refresh_image_count()
        self.gallery.refresh_from_db()
        self.assertEqual(self.gallery.image_count, 0)

    def test_refresh_image_count_parent(self):
        """测试刷新父图集图片数量"""
        parent = Gallery.objects.create(
            id='parent-gallery',
            title='父图集',
            folder_path='/gallery/parent/',
            level=0
        )
        child = Gallery.objects.create(
            id='parent-child',
            title='子图集',
            folder_path='/gallery/parent/child/',
            parent=parent,
            level=1,
            image_count=5
        )
        
        parent.refresh_image_count()
        # refresh_image_count 会递归刷新子图集并从数据库重新加载
        # 父图集的数量会在方法内部计算并保存
        parent.refresh_from_db()
        # 由于子图集的图片是从文件系统读取的（实际为0），父图集数量应该是0
        # 或者如果我们手动设置了子图集数量，需要重新加载子图集
        child.refresh_from_db()
        self.assertEqual(child.image_count, 0)  # 叶子节点从文件系统读取为0
        self.assertEqual(parent.image_count, 0)  # 父节点汇总也是0


class GalleryAdminTests(TestCase):
    """图集后台管理测试"""

    def setUp(self):
        """测试准备"""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@test.com'
        )
        self.gallery = Gallery.objects.create(
            id='admin-test',
            title='Admin测试图集',
            folder_path='/gallery/admin-test/',
            level=0
        )

    def test_admin_list_view(self):
        """测试后台列表视图访问"""
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/gallery/gallery/')
        self.assertEqual(response.status_code, 200)

    def test_admin_change_view(self):
        """测试后台编辑视图访问"""
        self.client.force_login(self.admin_user)
        response = self.client.get(f'/admin/gallery/gallery/{self.gallery.id}/change/')
        self.assertEqual(response.status_code, 200)


class GalleryEdgeCaseTests(TestCase):
    """边界情况测试"""

    def test_gallery_id_special_chars(self):
        """测试特殊字符 ID"""
        gallery = Gallery.objects.create(
            id='test-id_with.special-chars',
            title='特殊ID图集',
            folder_path='/gallery/special/',
        )
        self.assertEqual(gallery.id, 'test-id_with.special-chars')

    def test_gallery_long_title(self):
        """测试超长标题"""
        long_title = '这是一个非常长的标题' * 20
        gallery = Gallery.objects.create(
            id='long-title',
            title=long_title,
            folder_path='/gallery/long/',
        )
        self.assertEqual(gallery.title, long_title)

    def test_gallery_deep_nesting(self):
        """测试深层嵌套"""
        parent = None
        for i in range(5):
            gallery = Gallery.objects.create(
                id=f'nest-level-{i}',
                title=f'嵌套层级 {i}',
                folder_path=f'/gallery/nest/level{i}/',
                parent=parent,
                level=i
            )
            parent = gallery
        
        # 验证最深层的面包屑
        deepest = Gallery.objects.get(id='nest-level-4')
        breadcrumbs = deepest.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 5)

    def test_get_images_invalid_folder(self):
        """测试获取无效文件夹的图片"""
        gallery = Gallery.objects.create(
            id='invalid-folder',
            title='无效文件夹',
            folder_path='/non/existent/path/',
        )
        images = gallery.get_images()
        self.assertEqual(images, [])

    def test_tags_default_empty_list(self):
        """测试标签默认值为空列表"""
        gallery = Gallery.objects.create(
            id='tags-test',
            title='标签测试',
            folder_path='/gallery/tags/',
        )
        self.assertEqual(gallery.tags, [])
