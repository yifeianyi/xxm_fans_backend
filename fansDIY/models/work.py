from django.db import models


class Work(models.Model):
    """作品记录"""
    collection = models.ForeignKey(
        'Collection', 
        on_delete=models.CASCADE, 
        related_name='works',
        verbose_name="所属合集"
    )
    title = models.CharField(max_length=300, verbose_name="作品标题")
    cover_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="封面图片地址")
    view_url = models.URLField(blank=True, null=True, verbose_name="观看链接")
    author = models.CharField(max_length=100, verbose_name="作者")
    notes = models.TextField(blank=True, null=True, verbose_name="备注")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    position = models.IntegerField(default=0, verbose_name="位置")
    
    class Meta:
        verbose_name = "作品记录"
        verbose_name_plural = "作品记录"
        ordering = ['position', 'display_order', '-id']
    
    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_cover_thumbnail_url(self):
        """获取封面缩略图 URL"""
        if not self.cover_url:
            return self.cover_url
        
        from core.thumbnail_generator import ThumbnailGenerator
        return ThumbnailGenerator.get_thumbnail_url(self.cover_url)
    
    def save(self, *args, **kwargs):
        """保存时自动更新合集的作品数量"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.collection.update_works_count()
    
    def delete(self, *args, **kwargs):
        """删除时自动更新合集的作品数量"""
        collection = self.collection
        super().delete(*args, **kwargs)
        collection.update_works_count()
