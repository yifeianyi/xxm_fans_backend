"""
Admin 配置
"""
from django.contrib import admin, messages
from django.db.models import Sum
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django import forms
from urllib.parse import unquote, quote

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction

import os

from .models import Song, SongRecord, Style, SongStyle, Tag, SongTag, OriginalWork
from .forms import BVImportForm, SongRecordForm, SongStyleForm, SongTagForm, BatchSongStyleForm, BatchSongTagForm


@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    """曲风管理"""
    list_display = ['id', 'name', 'description']
    search_fields = ['name']
    change_list_template = 'admin/style_change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-tag-songs/', self.admin_site.admin_view(self.batch_tag_songs_view), name='batch_tag_songs_for_style'),
        ]
        return custom_urls + urls
    
    def batch_tag_songs_view(self, request):
        """曲风批量标记歌曲页面"""
        all_styles = Style.objects.all()
        all_songs = Song.objects.all().order_by('song_name')
        selected_style = None
        
        if request.method == 'POST':
            style_id = request.POST.get('style')
            song_ids = request.POST.getlist('songs')
            
            if not style_id or not song_ids:
                self.message_user(request, '请选择曲风和歌曲', level=messages.WARNING)
            else:
                style = Style.objects.get(id=style_id)
                songs = Song.objects.filter(id__in=song_ids)
                
                created_count = 0
                for song in songs:
                    song_style, created = SongStyle.objects.get_or_create(
                        song=song,
                        style=style
                    )
                    if created:
                        created_count += 1
                
                self.message_user(
                    request,
                    f'成功为 {songs.count()} 首歌曲添加了曲风「{style.name}」，共创建 {created_count} 个新关联。',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(reverse('admin:song_management_style_changelist'))
        
        context = dict(
            self.admin_site.each_context(request),
            all_styles=all_styles,
            all_songs=all_songs,
            selected_style=selected_style,
            title='批量标记歌曲 - 曲风',
            opts=self.model._meta,
        )
        return render(request, 'admin/batch_tag_songs_for_style.html', context)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """标签管理"""
    list_display = ['id', 'name']
    search_fields = ['name']
    change_list_template = 'admin/tag_change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-tag-songs/', self.admin_site.admin_view(self.batch_tag_songs_view), name='batch_tag_songs_for_tag'),
        ]
        return custom_urls + urls
    
    def batch_tag_songs_view(self, request):
        """标签批量标记歌曲页面"""
        all_tags = Tag.objects.all()
        all_songs = Song.objects.all().order_by('song_name')
        selected_tag = None
        
        if request.method == 'POST':
            tag_id = request.POST.get('tag')
            song_ids = request.POST.getlist('songs')
            
            if not tag_id or not song_ids:
                self.message_user(request, '请选择标签和歌曲', level=messages.WARNING)
            else:
                tag = Tag.objects.get(id=tag_id)
                songs = Song.objects.filter(id__in=song_ids)
                
                created_count = 0
                for song in songs:
                    song_tag, created = SongTag.objects.get_or_create(
                        song=song,
                        tag=tag
                    )
                    if created:
                        created_count += 1
                
                self.message_user(
                    request,
                    f'成功为 {songs.count()} 首歌曲添加了标签「{tag.name}」，共创建 {created_count} 个新关联。',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(reverse('admin:song_management_tag_changelist'))
        
        context = dict(
            self.admin_site.each_context(request),
            all_tags=all_tags,
            all_songs=all_songs,
            selected_tag=selected_tag,
            title='批量标记歌曲 - 标签',
            opts=self.model._meta,
        )
        return render(request, 'admin/batch_tag_songs_for_tag.html', context)


@admin.register(SongStyle)
class SongStyleAdmin(admin.ModelAdmin):
    """歌曲曲风关联管理"""
    form = SongStyleForm
    list_display = ['song', 'style']
    list_filter = ['style']
    search_fields = ['song__song_name', 'style__name']
    actions = ['batch_add_song_styles']
    change_list_template = 'admin/songstyle_change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-add/', self.admin_site.admin_view(self.batch_add_view), name='batch_add_song_styles'),
        ]
        return custom_urls + urls
    
    def batch_add_song_styles(self, request, queryset):
        """批量添加歌曲曲风的action"""
        return HttpResponseRedirect(reverse('admin:batch_add_song_styles'))
    
    batch_add_song_styles.short_description = "批量添加歌曲曲风"
    
    def batch_add_view(self, request):
        """批量添加歌曲曲风的视图 - 新布局"""
        if request.method == 'POST':
            # 添加调试信息
            self.message_user(request, f'POST数据: {request.POST}', messages.INFO)
            
            form = BatchSongStyleForm(request.POST)
            # 重要：确保字段的queryset被正确设置
            form.fields['available_songs'].queryset = Song.objects.all().order_by('song_name')
            form.fields['selected_songs'].queryset = Song.objects.all().order_by('song_name')
            
            if form.is_valid():
                selected_songs = form.cleaned_data['selected_songs']
                style = form.cleaned_data['style']
                
                # 添加调试信息
                self.message_user(request, f'选中的歌曲数量: {selected_songs.count()}', messages.INFO)
                self.message_user(request, f'选中的曲风: {style.name}', messages.INFO)
                
                if not selected_songs or not style:
                    self.message_user(request, '请选择歌曲和曲风', messages.WARNING)
                    return HttpResponseRedirect(reverse('admin:batch_add_song_styles'))
                
                created_count = 0
                for song in selected_songs:
                    _, created = SongStyle.objects.get_or_create(
                        song=song,
                        style=style
                    )
                    if created:
                        created_count += 1
                
                self.message_user(
                    request,
                    f'成功为 {selected_songs.count()} 首歌曲添加了曲风「{style.name}」，共创建 {created_count} 个新关联。',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(reverse('admin:song_management_songstyle_changelist'))
            else:
                # 添加表单错误信息
                self.message_user(request, f'表单验证失败: {form.errors}', messages.ERROR)
        else:
            # 处理搜索功能
            search_query = request.GET.get('song_search', '')
            form = BatchSongStyleForm()
            
            # 添加调试信息
            initial_count = Song.objects.all().order_by('song_name').count()
            self.message_user(request, f'初始化时歌曲总数: {initial_count}', messages.INFO)
            
            if search_query:
                # 根据搜索词过滤歌曲 - 显示所有匹配的搜索结果
                filtered_songs = Song.objects.filter(
                    song_name__icontains=search_query
                ).order_by('song_name')
                form.fields['available_songs'].queryset = filtered_songs
                self.message_user(request, f'搜索"{search_query}"后找到 {filtered_songs.count()} 首歌曲', messages.INFO)
            else:
                # 显示所有歌曲，按名称排序
                all_songs = Song.objects.all().order_by('song_name')
                form.fields['available_songs'].queryset = all_songs
                self.message_user(request, f'未搜索时显示 {all_songs.count()} 首歌曲', messages.INFO)
        
        context = dict(
            self.admin_site.each_context(request),
            form=form,
            title='批量添加歌曲曲风',
            opts=self.model._meta,
        )
        return render(request, 'admin/batch_add_song_styles.html', context)


@admin.register(SongTag)
class SongTagAdmin(admin.ModelAdmin):
    """歌曲标签关联管理"""
    form = SongTagForm
    list_display = ['song', 'tag']
    list_filter = ['tag']
    search_fields = ['song__song_name', 'tag__name']
    actions = ['batch_add_song_tags']
    change_list_template = 'admin/songtag_change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-add/', self.admin_site.admin_view(self.batch_add_view), name='batch_add_song_tags'),
        ]
        return custom_urls + urls
    
    def batch_add_song_tags(self, request, queryset):
        """批量添加歌曲标签的action"""
        return HttpResponseRedirect(reverse('admin:batch_add_song_tags'))
    
    batch_add_song_tags.short_description = "批量添加歌曲标签"
    
    def batch_add_view(self, request):
        """批量添加歌曲标签的视图 - 新布局"""
        if request.method == 'POST':
            # 添加调试信息
            self.message_user(request, f'POST数据: {request.POST}', messages.INFO)
            
            form = BatchSongTagForm(request.POST)
            # 重要：确保字段的queryset被正确设置
            form.fields['available_songs'].queryset = Song.objects.all().order_by('song_name')
            form.fields['selected_songs'].queryset = Song.objects.all().order_by('song_name')
            
            if form.is_valid():
                selected_songs = form.cleaned_data['selected_songs']
                tag = form.cleaned_data['tag']
                
                # 添加调试信息
                self.message_user(request, f'选中的歌曲数量: {selected_songs.count()}', messages.INFO)
                self.message_user(request, f'选中的标签: {tag.name}', messages.INFO)
                
                if not selected_songs or not tag:
                    self.message_user(request, '请选择歌曲和标签', messages.WARNING)
                    return HttpResponseRedirect(reverse('admin:batch_add_song_tags'))
                
                created_count = 0
                for song in selected_songs:
                    _, created = SongTag.objects.get_or_create(
                        song=song,
                        tag=tag
                    )
                    if created:
                        created_count += 1
                
                self.message_user(
                    request,
                    f'成功为 {selected_songs.count()} 首歌曲添加了标签「{tag.name}」，共创建 {created_count} 个新关联。',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(reverse('admin:song_management_songtag_changelist'))
            else:
                # 添加表单错误信息
                self.message_user(request, f'表单验证失败: {form.errors}', messages.ERROR)
        else:
            # 处理搜索功能
            search_query = request.GET.get('song_search', '')
            form = BatchSongTagForm()
            
            # 添加调试信息
            initial_count = Song.objects.all().order_by('song_name').count()
            self.message_user(request, f'初始化时歌曲总数: {initial_count}', messages.INFO)
            
            if search_query:
                # 根据搜索词过滤歌曲 - 显示所有匹配的搜索结果
                filtered_songs = Song.objects.filter(
                    song_name__icontains=search_query
                ).order_by('song_name')
                form.fields['available_songs'].queryset = filtered_songs
                self.message_user(request, f'搜索"{search_query}"后找到 {filtered_songs.count()} 首歌曲', messages.INFO)
            else:
                # 显示所有歌曲，按名称排序
                all_songs = Song.objects.all().order_by('song_name')
                form.fields['available_songs'].queryset = all_songs
                self.message_user(request, f'未搜索时显示 {all_songs.count()} 首歌曲', messages.INFO)
        
        context = dict(
            self.admin_site.each_context(request),
            form=form,
            title='批量添加歌曲标签',
            opts=self.model._meta,
        )
        return render(request, 'admin/batch_add_song_tags.html', context)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """歌曲管理"""
    list_display = ['song_name_display', 'language_display', 'singer_display', 'styles_display', 'last_performed_display', 'perform_count_display', 'view_records']
    list_filter = ['language', 'last_performed']
    search_fields = ["song_name", "perform_count", "singer"]
    actions = ['merge_songs_action', 'set_language_action', "split_song_action", "batch_add_styles_action", "batch_add_tags_action"]
    fields = ["song_name", "singer", "language"]
    list_per_page = 25
    ordering = ['song_name']

    class Media:
        css = {
            'all': ('admin/css/collapsible.css',)
        }
        js = ('admin/js/collapsible.js',)
    
    @admin.display(description="歌手", ordering="singer")
    def singer_display(self, obj):
        return obj.singer

    @admin.display(description="语言", ordering="language")
    def language_display(self, obj):
        return obj.language

    @admin.display(description="首次演唱时间", ordering="first_perform")
    def first_performed_display(self, obj):
        return obj.first_perform

    @admin.display(description="最近演唱时间", ordering="last_performed")
    def last_performed_display(self, obj):
        return obj.last_performed

    @admin.display(description="歌名", ordering="song_name")
    def song_name_display(self, obj):
        return obj.song_name

    @admin.display(description="演唱次数", ordering="perform_count")
    def perform_count_display(self, obj):
        return obj.perform_count
    
    @admin.display(description="曲风")
    def styles_display(self, obj):
        styles = SongStyle.objects.filter(song=obj).select_related('style')
        style_names = [song_style.style.name for song_style in styles]
        return ', '.join(style_names) if style_names else '-'
    
    @admin.display(description="演唱记录")
    def view_records(self, obj):
        records = SongRecord.objects.filter(song=obj).order_by('-performed_at')
        if not records:
            return "暂无记录"

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
    
    # 路由设置
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("merge_songs/", self.admin_site.admin_view(self.merge_songs_view), name="merge_songs"),
            path('split_song/<int:song_id>/', self.admin_site.admin_view(self.split_song_view), name='split_song'),
        ]
        return custom_urls + urls
    
    # 合并按钮
    def merge_songs_action(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        if len(selected) < 2:
            self.message_user(request, "至少选择两个才能合并", level=messages.WARNING)
            return None
        
        current_path = request.get_full_path()
        next_url = quote(current_path)
        return HttpResponseRedirect(f"./merge_songs/?ids={','.join(selected)}&next={next_url}")
    
    # 拆分按钮
    def split_song_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "请只选择一首歌进行拆分")
            return
        song_id = queryset.first().id
        return redirect(f'./split_song/{song_id}/')
    
    # 批量标记语言
    def set_language_action(self, request, queryset):
        class LanguageForm(forms.Form):
            language = forms.CharField(label="语言", max_length=50)
        
        if 'apply' in request.POST:
            form = LanguageForm(request.POST)
            if form.is_valid():
                language = form.cleaned_data['language']
                count = queryset.update(language=language)
                self.message_user(request, f"已成功批量标记 {count} 首歌为{language}!")
                return None
        else:
            form = LanguageForm()
        return render(request, 'admin/batch_set_language.html', {'form': form, 'songs': queryset})

    # 批量添加曲风标签
    def batch_add_styles_action(self, request, queryset):
        class BatchAddStylesForm(forms.Form):
            styles = forms.ModelMultipleChoiceField(
                queryset=Style.objects.all(),
                widget=forms.CheckboxSelectMultiple,
                required=True,
                label="选择要添加的曲风"
            )
        
        if 'apply' in request.POST:
            form = BatchAddStylesForm(request.POST)
            if form.is_valid():
                styles = form.cleaned_data['styles']
                count = 0
                for song in queryset:
                    for style in styles:
                        # 使用get_or_create避免重复添加
                        song_style, created = SongStyle.objects.get_or_create(
                            song=song,
                            style=style
                        )
                        if created:
                            count += 1
                self.message_user(request, f"已成功为 {queryset.count()} 首歌添加了 {count} 个曲风标签!")
                return None
        else:
            form = BatchAddStylesForm()
            # 如果只选择了一首歌曲，过滤掉已关联的曲风
            if queryset.count() == 1:
                song = queryset.first()
                existing_style_ids = SongStyle.objects.filter(song=song).values_list('style', flat=True)
                form.fields['styles'].queryset = Style.objects.exclude(id__in=existing_style_ids)
        return render(request, 'admin/batch_add_styles.html', {'form': form, 'songs': queryset, 'title': '批量添加曲风标签'})

    # 批量添加标签
    def batch_add_tags_action(self, request, queryset):
        class BatchAddTagsForm(forms.Form):
            tags = forms.ModelMultipleChoiceField(
                queryset=Tag.objects.all(),
                widget=forms.CheckboxSelectMultiple,
                required=True,
                label="选择要添加的标签"
            )
        
        if 'apply' in request.POST:
            form = BatchAddTagsForm(request.POST)
            if form.is_valid():
                tags = form.cleaned_data['tags']
                count = 0
                for song in queryset:
                    for tag in tags:
                        # 使用get_or_create避免重复添加
                        song_tag, created = SongTag.objects.get_or_create(
                            song=song,
                            tag=tag
                        )
                        if created:
                            count += 1
                self.message_user(request, f"已成功为 {queryset.count()} 首歌添加了 {count} 个标签!")
                return None
        else:
            form = BatchAddTagsForm()
            # 如果只选择了一首歌曲，过滤掉已关联的标签
            if queryset.count() == 1:
                song = queryset.first()
                existing_tag_ids = SongTag.objects.filter(song=song).values_list('tag', flat=True)
                form.fields['tags'].queryset = Tag.objects.exclude(id__in=existing_tag_ids)
        return render(request, 'admin/batch_add_tags.html', {'form': form, 'songs': queryset, 'title': '批量添加标签'})

    merge_songs_action.short_description = "合并选中的歌曲"
    set_language_action.short_description = "批量标记语言"
    split_song_action.short_description = "拆分选中的歌曲"
    batch_add_styles_action.short_description = "批量添加曲风标签"
    batch_add_tags_action.short_description = "批量添加标签"

    ##########################
    # 合并视图
    ##########################
    def merge_songs_view(self, request):
        ids = request.GET.get("ids", "") or request.POST.get("ids", "")
        id_list = ids.split(",")
        selected_songs = Song.objects.filter(id__in=id_list)

        if request.method == "POST":
            master_id = request.POST.get("master_id")
            if not master_id:
                self.message_user(request, "必须选择一个主项", level=messages.ERROR)
                return redirect(request.path + f"?ids={ids}")

            master_song = Song.objects.get(id=master_id)
            other_songs = selected_songs.exclude(id=master_id)

            for song in other_songs:
                SongRecord.objects.filter(song=song).update(song=master_song)
            total_add = other_songs.aggregate(Sum('perform_count'))['perform_count__sum'] or 0
            master_song.perform_count += total_add

            # 从演唱记录中获取最早的演唱时间
            earliest_record = master_song.records.order_by('performed_at').first()
            master_song.first_perform = earliest_record.performed_at if earliest_record else None

            # 从演唱记录中获取最新的演唱时间
            latest_record = master_song.records.order_by('-performed_at').first()
            master_song.last_performed = latest_record.performed_at if latest_record else None

            master_song.save()
            other_songs.delete()

            self.message_user(request, f"成功将 {len(id_list)-1} 项合并到主项《{master_song.song_name}》。")
            next_url = request.GET.get('next') or request.POST.get('next') or reverse('admin:song_management_song_changelist')
            next_url = unquote(next_url)
            return HttpResponseRedirect(next_url)

        context = dict(
            self.admin_site.each_context(request),
            songs=selected_songs,
            ids=ids,
            next=request.GET.get('next', '') 
        )
        return TemplateResponse(request, "admin/merge_songs.html", context)

    ##########################
    # 拆分视图
    ##########################
    class SplitSongForm(forms.Form):
        records = forms.ModelMultipleChoiceField(
            queryset=SongRecord.objects.none(),
            widget=forms.CheckboxSelectMultiple,
            required=True,
            label="选择要拆分的演唱记录"
        )
        
    def split_song_view(self, request, song_id):
        song = Song.objects.get(id=song_id)
        queryset = SongRecord.objects.filter(song=song).order_by('-performed_at')
        
        if request.method == 'POST':
            form = self.SplitSongForm(request.POST)
            form.fields['records'].queryset = queryset
            if form.is_valid():
                selected_records = form.cleaned_data['records']
                with transaction.atomic():
                    # 创建新歌曲
                    new_song = Song.objects.create(
                        song_name=song.song_name,
                        singer=None,
                        language=song.language
                    )

                    # 将选中的演唱记录转移到新歌曲
                    for record in selected_records:
                        record.song = new_song
                        record.save()

                    # 更新新歌曲的统计字段
                    new_song.perform_count = new_song.records.count()
                    latest_record = new_song.records.order_by('-performed_at').first()
                    new_song.last_performed = latest_record.performed_at if latest_record else None
                    earliest_record = new_song.records.order_by('performed_at').first()
                    new_song.first_perform = earliest_record.performed_at if earliest_record else None
                    new_song.save()

                    # 更新原歌曲的统计字段
                    song.perform_count = song.records.count()
                    latest_record = song.records.order_by('-performed_at').first()
                    song.last_performed = latest_record.performed_at if latest_record else None
                    earliest_record = song.records.order_by('performed_at').first()
                    song.first_perform = earliest_record.performed_at if earliest_record else None
                    song.save()

                self.message_user(request, f"已成功拆分 {len(selected_records)} 条演唱记录")
                return redirect('admin:song_management_song_changelist')
        else:
            form = self.SplitSongForm()
            form.fields['records'].queryset = queryset

        return render(request, 'admin/split_song.html', {
            'song': song,
            'form': form,
            'opts': self.model._meta,
        })


