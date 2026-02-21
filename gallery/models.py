import os
import logging
from collections import deque
from django.db import models, transaction
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


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
        blank=True,
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
        editable=False,
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

    # 支持的图片和视频格式
    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4')
    COVER_FILENAME = 'cover.jpg'

    class Meta:
        db_table = 'gallery'
        verbose_name = '图集'
        verbose_name_plural = '图集'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title

    def clean(self):
        """模型级别验证"""
        super().clean()
        
        # 防止循环引用
        if self.parent:
            parent = self.parent
            visited = {self.id}  # 包含自身，防止将自己设为父节点
            while parent:
                if parent.id in visited:
                    raise ValidationError('不能形成循环引用：父图集不能是当前图集的子节点')
                visited.add(parent.id)
                parent = parent.parent

    def save(self, *args, **kwargs):
        """保存时自动计算层级"""
        # 自动计算 level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        
        self.clean()
        super().save(*args, **kwargs)

    def get_cover_thumbnail_url(self):
        """获取封面缩略图 URL"""
        if not self.cover_url:
            return self.cover_url
        
        from .utils import ThumbnailGenerator
        return ThumbnailGenerator.get_thumbnail_url(self.cover_url)

    def is_leaf(self):
        """判断是否为叶子节点（无子图集）"""
        return not self.children.exists()

    def get_breadcrumbs(self):
        """获取面包屑路径（迭代实现，支持任意深度）"""
        breadcrumbs = []
        current = self
        
        # 防止无限循环（理论上不会发生，但做安全检查）
        visited = set()
        while current and current.id not in visited:
            visited.add(current.id)
            breadcrumbs.append({
                'id': current.id,
                'title': current.title
            })
            current = current.parent
        
        # 反转得到从根到当前的顺序
        breadcrumbs.reverse()
        return breadcrumbs

    def _get_media_folder_path(self):
        """将文件夹路径转换为媒体 URL 路径"""
        if not self.folder_path:
            return ''
        return self.folder_path.replace('/gallery/', '/media/gallery/', 1)

    def get_images(self):
        """获取图集下的所有图片"""
        folder_path = self.folder_path.lstrip('/')

        if not folder_path or not default_storage.exists(folder_path):
            return []

        try:
            # 尝试使用 listdir，如果存储后端不支持则返回空列表
            try:
                dirs, files = default_storage.listdir(folder_path)
            except (NotImplementedError, OSError):
                return []

            image_files = sorted([
                f for f in files
                if f.lower().endswith(self.SUPPORTED_EXTENSIONS)
                and f != self.COVER_FILENAME
            ])

            from .utils import ThumbnailGenerator

            # 使用统一方法转换路径
            media_folder_path = self._get_media_folder_path()

            return [{
                'filename': f,
                'url': f"{media_folder_path}{f}",
                'thumbnail_url': f"/api/gallery/thumbnail/?path={self.folder_path}{f}",
                'title': f"{self.title} - {idx + 1}",
                'is_gif': f.lower().endswith('.gif'),
                'is_video': f.lower().endswith('.mp4'),
            } for idx, f in enumerate(image_files)]
        except Exception as e:
            logger.error(f"获取图集 {self.id} 图片失败: {e}")
            return []

    def _get_next_available_number(self, folder_path):
        """获取下一个可用的文件编号（考虑并发安全）"""
        try:
            _, files = default_storage.listdir(folder_path)
            existing_numbers = set()
            
            for f in files:
                if f.lower().endswith(self.SUPPORTED_EXTENSIONS) and f != self.COVER_FILENAME:
                    # 提取数字前缀（如 "001.jpg" -> 1）
                    name_without_ext = os.path.splitext(f)[0]
                    if name_without_ext.isdigit():
                        existing_numbers.add(int(name_without_ext))
            
            # 找到第一个未被使用的编号
            next_num = 1
            while next_num in existing_numbers:
                next_num += 1
            
            return next_num
        except (OSError, NotImplementedError):
            return 1

    def add_image(self, image_file, filename=None):
        """添加图片到图集（并发安全）"""
        folder_path = self.folder_path.lstrip('/')

        # 确保文件夹存在
        if not default_storage.exists(folder_path):
            default_storage.makedirs(folder_path)

        if not filename:
            # 使用数据库行锁保证并发安全
            with transaction.atomic():
                # 锁定当前图集记录，防止并发修改
                Gallery.objects.select_for_update().get(pk=self.pk)
                
                # 在锁内获取下一个可用编号
                next_num = self._get_next_available_number(folder_path)
                ext = os.path.splitext(image_file.name)[1].lower()
                filename = f"{str(next_num).zfill(3)}{ext}"

        save_path = os.path.join(folder_path, filename)

        # 最终检查：如果文件已存在（极端并发情况），寻找下一个可用编号
        final_filename = filename
        counter = 0
        max_attempts = 100  # 防止无限循环
        
        while default_storage.exists(save_path) and counter < max_attempts:
            counter += 1
            name_without_ext = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            
            # 尝试解析当前编号并递增
            if name_without_ext.isdigit():
                next_num = int(name_without_ext) + counter
            else:
                next_num = counter
                
            final_filename = f"{str(next_num).zfill(3)}{ext}"
            save_path = os.path.join(folder_path, final_filename)

        if counter >= max_attempts:
            raise RuntimeError(f"无法为图集 {self.id} 生成唯一文件名，请检查文件系统")

        # 保存图片
        default_storage.save(save_path, image_file)

        # 更新图片数量
        self.refresh_image_count()

        return final_filename

    def delete_image(self, filename):
        """删除图集中的图片"""
        if filename == self.COVER_FILENAME:
            logger.warning(f"尝试删除封面图片被阻止: {filename}")
            return False
            
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
        cover_path = os.path.join(folder_path, self.COVER_FILENAME)
        default_storage.save(cover_path, cover_file)

        # 更新封面 URL
        self.cover_url = f"{self.folder_path}{self.COVER_FILENAME}"
        self.save(update_fields=['cover_url', 'updated_at'])

    def refresh_image_count(self):
        """刷新图片数量（迭代实现，支持任意深度）"""
        # 收集所有需要更新的节点（当前节点及其所有后代）
        nodes_to_update = []
        stack = [self]
        
        # DFS 收集所有节点
        while stack:
            node = stack.pop()
            nodes_to_update.append(node)
            # 预取子节点减少查询
            stack.extend(node.children.all())
        
        # 按层级降序排序（叶子节点在前）
        nodes_to_update.sort(key=lambda x: x.level, reverse=True)
        
        # 创建一个字典来缓存每个节点的计数
        count_cache = {}
        
        for node in nodes_to_update:
            if node.is_leaf():
                # 叶子节点：统计当前目录的图片数量
                images = node.get_images()
                count_cache[node.id] = len(images)
                node.image_count = len(images)
                node.save(update_fields=['image_count', 'updated_at'])
            else:
                # 父节点：汇总所有子节点的数量
                total = 0
                for child in node.children.all():
                    total += count_cache.get(child.id, 0)
                count_cache[node.id] = total
                node.image_count = total
                node.save(update_fields=['image_count', 'updated_at'])

    def get_all_children_images(self):
        """获取父图集下所有子图集的图片，按子图集分组返回（迭代实现）"""
        if self.is_leaf():
            return []

        result = []
        # 使用队列进行广度优先遍历
        queue = deque([self])
        
        while queue:
            node = queue.popleft()
            
            # 处理当前节点的直接子节点
            for child in node.children.all():
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
                # 将子节点加入队列，继续处理其后代
                if not child.is_leaf():
                    queue.append(child)
        
        return result

    def get_descendants(self):
        """获取所有后代节点（迭代实现）"""
        descendants = []
        queue = deque([self])
        
        while queue:
            node = queue.popleft()
            if node != self:  # 不包含自身
                descendants.append(node)
            queue.extend(node.children.all())
        
        return descendants

    def get_ancestors(self):
        """获取所有祖先节点（迭代实现）"""
        ancestors = []
        current = self.parent
        
        # 防止循环引用导致的无限循环
        visited = set()
        while current and current.id not in visited:
            visited.add(current.id)
            ancestors.append(current)
            current = current.parent
        
        return ancestors
