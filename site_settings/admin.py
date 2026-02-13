from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from site_settings.models import SiteSettings, Recommendation, Milestone


class SiteSettingsForm(forms.ModelForm):
    """网站设置表单"""
    artist_profession = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '请输入职业，用逗号分隔，例如：歌手, 音乐主播, 唱见'}),
        help_text='请输入职业，用逗号分隔'
    )
    artist_voice_features = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '请输入声线特点，用逗号分隔，例如：甜美, 清脆, 有磁性'}),
        help_text='请输入声线特点，用逗号分隔'
    )

    class Meta:
        model = SiteSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 将 JSON 数组转换为逗号分隔的字符串
            if self.instance.artist_profession is not None:
                self.fields['artist_profession'].initial = ', '.join(self.instance.artist_profession) if self.instance.artist_profession else ''
            if self.instance.artist_voice_features is not None:
                self.fields['artist_voice_features'].initial = ', '.join(self.instance.artist_voice_features) if self.instance.artist_voice_features else ''

    def clean_artist_profession(self):
        """将逗号分隔的字符串转换为 JSON 数组"""
        profession = self.cleaned_data.get('artist_profession', '')
        if profession:
            # 分割字符串，去除空格和空值
            profession_list = [p.strip() for p in profession.split(',') if p.strip()]
            return profession_list
        return []

    def clean_artist_voice_features(self):
        """将逗号分隔的字符串转换为 JSON 数组"""
        features = self.cleaned_data.get('artist_voice_features', '')
        if features:
            # 分割字符串，去除空格和空值
            features_list = [f.strip() for f in features.split(',') if f.strip()]
            return features_list
        return []


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """网站设置Admin"""
    form = SiteSettingsForm
    list_display = ['id', 'artist_name', 'favicon_preview', 'artist_avatar_preview', 'artist_birthday', 'artist_constellation', 'artist_location', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['artist_name', 'artist_location']
    readonly_fields = ['favicon_preview', 'artist_avatar_preview', 'created_at', 'updated_at']

    fieldsets = (
        ('基础设置', {
            'fields': ('favicon', 'favicon_preview')
        }),
        ('艺人信息', {
            'fields': ('artist_name', 'artist_avatar', 'artist_avatar_preview', 'artist_birthday', 'artist_constellation', 'artist_location')
        }),
        ('艺人特色', {
            'fields': ('artist_profession', 'artist_voice_features')
        }),
        ('社交媒体', {
            'fields': ('bilibili_url', 'weibo_url', 'netease_music_url', 'youtube_url', 'qq_music_url', 'xiaohongshu_url', 'douyin_url')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def favicon_preview(self, obj):
        """favicon预览"""
        if obj.favicon:
            return mark_safe(f'<img src="{obj.favicon.url}" style="height:32px;width:32px;object-fit:cover;border-radius:4px;" />')
        return '-'
    favicon_preview.short_description = '当前图标预览'

    def artist_avatar_preview(self, obj):
        """艺人头像预览"""
        if obj.artist_avatar:
            return mark_safe(f'<img src="{obj.artist_avatar.url}" style="height:80px;width:80px;object-fit:cover;border-radius:8px;" />')
        return '-'
    artist_avatar_preview.short_description = '当前头像预览'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """推荐语Admin"""
    list_display = ['id', 'content_preview', 'is_active', 'song_count', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['content']
    filter_horizontal = ['recommended_songs']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['activate_recommendations', 'deactivate_recommendations']

    def content_preview(self, obj):
        """显示推荐语预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '推荐语内容'

    def song_count(self, obj):
        """显示推荐歌曲数量"""
        return obj.recommended_songs.count()
    song_count.short_description = '推荐歌曲数'

    def activate_recommendations(self, request, queryset):
        """批量激活推荐语"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 条推荐语。')
    activate_recommendations.short_description = '激活选中的推荐语'

    def deactivate_recommendations(self, request, queryset):
        """批量停用推荐语"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 条推荐语。')
    deactivate_recommendations.short_description = '停用选中的推荐语'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """里程碑Admin"""
    list_display = ['id', 'date', 'title', 'display_order', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-date', 'display_order']
    readonly_fields = ['created_at']