@admin.register(SongRecord)
class SongRecordAdmin(admin.ModelAdmin):
    """演唱记录管理"""
    form = SongRecordForm
    list_display = ("song", "performed_at", "url", "cover_url", "cover_thumb", "notes")
    change_list_template = 'admin/songrecord_change_list.html'
    search_fields = ["song__song_name", "notes"]
    list_filter = ["performed_at", "song__song_name"]
    autocomplete_fields = ("song",)

    def get_fields(self, request, obj=None):
        fields = ["song", "performed_at", "url", "notes"]
        if obj:
            # 编辑模式：显示所有字段
            return fields + ["cover_image", "cover_url", "cover_thumb_large"]
        else:
            # 新增模式
            return fields + ["cover_image", "cover_url"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["cover_thumb", "cover_thumb_large"]
        return ["cover_thumb"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-bv/", self.admin_site.admin_view(self.import_bv_view), name="import-bv-songrecord"),
        ]
        return my_urls + urls

    # 缩略图显示（列表页）
    def cover_thumb(self, obj):
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:48px;max-width:80px;object-fit:cover;" />')
        return "-"
    cover_thumb.short_description = "封面缩略图"

    # 大缩略图显示（编辑页）
    def cover_thumb_large(self, obj):
        if obj.cover_url:
            from core.thumbnail_generator import ThumbnailGenerator
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover_url)
            return mark_safe(f'<img src="{thumb_url}" style="height:150px;max-width:250px;object-fit:cover;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);" />')
        return '<span style="color:#999;">暂无封面</span>'
    cover_thumb_large.short_description = '当前封面预览'

    # 导入BV演唱记录的视图
    def import_bv_view(self, request):
        if request.method == "POST":
            form = BVImportForm(request.POST)
            if form.is_valid():
                bvid = form.cleaned_data["bvid"]
                selected_song_id = request.POST.get("selected_song_id")
                pending_parts_json = request.POST.get("pending_parts")
                all_results_count = int(request.POST.get("all_results_count", 0))

                # 解析待处理分P信息
                pending_parts = None
                if pending_parts_json:
                    import json
                    try:
                        pending_parts = json.loads(pending_parts_json)
                    except json.JSONDecodeError:
                        pending_parts = None

                import json
                conflict_info = None
                while True:
                    from .services.bilibili_import_service import BilibiliImporter
                    importer = BilibiliImporter()

                    result_list, remaining_parts, conflict_info = importer.import_bv_song(
                        bvid,
                        selected_song_id=selected_song_id,
                        pending_parts=pending_parts
                    )

                    # 展平 result_list（避免嵌套）
                    flattened_result_list = []
                    for item in result_list:
                        if isinstance(item, list):
                            flattened_result_list.extend(item)
                        else:
                            flattened_result_list.append(item)
                    result_list = flattened_result_list

                    all_results_count += len(result_list)

                    # 显示导入结果
                    for result in result_list:
                        if not isinstance(result, dict):
                            self.message_user(request, f"⚠️ 导入结果格式异常: {result}", level=messages.WARNING)
                            continue

                        song_name = result.get('song_name', '未知歌曲')
                        msg = f"✅ {song_name}"
                        if result.get("note"):
                            msg += f"（{result['note']}）"
                        if result.get("created_song"):
                            msg += "，🎵 新建歌曲"
                        if result.get("cover_url"):
                            msg += "，🖼️ 封面已下载"
                        self.message_user(request, msg, level=messages.SUCCESS)

                    # 如果有错误信息（API错误等）
                    if conflict_info and conflict_info.get("error"):
                        self.message_user(request, f"❌ 导入失败: {conflict_info['error']}", level=messages.ERROR)
                        return redirect("admin:song_management_songrecord_changelist")

                    # 如果有冲突
                    if conflict_info:
                        # 判断是不是第一次进入冲突处理
                        if not selected_song_id:
                            # 首次进入 -> 返回选择页面
                            remaining_parts_for_template = conflict_info["remaining_parts"]
                            if isinstance(remaining_parts_for_template, str):
                                try:
                                    remaining_parts_for_template = json.loads(remaining_parts_for_template)
                                except json.JSONDecodeError:
                                    pass

                            return render(request, "admin/select_song.html", {
                                "song_name": conflict_info["song_name"],
                                "candidates": conflict_info["candidates"],
                                "bvid": bvid,
                                "pending_parts": json.dumps(remaining_parts_for_template) if not isinstance(remaining_parts_for_template, str) else remaining_parts_for_template,
                                "current_part": conflict_info["current_part"],
                                "all_results_count": all_results_count,
                            })
                        else:
                            # 用户已经选择了歌曲 -> 清空 selected_song_id，用于继续后续 pending_parts
                            pending_parts = conflict_info["remaining_parts"]
                            selected_song_id = None
                            continue

                    # 没有剩余 -> 完成
                    if not remaining_parts:
                        if all_results_count == 0:
                            self.message_user(request, f"⚠️ BV导入完成，但未找到有效的演唱记录。请检查视频分P标题是否包含日期格式（如：2024年1月1日）", level=messages.WARNING)
                        else:
                            self.message_user(request, f"🎉 BV导入完成！共处理 {all_results_count} 条记录", level=messages.SUCCESS)
                        return redirect("admin:song_management_songrecord_changelist")

                    # 没有冲突但还有剩余，继续循环
                    pending_parts = remaining_parts
                    selected_song_id = None
        else:
            form = BVImportForm()
        return render(request, "admin/import_bv_form.html", {"form": form})


