from django.contrib import admin, messages
from django.urls import reverse
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from urllib.parse import unquote, quote
from .models import Songs, Style, SongRecord, SongStyle, ViewBaseMess, ViewRealTimeInformation
# Register your models here.
from .models import *
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.shortcuts import render
from .utils import import_bv_song
from django.utils.html import format_html, format_html_join

admin.site.register(Style)
admin.site.register(SongStyle)
    

class SelectMainSongFrom(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    main_song = forms.ChoiceField(label="请选择主项",widget=forms.RadioSelect)

@admin.register(Songs)
class SongsAdmin(admin.ModelAdmin):
    list_display = ['song_name_display','singer_display', 'last_performed_display', 'perform_count_display', 'view_records' ]
    list_filter = ['language','last_performed']
    search_fields = ["song_name","perform_count","singer"]
    actions = ['merge_songs_action']

    list_per_page = 25  # 每页30条
    
    class Media:
        css = {
            'all': ('admin/css/collapsible.css',)
        }
        js = ('admin/js/collapsible.js',)
    
    """
        后台管理界面的显示方式
    """
    @admin.display(description="歌手",ordering="singer")
    def singer_display(self,obj):
        return obj.singer

    @admin.display(description="最近演唱时间", ordering="last_performed")
    def last_performed_display(self, obj):
        return obj.last_performed

    @admin.display(description="歌名", ordering="song_name")
    def song_name_display(self, obj):
        return obj.song_name

    @admin.display(description="演唱次数",ordering="perform_count")
    def perform_count_display(self, obj):
        return obj.perform_count
    
    @admin.display(description="演唱记录")
    def view_records(self, obj):
        records = SongRecord.objects.filter(song=obj).order_by('-performed_at')
        if not records:
            return "暂无记录"

        from django.utils.html import format_html, format_html_join

        def get_date_html(record):
            date_str = record.performed_at.strftime('%Y-%m-%d') if record.performed_at else '未知日期'
            if record.url:
                return format_html("<a href='{}' target='_blank' style='color:#79aec8;font-weight:bold;text-decoration:underline;font-size:13px;'>{}</a>", record.url, date_str)
            else:
                return date_str

        records_html = format_html_join(
            '',
            '<li>{}{}</li>',
            (
                (get_date_html(r), f"（{r.notes}）" if r.notes else "")
                for r in records
            )
        )
        ul_html = format_html('<ul style="margin:0 0 0 10px;padding:0;list-style:disc inside;">{}</ul>', records_html)
        return format_html(
            '<button type="button" class="toggle-records" data-song-id="{}" style="background: #79aec8; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">查看记录</button>'
            '<div class="records-content" id="records-{}" style="display: none; margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 3px;">{}</div>',
            obj.id, obj.id, ul_html
        )
    ##################################
    #   合并多个数据项
    ##################################
    
    #获取跳转页面的url
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("merge_songs/", self.admin_site.admin_view(self.merge_songs_view), name="merge_songs"),
        ]
        return custom_urls + urls
    
    def merge_songs_view(self, request):
        ids = request.GET.get("ids", "") or request.POST.get("ids", "")
        id_list = ids.split(",")
        selected_songs = Songs.objects.filter(id__in=id_list)

        if request.method == "POST":
            master_id = request.POST.get("master_id")
            if not master_id:
                self.message_user(request, "必须选择一个主项", level=messages.ERROR)
                return redirect(request.path + f"?ids={ids}")

            master_song = Songs.objects.get(id=master_id)
            other_songs = selected_songs.exclude(id=master_id)

            for song in other_songs:
                for record in SongRecord.objects.filter(song=song):
                    # 复制所有字段，song 换成 master_song
                    record.pk = None  # 新建一条
                    record.song = master_song
                    record.save()
                master_song.perform_count += song.perform_count
            master_song.save()
            other_songs.delete()

            self.message_user(request, f"成功将 {len(id_list)-1} 项合并到主项《{master_song.song_name}》。")

            next_url = request.GET.get('next') or request.POST.get('next') or "../"
            next_url = unquote(next_url)

            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(next_url)  # 返回admin changelist 页

        # GET 请求显示页面
        context = dict(
            self.admin_site.each_context(request),
            songs=selected_songs,
            ids=ids,
            next=request.GET.get('next', '') 
        )
        return TemplateResponse(request, "admin/merge_songs.html", context)

    def merge_songs_action(self, request, queryset):
        from django.http import HttpResponseRedirect
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        if len(selected) < 2:
            self.message_user(request, "至少选择两个才能合并",level=messages.WARNING)
            return None
        # #重定向到新页面选择合并方式

        current_path = request.get_full_path()
        # print("merge_songs_action current_path:", current_path)
        next_url = quote(current_path)
        return HttpResponseRedirect(f"./merge_songs/?ids={','.join(selected)}&next={next_url}")
    merge_songs_action.short_description = "合并选中的歌曲"

class BVImportForm(forms.Form):
        bvid = forms.CharField(label="BV号", max_length=20)
@admin.register(SongRecord)
class SongReccordAdmin(admin.ModelAdmin):
    list_display = ("song", "performed_at", "url","cover_url","notes")
    actions = ["import_from_bv"]
    search_fields = ["song__song_name", "notes"]
    list_filter = ["performed_at", "song__song_name"]

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
                        if result["cover_url"]:
                            msg += "，🖼️ 封面已下载"
                        request.session.setdefault("_messages", []).append(("SUCCESS", msg))
                    return redirect("admin:import-bv-songrecord")
                except Exception as e:
                    self.message_user(request, f"❌ 导入失败: {e}", level=messages.ERROR)
        else:
            form = BVImportForm()

        return render(request, "admin/import_bv_form.html", {"form": form})