import os
from django.contrib import admin, messages
from django.urls import reverse
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.utils.safestring import mark_safe
from django.core.files.storage import default_storage

from fansDIY.models import Collection, Work
from fansDIY.forms import BVImportForm
from fansDIY.utils import import_bv_work


class WorkAdminForm(forms.ModelForm):
    """作品管理表单 - 支持本地上传封面"""
    cover_image = forms.ImageField(
        label='上传/替换封面',
        required=False,
        help_text='上传本地图片作为封面。如果是已有记录且已有封面路径，将只替换原文件内容而不改变路径；如果是新记录，将自动创建路径。上传后会自动触发缩略图生成。'
    )

    class Meta:
        model = Work
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 调整字段顺序，让 cover_image 在 cover_url 前面
        self.fields = self._reorder_fields()

    def _reorder_fields(self):
        """重新排序字段，让上传字段在前面"""
        fields = {}
        field_order = [
            'collection', 'title', 'author', 'position', 'display_order',
            'cover_image', 'cover_url', 'view_url', 'notes'
        ]
        for field_name in field_order:
            if field_name in self.fields:
                fields[field_name] = self.fields[field_name]
        # 添加剩余字段
        for field_name, field in self.fields.items():
            if field_name not in fields:
                fields[field_name] = field
        return fields

    def save(self, commit=True):
        instance = super().save(commit=False)
        cover_image = self.cleaned_data.get('cover_image')

        if cover_image:
            if instance.cover_url and instance.pk:
                # 已有封面路径：只替换内容，保持原路径
                self._replace_cover_content(instance.cover_url, cover_image)
            else:
                # 没有封面路径：创建新路径
                saved_path = self._save_new_cover_image(cover_image)
                if saved_path:
                    instance.cover_url = saved_path

        if commit:
            instance.save()
            self.save_m2m()
            # 保存后触发生成缩略图
            self._generate_thumbnail(instance.cover_url)

        return instance

    def _replace_cover_content(self, cover_url, new_image):
        """替换已有封面的内容，保持原路径和文件名"""
        from django.conf import settings

        try:
            # 标准化路径
            rel_path = cover_url.lstrip('/')
            if rel_path.startswith('media/'):
                rel_path = rel_path[len('media/'):]

            # 确定存储路径
            if rel_path.startswith('footprint/'):
                storage_path = rel_path
            else:
                # 如果不是 footprint 路径，生成新的 footprint 路径
                ext = os.path.splitext(new_image.name)[1].lower()
                filename = f"work_{new_image.name[:50]}{ext}"
                storage_path = f'footprint/{filename}'
                # 更新 cover_url
                return f'/media/{storage_path}'

            # 获取完整的文件系统路径
            full_path = os.path.join(settings.MEDIA_ROOT, storage_path)

            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # 直接写入文件（覆盖原文件）
            with open(full_path, 'wb+') as f:
                for chunk in new_image.chunks():
                    f.write(chunk)

            # 删除旧缩略图（如果存在）
            from core.thumbnail_generator import ThumbnailGenerator
            ThumbnailGenerator.delete_thumbnail(storage_path)

        except Exception as e:
            raise forms.ValidationError(f'封面替换失败: {str(e)}')

    def _save_new_cover_image(self, image):
        """保存新封面图片到 media/footprint/ 目录"""
        try:
            # 生成文件名
            ext = os.path.splitext(image.name)[1].lower()
            filename = f"work_{image.name[:50]}{ext}"

            # 保存路径: media/footprint/
            upload_path = f'footprint/{filename}'

            # 保存文件
            saved_path = default_storage.save(upload_path, image)
            return f'/media/{saved_path}'
        except Exception as e:
            raise forms.ValidationError(f'图片保存失败: {str(e)}')

    def _generate_thumbnail(self, cover_url):
        """触发缩略图生成"""
        if not cover_url:
            return

        try:
            from core.thumbnail_generator import ThumbnailGenerator

            # 标准化路径
            rel_path = cover_url.lstrip('/')
            if rel_path.startswith('media/'):
                rel_path = rel_path[len('media/'):]

            # 强制重新生成缩略图（因为原图已更新）
            ThumbnailGenerator.generate_thumbnail(rel_path, force=True)
        except Exception as e:
            # 缩略图生成失败不应影响主流程
            print(f"缩略图生成失败: {cover_url}, 错误: {e}")


class WorkInline(admin.TabularInline):
    """作品内联"""
    model = Work
    extra = 0
    fields = ['title', 'author', 'position', 'display_order', 'cover_url_preview']
    readonly_fields = ['cover_url_preview']
    
    def cover_url_preview(self, obj):
        """封面预览 - 使用缩略图"""
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:40px;max-width:60px;object-fit:cover;" />')
        return "-"
    cover_url_preview.short_description = "封面预览"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """合集管理"""
    list_display = ['name', 'works_count', 'position', 'display_order', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['works_count', 'created_at', 'updated_at']
    inlines = [WorkInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'works_count', 'position', 'display_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """作品管理"""
    form = WorkAdminForm
    list_display = ['title', 'author', 'collection', 'position', 'display_order', 'cover_url_preview', 'view_url_link', 'notes_preview']
    list_filter = ['collection', 'author']
    search_fields = ['title', 'author', 'collection__name', 'notes']
    change_list_template = 'admin/fansDIY/work/change_list.html'
    readonly_fields = ['cover_url_preview_large']

    fieldsets = (
        ('基本信息', {
            'fields': ('collection', 'title', 'author', 'position', 'display_order')
        }),
        ('封面设置', {
            'fields': ('cover_image', 'cover_url', 'cover_url_preview_large'),
            'description': '支持两种方式：1.上传本地图片 2.输入图片URL（外链或本地路径）'
        }),
        ('链接信息', {
            'fields': ('view_url',)
        }),
        ('备注信息', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def cover_url_preview(self, obj):
        """封面预览（列表页）- 使用缩略图"""
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:40px;max-width:60px;object-fit:cover;" />')
        return "-"
    cover_url_preview.short_description = "封面预览"

    def cover_url_preview_large(self, obj):
        """封面预览大图标（编辑页）- 使用缩略图"""
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:120px;max-width:200px;object-fit:cover;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" />')
        return '<span style="color:#999;">暂无封面</span>'
    cover_url_preview_large.short_description = '当前封面预览'
    
    def view_url_link(self, obj):
        """观看链接"""
        if obj.view_url:
            return mark_safe(f'<a href="{obj.view_url}" target="_blank">观看</a>')
        return "-"
    view_url_link.short_description = "观看链接"
    
    def notes_preview(self, obj):
        """备注预览"""
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = '备注'
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-bv/", self.admin_site.admin_view(self.import_bv_view), name="import-bv-work"),
        ]
        return my_urls + urls

    def import_bv_view(self, request):
        """导入B站作品视图"""
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]
                collection_name = form.get_collection_name()
                notes = form.cleaned_data.get("notes", "")
                try:
                    result = import_bv_work(bvid, collection_name, notes)
                    if result["success"]:
                        messages.success(request, result["message"])
                    else:
                        messages.warning(request, result["message"])
                    return redirect("admin:import-bv-work")
                except Exception as e:
                    messages.error(request, f"❌ 导入失败: {e}")
        else:
            form = BVImportForm()

        return render(request, "admin/import_bv_work_form.html", {"form": form})
    
    def save_model(self, request, obj, form, change):
        """保存时自动更新合集的作品数量"""
        super().save_model(request, obj, form, change)
        obj.collection.update_works_count()
