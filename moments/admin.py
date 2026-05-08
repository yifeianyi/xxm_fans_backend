from django.contrib import admin
from django import forms
from .models import Moment, PlatformCookie


class PlatformCookieForm(forms.ModelForm):
    new_cookie = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'placeholder': '在此粘贴新的 Cookie 字符串（留空则不修改）'}),
        required=False,
        label='更新 Cookie'
    )

    class Meta:
        model = PlatformCookie
        fields = ['platform', 'is_valid', 'new_cookie']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.cookie_string:
            self.initial['new_cookie'] = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cookie = self.cleaned_data.get('new_cookie')
        if new_cookie:
            instance.cookie_string = new_cookie
        if commit:
            instance.save()
        return instance


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ('source', 'source_id', 'content_preview', 'publish_time', 'created_at')
    list_filter = ('source', 'publish_time')
    search_fields = ('content', 'source_id')
    readonly_fields = ('created_at',)
    ordering = ('-publish_time',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'


@admin.register(PlatformCookie)
class PlatformCookieAdmin(admin.ModelAdmin):
    form = PlatformCookieForm
    list_display = ('platform', 'cookie_status', 'expire_notified', 'last_checked', 'updated_at')
    list_filter = ('platform', 'is_valid')
    readonly_fields = ('last_checked', 'updated_at', 'created_at')
    exclude = ('cookie_string',)

    def cookie_status(self, obj):
        return '✅ 已配置' if obj.cookie_string else '❌ 未配置'
    cookie_status.short_description = 'Cookie 状态'
