from django.contrib import admin, messages
from django.urls import reverse
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.utils.safestring import mark_safe
from .models import Collection, Work
from .forms import BVImportForm
from .utils import import_bv_work

# Register your models here.

class WorkInline(admin.TabularInline):
    model = Work
    extra = 0
    fields = ['title', 'author', 'position', 'display_order', 'cover_url_preview']
    readonly_fields = ['cover_url_preview']
    
    def cover_url_preview(self, obj):
        """封面预览"""
        if obj.cover_url:
            return mark_safe(f'<img src="{obj.cover_url}" style="height:40px;max-width:60px;object-fit:cover;" />')
        return "-"
    cover_url_preview.short_description = "封面预览"

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'works_count', 'position', 'display_order', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['works_count', 'created_at', 'updated_at']
    inlines = [WorkInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'works_count', 'position', 'display_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'collection', 'position', 'display_order', 'cover_url_preview', 'view_url_link', 'notes_preview']
    list_filter = ['collection', 'author']
    search_fields = ['title', 'author', 'collection__name', 'notes']
    change_list_template = 'admin/fansDIY/work/change_list.html'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('collection', 'title', 'author', 'position', 'display_order')
        }),
        ('链接信息', {
            'fields': ('cover_url', 'view_url')
        }),
        ('备注信息', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def cover_url_preview(self, obj):
        """封面预览"""
        if obj.cover_url:
            # 处理相对路径
            if obj.cover_url.startswith('/'):
                url = obj.cover_url
            else:
                url = '/' + obj.cover_url
            return mark_safe(f'<img src="{url}" style="height:40px;max-width:60px;object-fit:cover;" />')
        return "-"
    cover_url_preview.short_description = "封面预览"
    
    def view_url_link(self, obj):
        """观看链接"""
        if obj.view_url:
            return mark_safe(f'<a href="{obj.view_url}" target="_blank">观看</a>')
        return "-"
    view_url_link.short_description = "观看链接"
    
    def notes_preview(self, obj):
        """备注预览"""
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = '备注'
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-bv/", self.admin_site.admin_view(self.import_bv_view), name="import-bv-work"),
        ]
        return my_urls + urls

    def import_bv_view(self, request):
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]
                collection_name = form.get_collection_name()
                notes = form.cleaned_data.get("notes", "")
                try:
                    result = import_bv_work(bvid, collection_name, notes)
                    if result["success"]:
                        messages.success(request, result["message"])
                    else:
                        messages.warning(request, result["message"])
                    return redirect("admin:import-bv-work")
                except Exception as e:
                    messages.error(request, f"❌ 导入失败: {e}")
        else:
            form = BVImportForm()

        return render(request, "admin/import_bv_work_form.html", {"form": form})
    
    def save_model(self, request, obj, form, change):
        """保存时自动更新合集的作品数量"""
        super().save_model(request, obj, form, change)
        obj.collection.update_works_count()