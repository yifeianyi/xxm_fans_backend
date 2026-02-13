import os
import re
from datetime import datetime

from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.safestring import mark_safe
from django import forms
from django.core.files.storage import default_storage

from .models import Livestream
from .forms import BVImportForm

# 使用B站工具
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError


class LivestreamAdminForm(forms.ModelForm):
    """直播记录表单 - 支持本地上传封面和弹幕云图"""
    cover_image = forms.ImageField(
        label='上传/替换封面',
        required=False,
        help_text='上传本地图片作为封面。如果是已有封面路径，将只替换原文件内容而不改变路径。上传后会自动触发缩略图生成。'
    )
    danmaku_cloud_image = forms.ImageField(
        label='上传/替换弹幕云图',
        required=False,
        help_text='上传本地图片作为弹幕云图。如果是已有路径，将只替换原文件内容而不改变路径。'
    )

    class Meta:
        model = Livestream
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 调整字段顺序
        self.fields = self._reorder_fields()

    def _reorder_fields(self):
        """重新排序字段，让上传字段在前面"""
        fields = {}
        field_order = [
            'date', 'title', 'summary', 'live_moment', 'is_active', 'sort_order',
            'bvid', 'duration_seconds', 'duration_formatted', 'parts',
            'view_count', 'danmaku_count', 'start_time', 'end_time',
            'cover_image', 'cover_url',
            'danmaku_cloud_image', 'danmaku_cloud_url'
        ]
        for field_name in field_order:
            if field_name in self.fields:
                fields[field_name] = self.fields[field_name]
        # 添加剩余字段
        for field_name, field in self.fields.items():
            if field_name not in fields:
                fields[field_name] = field
        return fields

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 处理封面上传
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            if instance.cover_url and instance.pk:
                # 已有封面路径：只替换内容，保持原路径
                self._replace_image_content(instance.cover_url, cover_image)
            else:
                # 没有封面路径：根据日期创建新路径
                saved_path = self._save_new_image(cover_image, instance.date, 'covers')
                if saved_path:
                    instance.cover_url = saved_path

        # 处理弹幕云图上传
        danmaku_image = self.cleaned_data.get('danmaku_cloud_image')
        if danmaku_image:
            if instance.danmaku_cloud_url and instance.pk:
                # 已有路径：只替换内容
                self._replace_image_content(instance.danmaku_cloud_url, danmaku_image)
            else:
                # 没有路径：根据日期创建新路径
                saved_path = self._save_new_image(danmaku_image, instance.date, 'cloud_picture')
                if saved_path:
                    instance.danmaku_cloud_url = saved_path

        if commit:
            instance.save()
            # 保存后触发缩略图生成
            if cover_image:
                self._generate_thumbnail(instance.cover_url)
            if danmaku_image:
                self._generate_thumbnail(instance.danmaku_cloud_url)

        return instance

    def _replace_image_content(self, image_url, new_image):
        """替换已有图片的内容，保持原路径和文件名"""
        try:
            # 标准化路径
            rel_path = image_url.lstrip('/')
            if rel_path.startswith('media/'):
                rel_path = rel_path[len('media/'):]

            # 确定存储路径
            storage_path = rel_path
            
            # 获取完整的文件系统路径
            full_path = os.path.join(settings.MEDIA_ROOT, storage_path)

            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # 直接写入文件（覆盖原文件）
            with open(full_path, 'wb+') as f:
                for chunk in new_image.chunks():
                    f.write(chunk)

            # 删除旧缩略图（如果存在）
            from core.thumbnail_generator import ThumbnailGenerator
            ThumbnailGenerator.delete_thumbnail(storage_path)

        except Exception as e:
            raise forms.ValidationError(f'图片替换失败: {str(e)}')

    def _save_new_image(self, image, date, folder):
        """保存新图片到指定目录，按日期组织"""
        try:
            # 使用直播日期组织文件夹
            year = date.strftime('%Y')
            month = date.strftime('%m')
            date_str = date.strftime('%Y-%m-%d')

            # 生成文件名
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                ext = '.jpg'
            filename = f"{date_str}{ext}"

            # 保存路径: media/{folder}/YYYY/MM/
            upload_path = f'{folder}/{year}/{month}/{filename}'

            # 如果文件已存在，先删除
            if default_storage.exists(upload_path):
                default_storage.delete(upload_path)

            # 保存文件
            saved_path = default_storage.save(upload_path, image)
            return f'/media/{saved_path}'
        except Exception as e:
            raise forms.ValidationError(f'图片保存失败: {str(e)}')

    def _generate_thumbnail(self, image_url):
        """触发缩略图生成"""
        if not image_url:
            return

        try:
            from core.thumbnail_generator import ThumbnailGenerator

            # 标准化路径
            rel_path = image_url.lstrip('/')
            if rel_path.startswith('media/'):
                rel_path = rel_path[len('media/'):]

            # 强制重新生成缩略图
            ThumbnailGenerator.generate_thumbnail(rel_path, force=True)
        except Exception as e:
            # 缩略图生成失败不应影响主流程
            print(f"缩略图生成失败: {image_url}, 错误: {e}")


