from django.db import models


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
