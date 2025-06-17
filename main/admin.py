from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from .models import Songs, Style, SongRecord, SongStyle, ViewBaseMess, ViewRealTimeInformation
# Register your models here.
from .models import *
from django.shortcuts import render
from .utils import import_bv_song

# admin.site.register(Songs)
admin.site.register(Style)
admin.site.register(SongStyle)
# admin.site.register(SongRecord)

@admin.register(Songs)
class SongsAdmin(admin.ModelAdmin):
    list_display = ('song_name', 'last_performed', 'perform_count' )


class BVImportForm(forms.Form):
    bvid = forms.CharField(label="B站 BV号", max_length=20)

@admin.register(SongRecord)
class SongReccordAdmin(admin.ModelAdmin):
    list_display = ("song", "performed_at", "url", "notes")
    actions = ["import_from_bv"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-bv/", self.admin_site.admin_view(self.import_bv_view), name="import-bv-songrecord"),
        ]
        return my_urls + urls

    def import_bv_view(self, request):
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]
                try:
                    result_list = import_bv_song(bvid)
                    for result in result_list:
                        msg = f"✅ {result['song_name']}"
                        if result["note"]:
                            msg += f"（{result['note']}）"
                        if result["created_song"]:
                            msg += "，🎵 新建歌曲"
                        request.session.setdefault("_messages", []).append(("SUCCESS", msg))
                    return redirect("admin:import-bv-songrecord")
                except Exception as e:
                    self.message_user(request, f"❌ 导入失败: {e}", level=messages.ERROR)
        else:
            form = BVImportForm()

        return render(request, "admin/import_bv_form.html", {"form": form})

    # def import_from_bv(self, request, queryset):
        if "apply" in request.POST:
            Form = BVImportFrom(request.POST)
            if Form.is_valid():
                bvid = Form.cleaned_data["bvid"]
                try:
                    result_list = import_bv_song(bvid)
                    if not result_list:
                        self.message_user(request, "没有找到可导入的分P歌曲", level=messages.WARNING)
                        return None
                    
                    for result in result_list:
                        msg = f"✅ {result['song_name']} 导入成功"
                        if result["note"]:
                            msg += f"（{result['note']}）"
                        if result["created_song"]:
                            msg += "，新歌曲已创建"
                        self.message_user(request, msg, level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"❌ 失败: {str(e)}", level=messages.ERROR)
                return None
        else:
            Form = BVImportFrom()
        return render(request, "admin/import_bv_form.html", {"form": Form})
