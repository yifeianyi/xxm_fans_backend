from django import forms
from .models import Collection

class BVImportForm(forms.Form):
    bvid = forms.CharField(
        label="BV号", 
        max_length=20,
        help_text="请输入B站视频的BV号，例如：BV1xx411c7mD"
    )
    
    # 合集选择方式
    collection_choice = forms.ChoiceField(
        label="合集选择方式",
        choices=[
            ('existing', '选择已有合集'),
            ('new', '创建新合集')
        ],
        initial='existing',
        widget=forms.RadioSelect
    )
    
    # 已有合集下拉列表
    existing_collection = forms.ModelChoiceField(
        label="选择已有合集",
        queryset=Collection.objects.all().order_by('name'),
        required=False,
        empty_label="请选择合集",
        help_text="从已有合集中选择一个"
    )
    
    # 新合集名称
    collection_name = forms.CharField(
        label="新合集名称", 
        max_length=200,
        required=False,
        help_text="输入新合集名称，如果不存在会自动创建"
    )
    
    notes = forms.CharField(
        label="备注", 
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="可选，添加作品备注信息"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态更新已有合集的选项
        self.fields['existing_collection'].queryset = Collection.objects.all().order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        collection_choice = cleaned_data.get('collection_choice')
        
        if collection_choice == 'existing':
            if not cleaned_data.get('existing_collection'):
                raise forms.ValidationError("请选择一个已有合集")
        elif collection_choice == 'new':
            if not cleaned_data.get('collection_name'):
                raise forms.ValidationError("请输入新合集名称")
        
        return cleaned_data
    
    def get_collection_name(self):
        """获取最终选择的合集名称"""
        collection_choice = self.cleaned_data.get('collection_choice')
        if collection_choice == 'existing':
            collection = self.cleaned_data.get('existing_collection')
            return collection.name if collection else None
        else:
            return self.cleaned_data.get('collection_name') 