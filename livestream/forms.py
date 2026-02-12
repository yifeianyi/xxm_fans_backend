from django import forms


class BVImportForm(forms.Form):
    """直播记录BV号导入表单"""
    bvid = forms.CharField(
        label="BV号",
        max_length=20,
        help_text="请输入B站视频的BV号，例如：BV1xx411c7mD"
    )
