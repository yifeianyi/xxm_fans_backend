"""
Django 信号处理器 - 自动处理缩略图生成和删除
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db.models import ImageField, FileField


@receiver(post_save)
def generate_thumbnail_on_upload(sender, instance, created, **kwargs):
    """
    图片上传时自动生成缩略图

    Args:
        sender: 模型类
        instance: 模型实例
        created: 是否为新创建
        **kwargs: 其他参数
    """
    from .thumbnail_generator import ThumbnailGenerator
    
    # 跳过 settings 模块
    if sender.__module__.startswith('site_settings'):
        return
    
    # 遍历模型的所有 ImageField
    for field in instance._meta.get_fields():
        if isinstance(field, ImageField):
            # 获取图片路径
            image_field = getattr(instance, field.name)
            if image_field and hasattr(image_field, 'name') and image_field.name:
                try:
                    # 生成缩略图
                    ThumbnailGenerator.generate_thumbnail(image_field.name)
                except Exception as e:
                    print(f"自动生成缩略图失败 ({sender.__name__}.{field.name}): {e}")


@receiver(pre_delete)
def delete_thumbnail_on_delete(sender, instance, **kwargs):
    """
    图片删除时自动删除缩略图

    Args:
        sender: 模型类
        instance: 模型实例
        **kwargs: 其他参数
    """
    from .thumbnail_generator import ThumbnailGenerator
    
    # 跳过 settings 模块
    if sender.__module__.startswith('site_settings'):
        return
    
    # 遍历模型的所有 ImageField
    for field in instance._meta.get_fields():
        if isinstance(field, ImageField):
            # 获取图片路径
            image_field = getattr(instance, field.name)
            if image_field and hasattr(image_field, 'name') and image_field.name:
                try:
                    # 删除缩略图
                    ThumbnailGenerator.delete_thumbnail(image_field.name)
                except Exception as e:
                    print(f"自动删除缩略图失败 ({sender.__name__}.{field.name}): {e}")