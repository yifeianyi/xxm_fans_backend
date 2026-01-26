from django.db import models
from django.core.files.storage import default_storage
import os


class Gallery(models.Model):
    """图集模型 - 支持多级分类"""

    id = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name='图集ID'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='标题'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )
    cover_url = models.CharField(
        max_length=500,
        verbose_name='封面图片URL'
    )

    # 层级关系
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父图集'
    )
    level = models.IntegerField(
        default=0,
        verbose_name='层级'
    )

    # 图片信息
    image_count = models.IntegerField(
        default=0,
        verbose_name='图片数量'
    )
    folder_path = models.CharField(
        max_length=500,
        verbose_name='文件夹路径'
    )

    # 元数据
    tags = models.JSONField(
        default=list,
        verbose_name='标签'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'gallery'
        verbose_name = '图集'
        verbose_name_plural = '图集'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title

    def is_leaf(self):
        """判断是否为叶子节点（无子图集）"""
        return not self.children.exists()

    def get_breadcrumbs(self):
        """获取面包屑路径"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'title': current.title
            })
            current = current.parent
        return breadcrumbs

    def get_images(self):
        """获取图集下的所有图片"""
        folder_path = self.folder_path.lstrip('/')

        if not folder_path or not default_storage.exists(folder_path):
            return []

        try:
            files = default_storage.listdir(folder_path)[1] if hasattr(default_storage, 'listdir') else []
            image_files = sorted([
                f for f in files
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4'))
                and f != 'cover.jpg'
            ])

            return [{
                'filename': f,
                'url': f"{self.folder_path}{f}",
                'title': f"{self.title} - {idx + 1}"
            } for idx, f in enumerate(image_files)]
        except Exception:
            return []

    def add_image(self, image_file, filename=None):
        """添加图片到图集"""
        if not filename:
            # 自动生成文件名
            existing_images = self.get_images()
            next_num = len(existing_images) + 1
            ext = os.path.splitext(image_file.name)[1].lower()
            filename = f"{str(next_num).zfill(3)}{ext}"

        folder_path = self.folder_path.lstrip('/')

        # 确保文件夹存在
        if not default_storage.exists(folder_path):
            default_storage.makedirs(folder_path)

        # 保存图片
        save_path = os.path.join(folder_path, filename)
        default_storage.save(save_path, image_file)

        # 更新图片数量
        self.refresh_image_count()

        return filename

    def delete_image(self, filename):
        """删除图集中的图片"""
        folder_path = self.folder_path.lstrip('/')
        file_path = os.path.join(folder_path, filename)

        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            self.refresh_image_count()
            return True

        return False

    def update_cover(self, cover_file):
        """更新封面图片"""
        folder_path = self.folder_path.lstrip('/')

        # 确保文件夹存在
        if not default_storage.exists(folder_path):
            default_storage.makedirs(folder_path)

        # 保存封面
        cover_path = os.path.join(folder_path, 'cover.jpg')
        default_storage.save(cover_path, cover_file)

        # 更新封面 URL
        self.cover_url = f"{self.folder_path}cover.jpg"
        self.save()

    def refresh_image_count(self):
        """刷新图片数量"""
        if self.is_leaf():
            # 叶子节点：统计当前目录的图片数量
            images = self.get_images()
            self.image_count = len(images)
        else:
            # 父图集：递归统计所有子图集的图片总数
            total_count = 0
            for child in self.children.all():
                child.refresh_image_count()
                total_count += child.image_count
            self.image_count = total_count
        self.save()

    def get_all_children_images(self):
        """获取父图集下所有子图集的图片，按子图集分组返回"""
        if self.is_leaf():
            return []

        result = []
        for child in self.children.all():
            child_images = child.get_images()
            if child_images:
                result.append({
                    'gallery': {
                        'id': child.id,
                        'title': child.title,
                        'description': child.description,
                        'cover_url': child.cover_url,
                        'image_count': child.image_count,
                        'folder_path': child.folder_path,
                        'tags': child.tags,
                    },
                    'images': child_images
                })
        return result