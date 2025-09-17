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
    Recommendation,
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
            if os.path.exists(cover_path):
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
        widgets = {
            'song': FilteredSelectMultiple("歌曲", is_stacked=False),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为style字段设置queryset，确保在添加新项时能显示所有曲风
        self.fields['style'].queryset = Style.objects.all()
        
        # 如果正在编辑一个已存在的SongStyle实例，过滤掉已经与该曲风关联的歌曲
        if self.instance and self.instance.pk:
            # 获取当前曲风已关联的歌曲
            existing_song_ids = SongStyle.objects.filter(style=self.instance.style).values_list('song', flat=True)
            # 从歌曲选择列表中排除这些歌曲
            self.fields['song'].queryset = self.fields['song'].queryset.exclude(id__in=existing_song_ids)
        elif 'style' in self.data:
            # 如果通过表单数据传递了style ID，也进行过滤
            try:
                style_id = int(self.data.get('style'))
                existing_song_ids = SongStyle.objects.filter(style_id=style_id).values_list('song', flat=True)
                self.fields['song'].queryset = self.fields['song'].queryset.exclude(id__in=existing_song_ids)
            except (ValueError, TypeError):
                pass


class SongTagForm(forms.ModelForm):
    class Meta:
        model = SongTag
        fields = '__all__'
        widgets = {
            'song': FilteredSelectMultiple("歌曲", is_stacked=False),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为tag字段设置queryset，确保在添加新项时能显示所有标签
        self.fields['tag'].queryset = Tag.objects.all()
        
        # 如果正在编辑一个已存在的SongTag实例，过滤掉已经与该标签关联的歌曲
        if self.instance and self.instance.pk:
            # 获取当前标签已关联的歌曲
            existing_song_ids = SongTag.objects.filter(tag=self.instance.tag).values_list('song', flat=True)
            # 从歌曲选择列表中排除这些歌曲
            self.fields['song'].queryset = self.fields['song'].queryset.exclude(id__in=existing_song_ids)
        elif 'tag' in self.data:
            # 如果通过表单数据传递了tag ID，也进行过滤
            try:
                tag_id = int(self.data.get('tag'))
                existing_song_ids = SongTag.objects.filter(tag_id=tag_id).values_list('song', flat=True)
                self.fields['song'].queryset = self.fields['song'].queryset.exclude(id__in=existing_song_ids)
            except (ValueError, TypeError):
                pass