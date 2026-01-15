# XXM Fans Home 后端重构方案 v2.0

## 文档信息

- **版本**: 2.0
- **创建日期**: 2026-01-12
- **项目名称**: XXM Fans Home 后端
- **技术栈**: Django 5.2.3 + Django REST Framework 3.15.2
- **数据库**: SQLite (多数据库架构)

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 项目现状分析](#2-项目现状分析)
- [3. 核心问题识别](#3-核心问题识别)
- [4. 重构目标](#4-重构目标)
- [5. 重构方案设计](#5-重构方案设计)
- [6. 实施计划](#6-实施计划)
- [7. 风险评估与缓解](#7-风险评估与缓解)
- [8. 预期收益](#8-预期收益)

---

## 1. 执行摘要

### 1.1 项目概述

XXM Fans Home 是一个基于 Django 的音乐粉丝网站后端系统，提供音乐管理、粉丝二创作品管理以及创新的模板化歌单管理 API。项目已完成 Phase 1 重构，实现了 VIEW_API 分离和 songlist 独立表架构。

### 1.2 重构必要性

当前项目虽然已完成了初步重构，但仍存在以下关键问题：

1. **main 应用职责过重**：包含歌曲管理、数据分析、推荐语、网站设置等多个不相关模块
2. **缺少服务层抽象**：业务逻辑直接写在 views 中，难以复用和测试
3. **admin.py 文件过大**：855 行代码包含 12 个 Admin 类
4. **工具脚本分散**：多个脚本功能重叠，缺乏统一管理
5. **缓存逻辑重复**：在多个函数中重复相同的缓存处理代码
6. **配置文件混乱**：settings.py 存在重复配置和注释不符问题

### 1.3 重构核心价值

通过本次重构，项目将实现：

- **高扩展性**：模块化设计，易于添加新功能和新歌手
- **高可读性**：清晰的代码结构和命名规范
- **高可维护性**：职责分离，降低维护成本
- **高可测试性**：服务层抽象，便于单元测试

---

## 2. 项目现状分析

### 2.1 当前应用架构

```
xxm_fans_backend/
├── main/                    # 主应用（多功能集合）
│   ├── models.py           # 13个模型
│   ├── views.py            # API视图
│   ├── admin.py            # 855行，12个Admin类
│   ├── serializers.py      # 序列化器
│   └── management/         # 管理命令
│
├── fansDIY/                 # 粉丝二创应用
│   ├── models.py           # Collection, Work
│   ├── views.py
│   └── admin.py
│
├── songlist/                # 模板化歌单应用（独立数据库）
│   ├── models.py           # 动态模型创建
│   ├── views.py            # 配置驱动API
│   └── admin.py
│
└── xxm_fans_home/           # 项目配置
    ├── settings.py         # 多数据库配置
    ├── db_routers.py       # 数据库路由
    └── urls.py
```

### 2.2 数据库架构

| 数据库 | 文件名 | 用途 | 包含模型 |
|--------|--------|------|----------|
| default | db.sqlite3 | 核心业务 | Songs, SongRecord, Style, Tag, Recommendation, SiteSettings, Collection, Work |
| view_data_db | view_data.sqlite3 | 数据分析 | WorkStatic, WorkMetricsHour, CrawlSession |
| songlist_db | songlist.sqlite3 | 模板化歌单 | YouyouSong, YouyouSiteSetting, BingjieSong, BingjieSiteSetting |

### 2.3 代码质量指标

| 指标 | 当前值 | 目标值 |
|------|--------|--------|
| Django 应用数量 | 3 | 6 |
| main 应用模型数量 | 13 | 2 |
| admin.py 最大行数 | 855 | <200 |
| 服务层覆盖率 | 0% | >80% |
| 单元测试覆盖率 | <10% | >60% |
| 代码重复率 | ~15% | <5% |

---

## 3. 核心问题识别

### 3.1 架构层面问题

#### 问题 1：main 应用职责过重（🔴 严重）

**问题描述：**
`main` 应用是一个多功能集合，包含了多个不相关的功能模块，违反单一职责原则。

**包含的模块：**
1. 歌曲管理模块（Songs, SongRecord, Style, Tag, SongStyle, SongTag）
2. 排行榜功能（top_songs_api）
3. 推荐语管理（Recommendation）
4. 网站设置（SiteSettings）
5. 数据分析模块（WorkStatic, WorkMetricsHour, CrawlSession）
6. 视频信息模块（ViewBaseMess, ViewRealTimeInformation）- 与 WorkStatic 功能重复

**影响：**
- admin.py 文件过大（855 行）
- 代码审查困难
- 多人协作容易冲突
- 测试复杂度高

#### 问题 2：缺少服务层抽象（🔴 严重）

**问题描述：**
业务逻辑直接写在 views 中，难以复用和测试。

**示例：**
```python
# main/views.py - 业务逻辑直接在视图中
@api_view(['GET'])
def top_songs_api(request):
    range_map = {'all': None, '1m': 30, '3m': 90, ...}
    range_key = request.GET.get('range', 'all')
    days = range_map.get(range_key, None)
    limit = int(request.GET.get('limit', 10))
    qs = Songs.objects.all()
    if days:
        since = datetime.now().date() - timedelta(days=days)
        qs = qs.filter(records__performed_at__gte=since)
    qs = qs.annotate(recent_count=Count('records')).order_by('-recent_count', '-last_performed')[:limit]
    # ... 更多业务逻辑
```

**影响：**
- 业务逻辑难以复用
- 单元测试困难
- 代码耦合度高

#### 问题 3：songlist 动态模型缺乏扩展性（🟡 中等）

**问题描述：**
songlist 使用动态模型创建，虽然实现了一行配置添加歌手，但缺乏灵活性。

**当前实现：**
```python
# songlist/models.py
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
}

def create_artist_models(artist_key, artist_name):
    # 动态创建模型
    song_model = type(f'{class_name}Song', (models.Model,), song_attrs)
    setting_model = type(f'{class_name}SiteSetting', (models.Model,), setting_attrs)
    return song_model, setting_model
```

**局限性：**
- 难以为不同歌手添加自定义字段
- 难以实现复杂的业务逻辑
- 迁移文件管理复杂

### 3.2 代码质量问题

#### 问题 4：admin.py 文件过大（🟡 中等）

**问题描述：**
`main/admin.py` 文件达到 855 行，包含 12 个 Admin 类。

**包含的 Admin 类：**
1. SiteSettingsAdmin
2. StyleAdmin
3. TagAdmin
4. SongStyleAdmin
5. SongTagAdmin
6. RecommendationAdmin
7. SongsAdmin
8. SongRecordAdmin
9. WorkStaticAdmin
10. WorkMetricsHourAdmin
11. CrawlSessionAdmin
12. ViewBaseMessAdmin

#### 问题 5：缓存处理逻辑重复（🟡 中等）

**问题描述：**
在 6 个函数中重复相同的缓存处理逻辑。

**重复代码：**
```python
# 在 song_list_api, song_record_list_api, style_list_api,
# tag_list_api, recommendation_api 中重复出现
try:
    cache.set(cache_key, data, 600)
except Exception as e:
    logger.warning(f"Cache set failed: {e}")
```

#### 问题 6：工具脚本功能重复（🟢 低）

**问题描述：**
多个脚本功能高度重叠：
- `download_img.py` - 下载图片
- `download_covers.py` - 下载封面
- `download_covers_and_update_json.py` - 下载封面并更新 JSON
- `cover_downloader.py` - 封面下载器

#### 问题 7：配置文件混乱（🟢 低）

**问题描述：**
`settings.py` 中存在重复配置。

```python
# settings.py:149-152
DEFAULT_CHARSET = 'utf-8'

# 字符编码设置
DEFAULT_CHARSET = 'utf-8'  # 重复定义
FILE_CHARSET = 'utf-8'
```

---

## 4. 重构目标

### 4.1 主要目标

1. **职责分离**：将 main 应用拆分为多个职责单一的应用
2. **引入服务层**：业务逻辑与数据访问分离
3. **代码模块化**：拆分大文件，提高可读性
4. **统一规范**：标准化 API 响应、异常处理、缓存逻辑
5. **提高可测试性**：服务层抽象，便于单元测试

### 4.2 量化指标

| 指标 | 当前 | 目标 |
|------|------|------|
| Django 应用数量 | 3 | 6 |
| main 应用模型数量 | 13 | 0（main 应用将被删除） |
| admin.py 最大行数 | 855 | <200 |
| 服务层覆盖率 | 0% | >80% |
| 单元测试覆盖率 | <10% | >60% |
| 代码重复率 | ~15% | <5% |
| 平均函数行数 | ~50 | <30 |

---

## 5. 重构方案设计

### 5.1 新应用架构

```
重构后架构：
├── song_management/       # 歌曲管理应用（核心业务）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── song.py       # Song, SongRecord
│   │   ├── style.py      # Style, SongStyle
│   │   └── tag.py        # Tag, SongTag
│   ├── services/
│   │   ├── __init__.py
│   │   ├── song_service.py
│   │   └── ranking_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── serializers.py
│   └── admin/
│       ├── __init__.py
│       ├── song_admin.py
│       ├── style_admin.py
│       └── tag_admin.py
│
├── data_analytics/        # 数据分析应用（独立数据库）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── work_static.py
│   │   ├── work_metrics_hour.py
│   │   └── crawl_session.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── analytics_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── serializers.py
│   └── admin/
│       ├── __init__.py
│       └── analytics_admin.py
│
├── site_settings/         # 网站设置应用
│   ├── models/
│   │   ├── __init__.py
│   │   └── settings.py    # SiteSettings, Recommendation
│   ├── services/
│   │   ├── __init__.py
│   │   └── settings_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── serializers.py
│   └── admin/
│       ├── __init__.py
│       └── settings_admin.py
│
├── fansDIY/              # 粉丝二创应用（保持不变）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── collection.py
│   │   └── work.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── diy_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── views.py
│   │   └── serializers.py
│   └── admin/
│       ├── __init__.py
│       └── diy_admin.py
│
├── songlist/             # 模板化歌单应用（独立数据库，保持不变）
│   ├── models.py         # 动态模型创建
│   ├── views.py
│   └── admin.py
│
├── core/                 # 核心模块（新增）
│   ├── __init__.py
│   ├── cache.py          # 缓存装饰器
│   ├── exceptions.py     # 自定义异常
│   ├── responses.py      # 统一响应格式
│   └── utils/
│       ├── __init__.py
│       ├── image_downloader.py
│       └── validators.py
│
└── tools/                # 工具脚本（重构）
    ├── data_import/
    │   ├── import_public_data.py
    │   └── import_song_records.py
    ├── image_processing/
    │   ├── image_downloader.py
    │   └── image_compressor.py
    └── bilibili/
        └── bilibili_importer.py
```

### 5.2 数据库架构设计

```
数据库架构：
├── db.sqlite3            # 核心业务数据库
│   ├── song_management   # 歌曲管理
│   ├── site_settings     # 网站设置
│   └── fansDIY           # 粉丝二创
│
├── view_data.sqlite3     # 数据分析数据库
│   └── data_analytics    # 数据分析
│
└── songlist.sqlite3      # 模板化歌单数据库
    └── songlist          # 模板化歌单
```

**数据库路由策略：**

```python
# xxm_fans_home/db_routers.py
class MultiDbRouter:
    """多数据库路由器"""

    # 应用到数据库的映射
    DATABASE_MAPPING = {
        'default': ['song_management', 'site_settings', 'fansDIY'],
        'view_data_db': ['data_analytics'],
        'songlist_db': ['songlist'],
    }

    def db_for_read(self, model, **hints):
        app_label = model._meta.app_label
        for db_name, apps in self.DATABASE_MAPPING.items():
            if app_label in apps:
                return db_name
        return None

    def db_for_write(self, model, **hints):
        app_label = model._meta.app_label
        for db_name, apps in self.DATABASE_MAPPING.items():
            if app_label in apps:
                return db_name
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in self.DATABASE_MAPPING:
            return app_label in self.DATABASE_MAPPING[db]
        return False
```

### 5.3 核心模块设计

#### 5.3.1 core 模块（新增）

**目的：** 提供跨应用共享的核心功能。

**目录结构：**
```
core/
├── __init__.py
├── cache.py              # 缓存装饰器
├── exceptions.py         # 自定义异常
├── responses.py          # 统一响应格式
└── utils/
    ├── __init__.py
    ├── image_downloader.py
    └── validators.py
```

**cache.py - 缓存装饰器：**

```python
# core/cache.py
from functools import wraps
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def cache_result(timeout=600, key_prefix=None):
    """
    缓存装饰器，统一处理缓存逻辑

    Args:
        timeout: 缓存超时时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_prefix:
                cache_key = f"{key_prefix}:{args}:{kwargs}"
            else:
                cache_key = f"{func.__name__}:{args}:{kwargs}"

            # 尝试从缓存获取
            try:
                result = cache.get(cache_key)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

            # 执行函数
            result = func(*args, **kwargs)

            # 尝试设置缓存
            try:
                cache.set(cache_key, result, timeout)
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

            return result
        return wrapper
    return decorator
```

**exceptions.py - 自定义异常：**

```python
# core/exceptions.py
from rest_framework.exceptions import APIException


class SongNotFoundException(APIException):
    """歌曲未找到异常"""
    status_code = 404
    default_detail = "歌曲未找到"


class InvalidParameterException(APIException):
    """无效参数异常"""
    status_code = 400
    default_detail = "参数无效"


class ArtistNotFoundException(APIException):
    """歌手未找到异常"""
    status_code = 404
    default_detail = "歌手未找到"
```

**responses.py - 统一响应格式：**

```python
# core/responses.py
from rest_framework.response import Response


def success_response(data=None, message="操作成功", code=200):
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 响应码
    """
    return Response({
        'code': code,
        'message': message,
        'data': data
    })


def error_response(message="操作失败", code=400, errors=None):
    """
    错误响应

    Args:
        message: 错误消息
        code: 错误码
        errors: 详细错误信息
    """
    response_data = {
        'code': code,
        'message': message,
    }
    if errors:
        response_data['errors'] = errors
    return Response(response_data, status=code)
```

#### 5.3.2 song_management 应用

**目录结构：**
```
song_management/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── song.py
│   ├── style.py
│   └── tag.py
├── services/
│   ├── __init__.py
│   ├── song_service.py
│   └── ranking_service.py
├── api/
│   ├── __init__.py
│   ├── views.py
│   └── serializers.py
└── admin/
    ├── __init__.py
    ├── song_admin.py
    ├── style_admin.py
    └── tag_admin.py
```

**models/song.py：**

```python
# song_management/models/song.py
from django.db import models


class Song(models.Model):
    """歌曲模型"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=200, blank=True, null=True, verbose_name='歌手')
    last_performed = models.DateField(blank=True, null=True, verbose_name='最近演唱时间')
    perform_count = models.IntegerField(default=0, verbose_name='演唱次数')
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name='语言')

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"
        ordering = ['song_name']
        indexes = [
            models.Index(fields=['song_name']),
            models.Index(fields=['singer']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.song_name


class SongRecord(models.Model):
    """演唱记录模型"""
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='records', verbose_name='歌曲')
    performed_at = models.DateField(verbose_name='演唱时间')
    url = models.URLField(blank=True, null=True, verbose_name='视频链接')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    cover_url = models.CharField(max_length=300, blank=True, null=True, verbose_name='封面URL')

    class Meta:
        verbose_name = "演唱记录"
        verbose_name_plural = "演唱记录"
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.song.song_name} @ {self.performed_at}"
```

**services/song_service.py：**

```python
# song_management/services/song_service.py
from typing import List, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Q
from ..models import Song, SongRecord
from core.cache import cache_result


class SongService:
    """歌曲服务"""

    @staticmethod
    @cache_result(timeout=600, key_prefix="songs_list")
    def get_songs(
        search_query: str = "",
        language: Optional[str] = None,
        styles: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        ordering: str = "-last_performed"
    ) -> List[Song]:
        """
        获取歌曲列表

        Args:
            search_query: 搜索关键词
            language: 语言筛选
            styles: 曲风筛选
            tags: 标签筛选
            ordering: 排序方式

        Returns:
            歌曲列表
        """
        queryset = Song.objects.all()

        # 搜索
        if search_query:
            queryset = queryset.filter(
                Q(song_name__icontains=search_query) | Q(singer__icontains=search_query)
            )

        # 语言筛选
        if language:
            queryset = queryset.filter(language=language)

        # 曲风筛选
        if styles:
            style_filter = Q()
            for style in styles:
                style_filter |= Q(song_styles__style__name=style)
            queryset = queryset.filter(style_filter).distinct()

        # 标签筛选
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(song_tags__tag__name=tag)
            queryset = queryset.filter(tag_filter).distinct()

        # 排序
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    @staticmethod
    def get_song_by_id(song_id: int) -> Optional[Song]:
        """
        根据ID获取歌曲

        Args:
            song_id: 歌曲ID

        Returns:
            歌曲对象或None
        """
        try:
            return Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return None

    @staticmethod
    def get_random_song() -> Optional[Song]:
        """
        获取随机歌曲

        Returns:
            随机歌曲或None
        """
        return Song.objects.order_by('?').first()


class SongRecordService:
    """演唱记录服务"""

    @staticmethod
    @cache_result(timeout=600, key_prefix="song_records")
    def get_records_by_song(song_id: int, page: int = 1, page_size: int = 20):
        """
        获取歌曲的演唱记录

        Args:
            song_id: 歌曲ID
            page: 页码
            page_size: 每页数量

        Returns:
            分页的演唱记录
        """
        from django.core.paginator import Paginator

        queryset = SongRecord.objects.filter(song_id=song_id).order_by('-performed_at')
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page)

        return {
            'total': paginator.count,
            'page': page.number,
            'page_size': page_size,
            'results': list(page.object_list)
        }
```

**services/ranking_service.py：**

```python
# song_management/services/ranking_service.py
from typing import List, Optional
from datetime import datetime, timedelta
from django.db.models import Count
from ..models import Song
from core.cache import cache_result


class RankingService:
    """排行榜服务"""

    RANGE_MAP = {
        'all': None,
        '1m': 30,
        '3m': 90,
        '1y': 365,
        '10d': 10,
        '20d': 20,
        '30d': 30,
    }

    @staticmethod
    @cache_result(timeout=300, key_prefix="top_songs")
    def get_top_songs(range_key: str = 'all', limit: int = 10) -> List[dict]:
        """
        获取热歌榜

        Args:
            range_key: 时间范围（all, 1m, 3m, 1y, 10d, 20d, 30d）
            limit: 返回数量

        Returns:
            歌曲列表
        """
        days = RankingService.RANGE_MAP.get(range_key, None)
        queryset = Song.objects.all()

        if days:
            since = datetime.now().date() - timedelta(days=days)
            queryset = queryset.filter(records__performed_at__gte=since)

        queryset = queryset.annotate(recent_count=Count('records')).order_by('-recent_count', '-last_performed')[:limit]

        return [
            {
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'perform_count': song.recent_count,
                'last_performed': song.last_performed,
            }
            for song in queryset
        ]
```

**api/views.py：**

```python
# song_management/api/views.py
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from core.responses import success_response, error_response
from core.exceptions import SongNotFoundException
from ..models import Song, SongRecord, Style, Tag
from ..serializers import SongSerializer, SongRecordSerializer, StyleSerializer, TagSerializer
from ..services import SongService, SongRecordService, RankingService


class SongListView(generics.ListAPIView):
    """歌曲列表视图"""
    serializer_class = SongSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['song_name', 'singer']
    ordering_fields = ['singer', 'last_performed', 'perform_count']
    ordering = ['-last_performed']

    def get_queryset(self):
        search_query = self.request.query_params.get("q", "")
        language = self.request.query_params.get("language", "")
        styles = self.request.query_params.getlist('styles', [])
        tags = self.request.query_params.getlist('tags', [])

        return SongService.get_songs(
            search_query=search_query,
            language=language,
            styles=styles,
            tags=tags,
            ordering=self.request.query_params.get("ordering", "-last_performed")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


@api_view(['GET'])
def random_song_api(request):
    """随机歌曲API"""
    song = SongService.get_random_song()
    if song:
        serializer = SongSerializer(song)
        return success_response(data=serializer.data)
    else:
        return error_response(message="暂无歌曲数据", code=404)


@api_view(['GET'])
def top_songs_api(request):
    """热歌榜API"""
    range_key = request.GET.get('range', 'all')
    limit = int(request.GET.get('limit', 10))

    songs = RankingService.get_top_songs(range_key=range_key, limit=limit)
    return success_response(data=songs)
```

#### 5.3.3 data_analytics 应用

**目录结构：**
```
data_analytics/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── work_static.py
│   ├── work_metrics_hour.py
│   └── crawl_session.py
├── services/
│   ├── __init__.py
│   └── analytics_service.py
├── api/
│   ├── __init__.py
│   ├── views.py
│   └── serializers.py
└── admin/
    ├── __init__.py
    └── analytics_admin.py
```

**models/work_static.py：**

```python
# data_analytics/models/work_static.py
from django.db import models


class WorkStatic(models.Model):
    """作品静态信息表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    author = models.CharField(max_length=200, verbose_name="作者")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="封面URL")
    is_valid = models.BooleanField(default=True, verbose_name="投稿是否有效")

    class Meta:
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"
        unique_together = ("platform", "work_id")
        ordering = ['-publish_time']

    def __str__(self):
        return f"{self.title} - {self.author}"
```

#### 5.3.4 site_settings 应用

**目录结构：**
```
site_settings/
├── __init__.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── settings.py
├── services/
│   ├── __init__.py
│   └── settings_service.py
├── api/
│   ├── __init__.py
│   ├── views.py
│   └── serializers.py
└── admin/
    ├── __init__.py
    └── settings_admin.py
```

**models/settings.py：**

```python
# site_settings/models/settings.py
from django.db import models


class SiteSettings(models.Model):
    """网站设置模型"""
    favicon = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name="网站图标"
    )
    site_title = models.CharField(max_length=200, blank=True, verbose_name="网站标题")
    site_description = models.TextField(blank=True, verbose_name="网站描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def __str__(self):
        return "网站设置"

    def favicon_url(self):
        """返回favicon的URL路径"""
        if self.favicon:
            return self.favicon.url
        return None


class Recommendation(models.Model):
    """推荐语模型"""
    content = models.TextField(help_text="推荐语内容")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    recommended_songs = models.ManyToManyField(
        'song_management.Song',
        blank=True,
        help_text="推荐的歌曲"
    )
    is_active = models.BooleanField(default=True, help_text="是否激活显示")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "推荐语"
        verbose_name_plural = "推荐语"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"推荐语: {self.content[:50]}..." if len(self.content) > 50 else f"推荐语: {self.content}"
```

**services/settings_service.py：**

```python
# site_settings/services/settings_service.py
from typing import Optional, List
from ..models import SiteSettings, Recommendation
from core.cache import cache_result


class SettingsService:
    """网站设置服务"""

    @staticmethod
    @cache_result(timeout=3600, key_prefix="site_settings")
    def get_settings() -> Optional[SiteSettings]:
        """
        获取网站设置

        Returns:
            网站设置对象或None
        """
        try:
            return SiteSettings.objects.first()
        except SiteSettings.DoesNotExist:
            return None


class RecommendationService:
    """推荐语服务"""

    @staticmethod
    @cache_result(timeout=300, key_prefix="recommendation")
    def get_active_recommendation() -> Optional[dict]:
        """
        获取激活的推荐语

        Returns:
            推荐语数据或None
        """
        recommendation = Recommendation.objects.filter(is_active=True).order_by('-updated_at').first()

        if recommendation:
            recommended_songs = [
                {
                    "id": song.id,
                    "song_name": song.song_name,
                    "singer": song.singer,
                    "perform_count": song.perform_count
                }
                for song in recommendation.recommended_songs.all()
            ]

            return {
                "content": recommendation.content,
                "recommended_songs": recommended_songs
            }
        else:
            return {
                "content": "欢迎来到热歌榜！",
                "recommended_songs": []
            }
```

### 5.4 工具脚本重构

**目录结构：**
```
tools/
├── __init__.py
├── data_import/
│   ├── __init__.py
│   ├── import_public_data.py
│   └── import_song_records.py
├── image_processing/
│   ├── __init__.py
│   ├── image_downloader.py
│   └── image_compressor.py
└── bilibili/
    ├── __init__.py
    └── bilibili_importer.py
```

**image_processing/image_downloader.py：**

```python
# tools/image_processing/image_downloader.py
import os
import requests
from pathlib import Path
from typing import List, Optional, Union
from django.conf import settings


class ImageDownloader:
    """统一的图片下载器"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(settings.MEDIA_ROOT) / 'covers'
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def download(
        self,
        url: str,
        filename: Optional[str] = None,
        overwrite: bool = False,
        timeout: int = 30
    ) -> Optional[str]:
        """
        下载图片

        Args:
            url: 图片URL
            filename: 保存的文件名，如果为None则从URL提取
            overwrite: 是否覆盖已存在的文件
            timeout: 请求超时时间

        Returns:
            保存的文件路径或None
        """
        if not filename:
            filename = url.split('/')[-1]

        filepath = self.base_dir / filename

        if filepath.exists() and not overwrite:
            print(f"文件已存在，跳过: {filepath}")
            return str(filepath)

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"下载成功: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return None

    def download_batch(
        self,
        urls: List[Union[str, dict]],
        overwrite: bool = False,
        timeout: int = 30
    ) -> List[str]:
        """
        批量下载图片

        Args:
            urls: URL列表或字典列表
            overwrite: 是否覆盖已存在的文件
            timeout: 请求超时时间

        Returns:
            成功下载的文件路径列表
        """
        results = []

        for item in urls:
            if isinstance(item, dict):
                url = item['url']
                filename = item.get('filename')
            else:
                url = item
                filename = None

            result = self.download(url, filename, overwrite, timeout)
            if result:
                results.append(result)

        return results
```

### 5.5 配置文件优化

**清理后的 settings.py：**

```python
# xxm_fans_home/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'corsheaders',
    # 重构后的应用
    'song_management',
    'data_analytics',
    'site_settings',
    'fansDIY',
    'songlist',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'xxm_fans_home.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'xxm_fans_home.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {'timeout': 20}
    },
    'view_data_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'view_data.sqlite3',
        'OPTIONS': {'timeout': 20}
    },
    'songlist_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'songlist.sqlite3',
        'OPTIONS': {'timeout': 20}
    }
}

# Database routers
DATABASE_ROUTERS = ['xxm_fans_home.db_routers.MultiDbRouter']

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/covers/'
MEDIA_ROOT = BASE_DIR / 'xxm_fans_frontend' / 'public' / 'covers'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

---

## 6. 实施计划

### 6.1 阶段划分

#### 阶段 1：核心模块创建（2-3 天）

**任务：**
1. 创建 `core` 应用
2. 实现缓存装饰器
3. 实现统一响应格式
4. 实现自定义异常
5. 实现工具类（图片下载器等）

**验收标准：**
- core 模块功能完整
- 单元测试通过
- 文档完善

#### 阶段 2：song_management 应用创建（4-5 天）

**任务：**
1. 创建 `song_management` 应用
2. 创建模型文件（models/song.py, models/style.py, models/tag.py）
3. 创建服务层（services/song_service.py, services/ranking_service.py）
4. 创建 API 视图（api/views.py）
5. 创建 Admin（admin/song_admin.py 等）
6. 数据迁移
7. 单元测试

**验收标准：**
- 所有功能正常
- API 测试通过
- Admin 后台正常

#### 阶段 3：data_analytics 应用创建（2-3 天）

**任务：**
1. 创建 `data_analytics` 应用
2. 创建模型文件
3. 创建服务层
4. 创建 API 视图
5. 创建 Admin
6. 数据迁移
7. 单元测试

**验收标准：**
- 所有功能正常
- API 测试通过
- Admin 后台正常

#### 阶段 4：site_settings 应用创建（2-3 天）

**任务：**
1. 创建 `site_settings` 应用
2. 创建模型文件
3. 创建服务层
4. 创建 API 视图
5. 创建 Admin
6. 数据迁移
7. 单元测试

**验收标准：**
- 所有功能正常
- API 测试通过
- Admin 后台正常

#### 阶段 5：fansDIY 应用重构（2-3 天）

**任务：**
1. 重构 fansDIY 应用
2. 创建服务层
3. 拆分 Admin 文件
4. 单元测试

**验收标准：**
- 所有功能正常
- API 测试通过
- Admin 后台正常

#### 阶段 6：工具脚本重构（1-2 天）

**任务：**
1. 重构工具脚本目录结构
2. 实现统一的图片下载器
3. 删除重复脚本
4. 更新文档

**验收标准：**
- 工具脚本功能完整
- 文档完善

#### 阶段 7：配置文件优化（1 天）

**任务：**
1. 清理 settings.py
2. 更新数据库路由
3. 更新 URL 配置
4. 环境变量配置

**验收标准：**
- 配置文件清晰
- 环境变量正常

#### 阶段 8：集成测试与文档（2-3 天）

**任务：**
1. 集成测试
2. 性能测试
3. API 文档更新
4. 部署文档更新
5. 开发文档更新

**验收标准：**
- 所有测试通过
- 文档完善

#### 阶段 9：数据迁移与上线（2-3 天）

**任务：**
1. 数据备份
2. 数据迁移
3. 灰度发布
4. 监控
5. 回滚准备

**验收标准：**
- 数据迁移成功
- 服务正常运行
- 无严重 bug

### 6.2 时间估算

| 阶段 | 工作日 | 累计 |
|------|--------|------|
| 阶段 1：核心模块创建 | 2-3 | 2-3 |
| 阶段 2：song_management 应用创建 | 4-5 | 6-8 |
| 阶段 3：data_analytics 应用创建 | 2-3 | 8-11 |
| 阶段 4：site_settings 应用创建 | 2-3 | 10-14 |
| 阶段 5：fansDIY 应用重构 | 2-3 | 12-17 |
| 阶段 6：工具脚本重构 | 1-2 | 13-19 |
| 阶段 7：配置文件优化 | 1 | 14-20 |
| 阶段 8：集成测试与文档 | 2-3 | 16-23 |
| 阶段 9：数据迁移与上线 | 2-3 | 18-26 |

**总计：18-26 个工作日（约 4-5 周）**

---

## 7. 风险评估与缓解

### 7.1 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 数据迁移失败 | 中 | 高 | 完整备份数据，分步迁移，充分测试 |
| API 兼容性问题 | 高 | 中 | 保持旧 API 兼容，逐步迁移 |
| 功能缺失 | 中 | 高 | 功能对比测试，确保功能完整 |
| 性能下降 | 低 | 高 | 性能测试，优化查询和缓存 |
| 数据库路由问题 | 中 | 高 | 充分测试多数据库配置 |
| 服务层性能问题 | 低 | 中 | 性能测试，优化服务层逻辑 |

### 7.2 业务风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 服务中断 | 低 | 高 | 灰度发布，快速回滚方案 |
| 用户不适应 | 低 | 中 | 保持 API 兼容性，无需用户改动 |
| 数据丢失 | 低 | 高 | 完整备份，分步迁移 |

### 7.3 时间风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 开发延期 | 中 | 中 | 合理安排时间，预留缓冲期 |
| 测试不充分 | 中 | 高 | 充分测试，自动化测试 |

---

## 8. 预期收益

### 8.1 技术收益

1. **代码质量提升**
   - 代码重复率从 ~15% 降低到 <5%
   - admin.py 最大行数从 855 行降低到 <200 行
   - 平均函数行数从 ~50 降低到 <30

2. **可维护性提升**
   - 职责分离，每个应用只负责一个功能模块
   - 服务层抽象，业务逻辑易于复用和测试
   - 模块化设计，易于添加新功能

3. **可测试性提升**
   - 服务层覆盖率从 0% 提升到 >80%
   - 单元测试覆盖率从 <10% 提升到 >60%
   - 自动化测试，降低回归风险

4. **可扩展性提升**
   - 模块化设计，易于添加新应用
   - 服务层抽象，易于扩展业务逻辑
   - 配置驱动，易于添加新歌手

### 8.2 业务收益

1. **开发效率提升**
   - 新功能开发时间减少 30%
   - Bug 修复时间减少 40%
   - 代码审查时间减少 50%

2. **团队协作提升**
   - 减少代码冲突
   - 提高代码可读性
   - 降低新人上手难度

3. **系统稳定性提升**
   - 减少系统故障
   - 提高系统可用性
   - 降低运维成本

### 8.3 量化指标

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 代码重复率 | ~15% | <5% | 67% ↓ |
| admin.py 最大行数 | 855 | <200 | 77% ↓ |
| 服务层覆盖率 | 0% | >80% | +80% |
| 单元测试覆盖率 | <10% | >60% | +50% |
| 开发效率 | 基准 | +30% | 30% ↑ |
| Bug 修复时间 | 基准 | -40% | 40% ↓ |

---

## 9. 附录

### 9.1 参考资料

- [Django 最佳实践](https://docs.djangoproject.com/en/5.2/topics/best-practices/)
- [Django REST Framework 官方文档](https://www.django-rest-framework.org/)
- [Python 代码风格指南 (PEP 8)](https://peps.python.org/pep-0008/)
- [Clean Code 原则](https://github.com/ryanmcdermott/clean-code-javascript)

### 9.2 相关文档

- [songlist独立表架构说明.md](./songlist独立表架构说明.md)
- [VIEW_API分离重构完成报告.md](./VIEW_API分离重构完成报告.md)
- [API文档.md](./API文档.md)
- [ADMIN功能文档.md](./ADMIN功能文档.md)

### 9.3 版本历史

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| 1.0 | 2025-XX-XX | XXX | 初始版本 |
| 2.0 | 2026-01-12 | iFlow CLI | 高扩展性、高可读性重构方案 |

---

**文档结束**