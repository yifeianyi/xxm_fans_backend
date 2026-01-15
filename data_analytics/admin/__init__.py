"""
Admin 配置
"""
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse

from ..models import WorkStatic, WorkMetricsHour, CrawlSession
from ..forms import BVImportForm
from ..services.bilibili_service import BilibiliWorkStaticImporter


@admin.register(WorkStatic)
class WorkStaticAdmin(admin.ModelAdmin):
    """作品静态信息 Admin"""
    list_display = ['id', 'platform', 'work_id', 'title', 'author', 'publish_time', 'is_valid', 'cover_preview']
    list_filter = ['platform', 'is_valid', 'publish_time']
    search_fields = ['work_id', 'title', 'author']
    list_per_page = 50
    ordering = ['-publish_time']
    readonly_fields = ['id', 'cover_preview']
    change_list_template = 'admin/data_analytics/workstatic/change_list.html'
    actions = ['delete_selected']
    
    def cover_preview(self, obj):
        """封面预览"""
        if obj.cover_url:
            # 处理相对路径
            if obj.cover_url.startswith('views/'):
                url = f"/media/{obj.cover_url}"
            elif obj.cover_url.startswith('/'):
                url = obj.cover_url
            else:
                url = f'/{obj.cover_url}'
            from django.utils.safestring import mark_safe
            return mark_safe(f'<img src="{url}" style="height:60px;max-width:80px;object-fit:cover;" />')
        return "-"
    cover_preview.short_description = "封面预览"
    cover_preview.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-bv-work-static/", self.admin_site.admin_view(self.import_bv_work_static_view), name="import-bv-work-static"),
        ]
        return my_urls + urls
    
    def import_bv_work_static_view(self, request):
        """导入B站作品静态信息视图"""
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]
                try:
                    importer = BilibiliWorkStaticImporter()
                    success, message, work_static = importer.import_bv_work_static(bvid)
                    
                    if success:
                        messages.success(request, message)
                    else:
                        messages.warning(request, message)
                    
                    return redirect("admin:import-bv-work-static")
                except Exception as e:
                    messages.error(request, f"❌ 导入失败: {e}")
        else:
            form = BVImportForm()

        return render(request, "admin/data_analytics/import_bv_work_static_form.html", {"form": form})
    
    def delete_queryset(self, request, queryset):
        """自定义批量删除操作"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"成功删除 {count} 条作品静态信息", messages.SUCCESS)


@admin.register(WorkMetricsHour)
class WorkMetricsHourAdmin(admin.ModelAdmin):
    """作品小时指标 Admin"""
    list_display = ['id', 'platform', 'work_id', 'crawl_time', 'view_count', 'like_count', 'coin_count', 'favorite_count']
    list_filter = ['platform', 'crawl_time', 'session_id']
    search_fields = ['work_id']
    list_per_page = 50
    ordering = ['-crawl_time']
    readonly_fields = ['id', 'ingest_time']


@admin.register(CrawlSession)
class CrawlSessionAdmin(admin.ModelAdmin):
    """爬取会话 Admin"""
    list_display = ['id', 'source', 'node_id', 'start_time', 'end_time', 'total_work_count', 'success_count', 'fail_count']
    list_filter = ['source', 'start_time']
    search_fields = ['node_id']
    list_per_page = 50
    ordering = ['-start_time']
    readonly_fields = ['id']