from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.utils.html import format_html
from .models import Gallery


class GalleryAdminForm(forms.ModelForm):
    """图集管理表单"""
    
    tags_input = forms.CharField(
        label='标签',
        required=False,
        help_text='输入标签，用逗号分隔（例如：表情包,搞笑,可爱）',
        widget=forms.TextInput(attrs={
            'placeholder': '输入标签，用逗号分隔',
            'style': 'width: 100%;'
        })
    )
    
    class Meta:
        model = Gallery
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 将标签列表转换为逗号分隔的字符串
            tags = self.instance.tags or []
            self.fields['tags_input'].initial = ', '.join(tags)
    
    def clean_tags_input(self):
        """清理标签输入"""
        tags_str = self.cleaned_data.get('tags_input', '')
        if tags_str:
            # 分割标签，去除空格和空标签
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            return tags
        return []


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    """图集管理后台"""
    form = GalleryAdminForm

    list_display = [
        'id', 'title', 'parent_id', 'level',
        'image_count', 'is_active', 'created_at',
        'manage_images_link'
    ]
    list_filter = ['level', 'is_active', 'created_at']
    search_fields = ['id', 'title', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'image_count', 'level',
        'images_preview'
    ]

    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'title', 'description', 'cover_url')
        }),
        ('层级关系', {
            'fields': ('parent', 'level', 'sort_order', 'is_active'),
            'description': '层级会根据父图集自动计算'
        }),
        ('文件夹信息', {
            'fields': ('folder_path', 'image_count')
        }),
        ('图片管理', {
            'fields': ('images_preview',),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('tags_input',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    change_form_template = 'admin/gallery/change_form.html'

    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/upload-image/',
                self.admin_site.admin_view(self.upload_image_view),
                name='gallery_upload_image'
            ),
            path(
                '<path:object_id>/delete-image/<str:filename>/',
                self.admin_site.admin_view(self.delete_image_view),
                name='gallery_delete_image'
            ),
            path(
                '<path:object_id>/update-cover/',
                self.admin_site.admin_view(self.update_cover_view),
                name='gallery_update_cover'
            ),
            path(
                '<path:object_id>/refresh-count/',
                self.admin_site.admin_view(self.refresh_count_view),
                name='gallery_refresh_count'
            ),
        ]
        return custom_urls + urls

    def images_preview(self, obj):
        """显示图片预览"""
        images = obj.get_images()

        if not images:
            return format_html('<p style="color: #999;">暂无图片</p>')

        html_parts = [
            '<div style="display: flex; flex-wrap: wrap; gap: 10px; max-height: 400px; overflow-y: auto;">'
        ]

        # 最多显示 12 张
        for img in images[:12]:
            html_parts.append(format_html(
                '''<div style="position: relative; width: 100px; height: 100px;">
                    <img src="{}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
                    <span style="position: absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.7); color: white; font-size: 10px; padding: 2px 4px; border-radius: 4px;">{}</span>
                </div>''',
                img['url'], img['filename']
            ))

        if len(images) > 12:
            html_parts.append(
                format_html('<p style="color: #999; font-size: 12px;">还有 {} 张图片...</p>', len(images) - 12)
            )

        html_parts.append('</div>')
        return format_html(''.join(html_parts))
    images_preview.short_description = '图片预览'

    def parent_id(self, obj):
        """显示父图集ID"""
        if obj.parent:
            return obj.parent.id
        return '-'
    parent_id.short_description = '父图集ID'

    def manage_images_link(self, obj):
        """图片管理链接"""
        url = reverse('admin:gallery_gallery_change', args=[obj.id])
        return format_html('<a href="{}#images-section">管理图片</a>', url)
    manage_images_link.short_description = '图片管理'

    def save_model(self, request, obj, form, change):
        """保存模型时自动刷新图片数量"""
        # 从表单中获取标签
        tags_input = form.cleaned_data.get('tags_input', [])
        obj.tags = tags_input
        
        super().save_model(request, obj, form, change)
        # 如果文件夹路径存在，自动刷新图片数量
        # 注意：refresh_image_count 内部会调用 save()，不需要再次调用 super().save_model()
        if obj.folder_path:
            obj.refresh_image_count()

    def upload_image_view(self, request, object_id):
        """上传图片视图"""
        gallery = get_object_or_404(Gallery, id=object_id)

        if request.method == 'POST':
            image_file = request.FILES.get('image')

            if not image_file:
                return JsonResponse({'success': False, 'message': '未选择图片'})

            # 验证文件类型（添加 GIF 和 MP4 支持）
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif', 'video/mp4']
            if image_file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'message': '仅支持 JPG、PNG、WEBP、GIF、MP4 格式'})

            # 添加图片
            filename = gallery.add_image(image_file)

            return JsonResponse({
                'success': True,
                'filename': filename,
                'url': f"{gallery.folder_path}{filename}",
                'image_count': gallery.image_count
            })

        return render(request, 'admin/gallery/upload_image.html', {'gallery': gallery})

    def delete_image_view(self, request, object_id, filename):
        """删除图片视图"""
        gallery = get_object_or_404(Gallery, id=object_id)

        if request.method == 'POST':
            # 安全检查：防止删除封面
            if filename == Gallery.COVER_FILENAME:
                return JsonResponse({'success': False, 'message': '不能删除封面图片'})

            success = gallery.delete_image(filename)

            if success:
                return JsonResponse({
                    'success': True,
                    'filename': filename,
                    'image_count': gallery.image_count
                })
            else:
                return JsonResponse({'success': False, 'message': '文件不存在'})

        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

    def update_cover_view(self, request, object_id):
        """更新封面视图"""
        gallery = get_object_or_404(Gallery, id=object_id)

        if request.method == 'POST':
            cover_file = request.FILES.get('cover')

            if not cover_file:
                return JsonResponse({'success': False, 'message': '未选择封面'})

            # 验证文件类型（添加 GIF 和 MP4 支持）
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif', 'video/mp4']
            if cover_file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'message': '仅支持 JPG、PNG、WEBP、GIF、MP4 格式'})

            gallery.update_cover(cover_file)

            return JsonResponse({
                'success': True,
                'cover_url': gallery.cover_url
            })

        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

    def refresh_count_view(self, request, object_id):
        """刷新图片数量视图"""
        gallery = get_object_or_404(Gallery, id=object_id)

        if request.method == 'POST':
            gallery.refresh_image_count()

            return JsonResponse({
                'success': True,
                'image_count': gallery.image_count
            })

        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})


@staff_member_required
def get_gallery_images(request, gallery_id):
    """获取图集图片列表（仅 Admin 使用）"""
    try:
        gallery = Gallery.objects.get(id=gallery_id)
        images = gallery.get_images()

        # 分离封面和其他图片
        cover = None
        others = []

        for img in images:
            if img['filename'] == Gallery.COVER_FILENAME:
                cover = img
            else:
                others.append(img)

        return JsonResponse({
            'success': True,
            'images': {
                'cover': cover,
                'others': others
            },
            'total': len(images)
        })
    except Gallery.DoesNotExist:
        return JsonResponse({'success': False, 'message': '图集不存在'})