from django.contrib import admin
from django import forms
from .models import SongRecord, Song, Style, Tag, SongStyle, SongTag
from django.conf import settings
import os


class BVImportForm(forms.Form):
    bvid = forms.CharField(label="bv号", max_length=20)


# 替换Record封面图的
class SongRecordForm(forms.ModelForm):
    cover_image = forms.ImageField(
        label="上传/替换封面",
        required=False,
        help_text='上传本地图片作为封面。如果是已有记录且已有封面路径，将只替换原文件内容而不改变路径；如果是新记录，将按日期自动创建路径。上传后会自动触发缩略图生成。'
    )

    class Meta:
        model = SongRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 安全地设置初始值，避免字段不存在时抛出KeyError
        if 'url' in self.fields:
            self.fields['url'].initial = "https://player.bilibili.com/player.html?bvid='换成对应BV号'"
        if 'cover_url' in self.fields:
            self.fields['cover_url'].initial = "/covers/2025/01/01.jpg"

        # 调整字段顺序
        self.fields = self._reorder_fields()

    def _reorder_fields(self):
        """重新排序字段，让上传字段在前面"""
        fields = {}
        field_order = [
            'song', 'performed_at', 'url', 'notes',
            'cover_image', 'cover_url'
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
            # 保存后触发生成缩略图
            self._generate_thumbnail(instance.cover_url)

        return instance

    def _replace_cover_content(self, cover_url, new_image):
        """替换已有封面的内容，保持原路径和文件名"""
        from django.core.files.storage import default_storage
        from django.conf import settings

        try:
            # 标准化路径
            rel_path = cover_url.lstrip('/')
            if rel_path.startswith('media/'):
                rel_path = rel_path[len('media/'):]
            if rel_path.startswith('covers/'):
                rel_path = rel_path[len('covers/'):]

            # 完整的存储路径
            storage_path = f'covers/{rel_path}'
            
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
        """保存新封面图片到 media/covers/ 目录，按日期组织"""
        import datetime
        from django.core.files.storage import default_storage

        try:
            # 使用当前日期组织文件夹
            now = datetime.datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')

            # 生成文件名
            ext = os.path.splitext(image.name)[1].lower()
            filename = f"{now.strftime('%Y%m%d_%H%M%S')}{ext}"

            # 保存路径: media/covers/YYYY/MM/
            upload_path = f'covers/{year}/{month}/{filename}'

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


class SongStyleForm(forms.ModelForm):
    class Meta:
        model = SongStyle
        fields = '__all__'


class BatchSongStyleForm(forms.Form):
    """批量添加歌曲曲风的表单 - 新布局"""
    song_search = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': '输入歌曲名称搜索...',
            'class': 'song-search-input',
            'style': 'width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box;'
        })
    )
    available_songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="待选歌曲"
    )
    selected_songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="已选歌曲"
    )
    style = forms.ModelChoiceField(
        queryset=Style.objects.all(),
        widget=forms.Select(attrs={
            'style': 'width: 300px; padding: 5px;'
        }),
        required=True,
        label="选择曲风"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化时显示所有歌曲到待选框
        self.fields['available_songs'].queryset = Song.objects.all().order_by('song_name')
        self.fields['selected_songs'].queryset = Song.objects.none()


class SongTagForm(forms.ModelForm):
    class Meta:
        model = SongTag
        fields = '__all__'


class BatchSongTagForm(forms.Form):
    """批量添加歌曲标签的表单 - 新布局"""
    song_search = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': '输入歌曲名称搜索...',
            'class': 'song-search-input',
            'style': 'width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box;'
        })
    )
    available_songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="待选歌曲"
    )
    selected_songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="已选歌曲"
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.Select(attrs={
            'style': 'width: 300px; padding: 5px;'
        }),
        required=True,
        label="选择标签"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化时显示所有歌曲到待选框
        self.fields['available_songs'].queryset = Song.objects.all().order_by('song_name')
        self.fields['selected_songs'].queryset = Song.objects.none()