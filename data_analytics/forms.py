"""
表单定义
"""
from django import forms
from django.conf import settings
import os

from .models import WorkStatic
from core.thumbnail_generator import ThumbnailGenerator


class BVImportForm(forms.Form):
    """BV号导入表单"""
    bvid = forms.CharField(
        label="BV号",
        max_length=20,
        required=True,
        help_text="请输入B站视频的BV号，例如：BV1xx411c7mD"
    )


class WorkStaticForm(forms.ModelForm):
    """作品静态信息表单 - 支持封面上传"""
    replace_cover = forms.ImageField(
        label="更换封面图（仅内容覆盖，路径和文件名不变）",
        required=False,
        help_text="上传新封面后，会覆盖原文件内容，但保持文件名不变"
    )

    class Meta:
        model = WorkStatic
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置 help_text，显示当前封面信息
        if self.instance and self.instance.cover_url:
            cover_url = self.instance.cover_url
            # 提取文件名
            file_name = cover_url.rstrip('/').split('/')[-1]

            # 判断是本地路径还是外部 URL
            if cover_url.startswith('http'):
                cover_info = f"当前封面: {file_name} (外部链接)"
            else:
                cover_info = f"当前封面: {file_name}"

            self.fields['replace_cover'].help_text = f"{cover_info}。上传新封面后，会覆盖原文件内容，但保持文件名不变"
        else:
            self.fields['replace_cover'].help_text = "当前无封面。上传新封面后会保存到 data_analytics/covers/ 目录"

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cover = self.cleaned_data.get('replace_cover')

        if new_cover and instance.cover_url:
            # 处理封面上传
            # 如果 cover_url 是本地路径，直接覆盖
            if instance.cover_url.startswith('/'):
                # 绝对路径或以 / 开头的相对路径
                rel_path = instance.cover_url.lstrip('/')
            else:
                rel_path = instance.cover_url

            # 确定保存路径
            if rel_path.startswith('data_analytics/covers/'):
                # 已经是 data_analytics 路径
                cover_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            elif rel_path.startswith('covers/'):
                # 通用 covers 路径
                cover_path = os.path.join(settings.MEDIA_ROOT, 'data_analytics', rel_path)
            else:
                # 其他路径，保存到 data_analytics/covers 目录
                cover_dir = os.path.join(settings.MEDIA_ROOT, 'data_analytics', 'covers')
                os.makedirs(cover_dir, exist_ok=True)
                # 使用 work_id 作为文件名
                file_ext = os.path.splitext(new_cover.name)[1] or '.jpg'
                cover_path = os.path.join(cover_dir, f"{instance.work_id}{file_ext}")
                # 更新 cover_url
                instance.cover_url = f"/media/data_analytics/covers/{instance.work_id}{file_ext}"

            # 确保目录存在
            cover_dir = os.path.dirname(cover_path)
            os.makedirs(cover_dir, exist_ok=True)

            # 保存文件
            with open(cover_path, 'wb+') as f:
                for chunk in new_cover.chunks():
                    f.write(chunk)

            # 自动生成缩略图
            try:
                if instance.cover_url.startswith('/'):
                    rel_path = instance.cover_url.lstrip('/')
                    thumbnail_path = ThumbnailGenerator.generate_thumbnail(rel_path)
                    if thumbnail_path != rel_path:
                        print(f"[WorkStatic] ✅ 缩略图生成成功: {thumbnail_path}")
            except Exception as e:
                print(f"[WorkStatic] ⚠️ 缩略图生成失败: {e}")

        if commit:
            instance.save()
        return instance