@admin.register(OriginalWork)
class OriginalWorkAdmin(admin.ModelAdmin):
    """原唱作品管理"""
    list_display = ['title', 'release_date', 'featured', 'netease_id_display', 'bilibili_bvid_display', 'cover_thumb']
    list_filter = ['featured', 'release_date']
    search_fields = ['title', 'description']
    list_editable = ['featured']
    ordering = ['-featured', '-release_date']
    readonly_fields = ['cover_thumb', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'release_date', 'description', 'featured')
        }),
        ('播放链接', {
            'fields': ('netease_id', 'bilibili_bvid')
        }),
        ('封面', {
            'fields': ('cover', 'cover_thumb')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description="网易云音乐")
    def netease_id_display(self, obj):
        if obj.netease_id:
            return format_html(
                '<a href="https://music.163.com/#/song?id={}" target="_blank" style="color:#79aec8;">{}</a>',
                obj.netease_id,
                obj.netease_id
            )
        return '-'

    @admin.display(description="B站视频")
    def bilibili_bvid_display(self, obj):
        if obj.bilibili_bvid:
            return format_html(
                '<a href="https://www.bilibili.com/video/{}" target="_blank" style="color:#79aec8;">{}</a>',
                obj.bilibili_bvid,
                obj.bilibili_bvid
            )
        return '-'

    @admin.display(description="封面")
    def cover_thumb(self, obj):
        if obj.cover:
            # 使用缩略图而不是原图
            from core.thumbnail_generator import ThumbnailGenerator
            # covers/original/ 路径下的图片
            thumb_url = ThumbnailGenerator.get_thumbnail_url(obj.cover.url)
            return mark_safe(f'<img src="{thumb_url}" style="height:48px;max-width:80px;object-fit:cover;" />')
        return '-'
    cover_thumb.short_description = "封面"