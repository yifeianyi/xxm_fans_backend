from django import forms
from .models import SongRecord

class BVImportForm(forms.Form):
    bvid = forms.CharField(label="bv号", max_length=20)

# 替换Record封面图的
class ReplaceCoverForm(forms.ModelForm):
    replace_cover = forms.ImageField(label="更换封面图（仅内容覆盖，路径和文件名不变）", required=False)
    class Meta:
        model = SongRecord
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cover = self.cleaned_data.get('replace_cover')
        if new_cover and instance.cover_url:
            from django.conf import settings
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