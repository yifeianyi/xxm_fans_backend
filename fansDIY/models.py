from django.db import models

# Create your models here.

class Collection(models.Model):
    """粉丝二创合集"""
    name = models.CharField(max_length=200, verbose_name="合集名称")
    works_count = models.IntegerField(default=0, verbose_name="作品数量")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    position = models.IntegerField(default=0, verbose_name="位置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "二创合集"
        verbose_name_plural = "二创合集"
        ordering = ['position', 'display_order', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.works_count}个作品)"
    
    def update_works_count(self):
        """更新作品数量"""
        self.works_count = self.works.count()
        self.save(update_fields=['works_count'])


class Work(models.Model):
    """作品记录"""
    collection = models.ForeignKey(
        Collection, 
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