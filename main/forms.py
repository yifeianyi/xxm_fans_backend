from django.contrib import admin
from django import forms
from .models import SongRecord
from django.conf import settings
import os
from .models import (
    Songs,
    Style,
    Tag,
    SongRecord,
    SongStyle,
    SongTag,
    ViewBaseMess,
    ViewRealTimeInformation,
)
from django.contrib.admin.widgets import AutocompleteSelect, FilteredSelectMultiple
from django.contrib.admin.widgets import AutocompleteSelect

class BVImportForm(forms.Form):
    bvid = forms.CharField(label="bv号", max_length=20)

# 替换Record封面图的
class SongRecordForm(forms.ModelForm):
    replace_cover = forms.ImageField(label="更换封面图（仅内容覆盖，路径和文件名不变）", required=False)
    class Meta:
        model = SongRecord
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].initial = "	https://player.bilibili.com/player.html?bvid='换成对应BV号'"
        self.fields['cover_url'].initial = "/covers/2025/01/01.jpg"


    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cover = self.cleaned_data.get('replace_cover')
        if new_cover and instance.cover_url:
            
            # 兼容 /covers/ 前缀和无 /covers/ 前缀
            rel_path = instance.cover_url.lstrip('/')
            if rel_path.startswith('covers/'):
                rel_path = rel_path[len('covers/'):]
            cover_path = os.path.join(settings.BASE_DIR, 'xxm_fans_frontend', 'public', 'covers', rel_path)
            
            # 确保目录存在
            cover_dir = os.path.dirname(cover_path)
            os.makedirs(cover_dir, exist_ok=True)
            
            # 保存文件
            with open(cover_path, 'wb+') as f:
                for chunk in new_cover.chunks():
                    f.write(chunk)
        if commit:
            instance.save()
        return instance
   
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
        queryset=Songs.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="待选歌曲"
    )
    selected_songs = forms.ModelMultipleChoiceField(
        queryset=Songs.objects.none(),  # 动态设置
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
        self.fields['available_songs'].queryset = Songs.objects.all().order_by('song_name')
        self.fields['selected_songs'].queryset = Songs.objects.none()


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
        queryset=Songs.objects.none(),  # 动态设置
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 100%; height: 300px;'
        }),
        required=False,
        label="待选歌曲"
    )
    selected_songs = forms.ModelMultipleChoiceField(
        queryset=Songs.objects.none(),  # 动态设置
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
        self.fields['available_songs'].queryset = Songs.objects.all().order_by('song_name')
        self.fields['selected_songs'].queryset = Songs.objects.none()