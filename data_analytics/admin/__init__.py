"""
Admin 配置
"""
from django.contrib import admin, messages
from django.urls import path, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from ..models import WorkStatic, WorkMetricsHour, CrawlSession, Account, FollowerMetrics
from ..forms import WorkStaticForm, BVImportForm
from ..services.bilibili_service import BilibiliWorkStaticImporter


@admin.register(WorkStatic)
class WorkStaticAdmin(admin.ModelAdmin):
    """作品静态信息 Admin"""
    form = WorkStaticForm
    change_form_template = 'admin/data_analytics/workstatic/change_form.html'
    list_display = ['id', 'platform', 'work_id', 'title', 'author', 'publish_time', 'is_valid', 'cover_preview']
    list_filter = ['platform', 'is_valid', 'publish_time']
    search_fields = ['work_id', 'title', 'author']
    list_per_page = 50
    ordering = ['-publish_time']
    readonly_fields = ['id', 'cover_preview']

    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path('bv-import/', self.admin_site.admin_view(self.import_bv_view), name='bv-import-workstatic'),
            path('import-bv-api/', self.admin_site.admin_view(self.import_bv_api), name='data_analytics_workstatic_import_bv_api'),
        ]
        return custom_urls + urls

    def import_bv_view(self, request):
        """BV号导入视图（页面表单）"""
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]

                # 使用导入服务
                importer = BilibiliWorkStaticImporter()
                success, message, work_static = importer.import_bv_work_static(bvid)

                if success:
                    self.message_user(request, f"✅ {message}", level=messages.SUCCESS)
                    return HttpResponseRedirect('/admin/data_analytics/workstatic/')
                else:
                    self.message_user(request, f"❌ {message}", level=messages.ERROR)
        else:
            form = BVImportForm()

        return render(request, 'admin/data_analytics/import_bv_form.html', {"form": form})

    def import_bv_api(self, request):
        """BV 号导入 API（返回 JSON）"""
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': '只支持 POST 请求'}, status=405)

        bvid = request.POST.get('bvid', '').strip()
        if not bvid:
            return JsonResponse({'success': False, 'message': 'BV 号不能为空'})

        try:
            importer = BilibiliWorkStaticImporter()
            success, message, work_static = importer.import_bv_work_static(bvid)

            if success:
                # 返回作品信息用于填充表单
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'data': {
                        'platform': work_static.platform,
                        'work_id': work_static.work_id,
                        'title': work_static.title,
                        'author': work_static.author,
                        'publish_time': work_static.publish_time.strftime('%Y-%m-%d %H:%M:%S') if work_static.publish_time else '',
                        'cover_url': work_static.cover_url,
                        'is_valid': work_static.is_valid,
                    }
                })
            else:
                return JsonResponse({'success': False, 'message': message})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"导入失败: {str(e)}"})

    def cover_preview(self, obj):
        """封面预览（使用缩略图）"""
        if obj.cover_url:
            # 使用缩略图生成器获取缩略图 URL
            from core.thumbnail_generator import ThumbnailGenerator

            # 如果是本地路径，尝试获取缩略图
            if not obj.cover_url.startswith('http'):
                thumbnail_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
                return mark_safe(f'<img src="{thumbnail_url}" style="height:60px;max-width:80px;object-fit:cover;" />')
            else:
                # 外部 URL，直接显示
                return mark_safe(f'<img src="{obj.cover_url}" style="height:60px;max-width:80px;object-fit:cover;" />')
        return "-"
    cover_preview.short_description = "封面预览"
    cover_preview.allow_tags = True


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


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """账号管理 Admin"""
    list_display = ['id', 'name', 'uid', 'platform', 'is_active', 'follower_count', 'latest_crawl_time', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['name', 'uid']
    list_per_page = 20
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'follower_count', 'latest_crawl_time']

    def follower_count(self, obj):
        """最新粉丝数"""
        latest = obj.followermetrics_set.order_by('-crawl_time').first()
        return latest.follower_count if latest else '-'
    follower_count.short_description = '最新粉丝数'

    def latest_crawl_time(self, obj):
        """最新爬取时间"""
        latest = obj.followermetrics_set.order_by('-crawl_time').first()
        return latest.crawl_time.strftime('%Y-%m-%d %H:%M') if latest else '-'
    latest_crawl_time.short_description = '最新更新'


@admin.register(FollowerMetrics)
class FollowerMetricsAdmin(admin.ModelAdmin):
    """粉丝数据 Admin"""
    list_display = ['id', 'account', 'follower_count', 'crawl_time', 'ingest_time', 'delta']
    list_filter = ['account', 'crawl_time']
    search_fields = ['account__name', 'account__uid']
    list_per_page = 50
    ordering = ['-crawl_time']
    readonly_fields = ['id', 'ingest_time', 'delta']

    def delta(self, obj):
        """粉丝变化量"""
        # 获取同账号上一条记录
        prev = FollowerMetrics.objects.filter(
            account=obj.account,
            crawl_time__lt=obj.crawl_time
        ).order_by('-crawl_time').first()

        if prev:
            diff = obj.follower_count - prev.follower_count
            return f"+{diff}" if diff > 0 else str(diff)
        return "0"
    delta.short_description = '变化量'