@admin.register(Livestream)
class LivestreamAdmin(admin.ModelAdmin):
    """直播记录管理后台"""
    form = LivestreamAdminForm

    list_display = [
        'date',
        'title',
        'duration_formatted',
        'view_count',
        'danmaku_count',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'date']
    search_fields = ['title', 'summary', 'bvid']
    date_hierarchy = 'date'
    ordering = ['-date']
    change_list_template = 'admin/livestream_change_list.html'

    readonly_fields = ['cover_preview', 'danmaku_cloud_preview']

    fieldsets = (
        ('基础信息', {
            'fields': ('date', 'title', 'summary', 'live_moment', 'is_active', 'sort_order')
        }),
        ('B站视频信息', {
            'fields': ('bvid', 'duration_seconds', 'duration_formatted', 'parts')
        }),
        ('统计数据', {
            'fields': ('view_count', 'danmaku_count')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time')
        }),
        ('回放封面', {
            'fields': ('cover_image', 'cover_url', 'cover_preview'),
            'description': '支持两种方式：1.上传本地图片（推荐）2.输入图片URL'
        }),
        ('弹幕云图', {
            'fields': ('danmaku_cloud_image', 'danmaku_cloud_url', 'danmaku_cloud_preview'),
            'description': '支持两种方式：1.上传本地图片（推荐）2.输入图片URL'
        }),
    )

    def cover_preview(self, obj):
        """封面预览 - 使用缩略图"""
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:120px;max-width:200px;object-fit:cover;border-radius:8px;" />')
        return '-'
    cover_preview.short_description = '当前封面预览'

    def danmaku_cloud_preview(self, obj):
        """弹幕云图预览 - 使用缩略图"""
        if obj.danmaku_cloud_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.danmaku_cloud_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:120px;max-width:200px;object-fit:cover;border-radius:8px;" />')
        return '-'
    danmaku_cloud_preview.short_description = '当前云图预览'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-bv/', self.admin_site.admin_view(self.import_bv_view), name='import-bv-livestream'),
            path('select-cover/', self.admin_site.admin_view(self.select_cover_view), name='select-cover-livestream'),
        ]
        return custom_urls + urls

    def import_bv_view(self, request):
        """导入BV号视图"""
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"].strip()

                # 验证BV号格式
                if not re.match(r'^BV[a-zA-Z0-9]+$', bvid):
                    self.message_user(request, "❌ BV号格式不正确，应以BV开头", level=messages.ERROR)
                    return render(request, "admin/import_bv_livestream_form.html", {"form": form})

                try:
                    # 解析BV信息
                    bv_info = self._parse_bv_info(bvid)
                    
                    if not bv_info:
                        self.message_user(
                            request,
                            "⚠️ 未找到有效的直播记录。请检查视频分P标题是否包含日期格式（如：2019-12-10）",
                            level=messages.WARNING
                        )
                        return redirect("admin:livestream_livestream_changelist")

                    # 检查是否已存在该日期的记录且有封面
                    existing = Livestream.objects.filter(date=bv_info['date']).first()
                    
                    # 判断是否需要显示封面选择页面
                    need_cover_selection = (
                        existing and 
                        existing.cover_url and 
                        bv_info['new_cover_url']
                    )

                    if need_cover_selection:
                        # 构建现有封面的URL（用于显示）
                        existing_cover_url = self._get_cover_display_url(existing.cover_url)
                        
                        # 显示封面选择页面
                        return render(request, "admin/select_cover.html", {
                            'bvid': bvid,
                            'date': bv_info['date'].strftime('%Y-%m-%d'),
                            'title': bv_info['title'],
                            'summary': bv_info['summary'],
                            'total_parts': bv_info['total_parts'],
                            'total_duration_seconds': bv_info['total_duration_seconds'],
                            'duration_formatted': bv_info['duration_formatted'],
                            'new_cover_url': bv_info['new_cover_url'],
                            'existing_cover_url': existing_cover_url,
                        })
                    else:
                        # 直接完成导入
                        result = self._save_livestream(bv_info, existing, replace_cover=True)
                        
                        msg = f"✅ {result['date']} - {result['title']}"
                        if result.get('note'):
                            msg += f"（{result['note']}）"
                        if result.get('created'):
                            msg += " - 新建记录"
                        else:
                            msg += " - 更新记录"
                        self.message_user(request, msg, level=messages.SUCCESS)
                        
                        return redirect("admin:livestream_livestream_changelist")

                except BilibiliAPIError as e:
                    self.message_user(request, f"❌ B站API错误: {e.message}", level=messages.ERROR)
                except Exception as e:
                    self.message_user(request, f"❌ 导入失败: {str(e)}", level=messages.ERROR)
        else:
            form = BVImportForm()

        return render(request, "admin/import_bv_livestream_form.html", {"form": form})

    def select_cover_view(self, request):
        """封面选择视图"""
        if request.method == "POST":
            # 获取表单数据
            bvid = request.POST.get('bvid')
            date_str = request.POST.get('date')
            title = request.POST.get('title')
            summary = request.POST.get('summary')
            total_parts = int(request.POST.get('total_parts', 1))
            total_duration_seconds = int(request.POST.get('total_duration_seconds', 0))
            duration_formatted = request.POST.get('duration_formatted', '')
            new_cover_url = request.POST.get('new_cover_url', '')
            cover_choice = request.POST.get('cover_choice', 'replace')

            try:
                # 构建bv_info字典
                bv_info = {
                    'bvid': bvid,
                    'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                    'title': title,
                    'summary': summary,
                    'total_parts': total_parts,
                    'total_duration_seconds': total_duration_seconds,
                    'duration_formatted': duration_formatted,
                    'new_cover_url': new_cover_url,
                }

                # 检查现有记录
                existing = Livestream.objects.filter(date=bv_info['date']).first()

                # 根据用户选择决定是否替换封面
                replace_cover = (cover_choice == 'replace')

                # 保存记录
                result = self._save_livestream(bv_info, existing, replace_cover=replace_cover)

                # 显示结果消息
                cover_msg = "（替换封面）" if replace_cover and existing and existing.cover_url else ""
                msg = f"✅ {result['date']} - {result['title']}{cover_msg}"
                if result.get('note'):
                    msg += f"（{result['note']}）"
                if result.get('created'):
                    msg += " - 新建记录"
                else:
                    msg += " - 更新记录"
                self.message_user(request, msg, level=messages.SUCCESS)

                return redirect("admin:livestream_livestream_changelist")

            except Exception as e:
                self.message_user(request, f"❌ 保存失败: {str(e)}", level=messages.ERROR)
                return redirect("admin:livestream_livestream_changelist")

        # GET请求，重定向到导入页面
        return redirect("admin:import-bv-livestream")

    def _parse_bv_info(self, bvid: str) -> dict:
        """
        解析BV号信息，返回包含所有需要信息的字典
        
        Returns:
            dict: 包含以下键的字典
                - date: 直播日期
                - title: 直播标题
                - summary: 直播简介
                - total_parts: 分P数
                - total_duration_seconds: 总时长（秒）
                - duration_formatted: 格式化时长
                - new_cover_url: B站封面URL（用于显示）
        """
        api_client = BilibiliAPIClient(timeout=10, retry_times=3)

        # 获取视频信息
        video_info = api_client.get_video_info(bvid)

        # 获取分P信息
        pagelist = api_client.get_video_pagelist(bvid)

        if not pagelist:
            return None

        # 获取总封面URL
        new_cover_url = video_info.get_cover_url() if video_info else None

        # 定义日期匹配的正则表达式
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # YYYY年M月D日
        ]

        # 从第一个分P提取日期和标题
        first_part = pagelist[0]
        first_title = first_part.part

        performed_date = None
        date_match = None

        for pattern in date_patterns:
            date_match = re.search(pattern, first_title)
            if date_match:
                try:
                    year, month, day = map(int, date_match.groups())
                    performed_date = datetime(year, month, day).date()
                    break
                except ValueError:
                    continue

        if not performed_date:
            # 如果分P标题中没有日期，尝试使用视频发布时间
            if video_info:
                try:
                    pub_date = video_info.pub_date
                    performed_date = pub_date.date()
                    date_match = True
                except (AttributeError, ValueError):
                    pass

        if not performed_date:
            return None

        # 提取直播标题和简介
        live_title = first_title
        live_summary = f'{performed_date} 的精彩直播时刻'

        # 匹配 "直播录像" 后的所有内容
        summary_match = re.search(r'直播录像[\-:\s]*(.+)', first_title, re.IGNORECASE)
        if summary_match:
            extracted_summary = summary_match.group(1).strip('- ')
            if extracted_summary:
                live_summary = extracted_summary
            live_title = re.sub(r'(直播录像)[\-:\s]*.+', r'\1', first_title, flags=re.IGNORECASE)
            live_title = live_title.strip('- ')

        # 如果标题为空或无法解析，使用默认标题
        if not live_title or live_title == first_title:
            live_title = f"咻咻满-{performed_date}-直播录像"

        # 计算总时长
        total_parts = len(pagelist)
        total_duration_seconds = sum(p.duration for p in pagelist if hasattr(p, 'duration'))
        duration_formatted = self._format_duration(total_duration_seconds)

        return {
            'bvid': bvid,
            'date': performed_date,
            'title': live_title,
            'summary': live_summary,
            'total_parts': total_parts,
            'total_duration_seconds': total_duration_seconds,
            'duration_formatted': duration_formatted,
            'new_cover_url': new_cover_url,
        }

    def _save_livestream(self, bv_info: dict, existing: Livestream = None, replace_cover: bool = True) -> dict:
        """
        保存直播记录
        
        Args:
            bv_info: BV信息字典
            existing: 现有记录（如果有）
            replace_cover: 是否替换封面
            
        Returns:
            dict: 操作结果
        """
        # 下载封面（如果需要）
        cover_path = None
        if replace_cover and bv_info['new_cover_url']:
            cover_downloader = BilibiliCoverDownloader()
            
            # 确定文件名和路径
            date_str = bv_info['date'].strftime("%Y-%m-%d")
            year = bv_info['date'].strftime("%Y")
            month = bv_info['date'].strftime("%m")
            
            # 如果存在原封面，使用原文件名以保持文件名一致
            if existing and existing.cover_url:
                filename = self._extract_filename_from_cover_url(existing.cover_url)
                if not filename:
                    filename = f"{date_str}.jpg"
            else:
                filename = f"{date_str}.jpg"
            
            # 使用 download 方法并设置 check_exists=False 强制覆盖
            sub_path = f"covers/{year}/{month}"
            cover_path = cover_downloader.download(
                bv_info['new_cover_url'],
                sub_path,
                filename,
                check_exists=False  # 强制覆盖，确保下载新封面
            )

        if existing:
            # 更新现有记录
            if not existing.bvid:
                existing.bvid = bv_info['bvid']
                note_msg = f'补充BV号{"和多P" if bv_info["total_parts"] > 1 else ""}'
            else:
                note_msg = f'更新信息{"和多P" if bv_info["total_parts"] > 1 else ""}'

            existing.title = bv_info['title']
            existing.summary = bv_info['summary']
            existing.parts = bv_info['total_parts']
            existing.duration_seconds = bv_info['total_duration_seconds']
            existing.duration_formatted = bv_info['duration_formatted']
            
            # 根据replace_cover决定是否更新封面
            if replace_cover and cover_path:
                existing.cover_url = cover_path
            
            existing.save()
            
            return {
                'date': bv_info['date'].strftime('%Y-%m-%d'),
                'title': bv_info['title'],
                'note': f'{note_msg} ({bv_info["total_parts"]}P)' if bv_info['total_parts'] > 1 else note_msg,
                'created': False,
            }
        else:
            # 创建新记录
            livestream = Livestream.objects.create(
                date=bv_info['date'],
                title=bv_info['title'],
                summary=bv_info['summary'],
                bvid=bv_info['bvid'],
                parts=bv_info['total_parts'],
                duration_seconds=bv_info['total_duration_seconds'],
                duration_formatted=bv_info['duration_formatted'],
                cover_url=cover_path or '',
                is_active=True,
            )
            
            return {
                'date': bv_info['date'].strftime('%Y-%m-%d'),
                'title': bv_info['title'],
                'note': f'{bv_info["total_parts"]}P' if bv_info['total_parts'] > 1 else '单P',
                'created': True,
            }

    def _get_cover_display_url(self, cover_path: str) -> str:
        """
        获取封面用于显示的URL
        
        Args:
            cover_path: 数据库中存储的封面路径
            
        Returns:
            str: 可用于<img>标签的完整URL
        """
        if not cover_path:
            return ''
        
        # 如果已经是完整URL，直接返回
        if cover_path.startswith('http://') or cover_path.startswith('https://'):
            return cover_path
        
        # 处理相对路径
        # 确保路径以 /media/ 开头
        if cover_path.startswith('/'):
            return cover_path
        else:
            return f'/media/{cover_path}'

    def _extract_filename_from_cover_url(self, cover_url: str) -> str:
        """
        从封面URL/路径中提取文件名
        
        Args:
            cover_url: 封面的URL或路径
            
        Returns:
            str: 文件名（如：2019-12-10.jpg）
        """
        import os
        
        if not cover_url:
            return None
        
        # 移除URL参数（如果有）
        clean_url = cover_url.split('?')[0]
        
        # 提取文件名
        filename = os.path.basename(clean_url)
        
        # 如果文件名无效，返回None（让下载器使用默认文件名）
        if not filename or filename == '':
            return None
        
        return filename

    def _format_duration(self, seconds: int) -> str:
        """
        将秒数格式化为可读字符串（如：3h4m50s）
        """
        if seconds <= 0:
            return ''

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f'{hours}h')
        if minutes > 0:
            parts.append(f'{minutes}m')
        if secs > 0 or not parts:
            parts.append(f'{secs}s')

        return ''.join(parts)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
