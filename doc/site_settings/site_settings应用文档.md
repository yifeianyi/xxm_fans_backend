# site_settings 应用文档

## 概述

site_settings 应用负责管理网站的设置和推荐语功能。该应用从 main 应用中拆分出来，专门负责网站级别的配置和推荐内容管理。

## 功能特性

### 1. 网站设置管理
- 网站图标（favicon）管理
- 网站设置的单例模式（只能创建一个网站设置实例）

### 2. 推荐语管理
- 推荐语内容的创建、更新、删除
- 推荐语激活/停用状态管理
- 推荐歌曲的关联管理
- 推荐语的批量激活/停用操作

## 技术架构

### 模型层 (Models)

#### SiteSettings 模型
```python
class SiteSettings(models.Model):
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**字段说明：**
- `favicon`: 网站图标文件
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### Recommendation 模型
```python
class Recommendation(models.Model):
    content = models.TextField(help_text="推荐语内容")
    recommended_songs = models.ManyToManyField('song_management.Song', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**字段说明：**
- `content`: 推荐语内容
- `recommended_songs`: 推荐的歌曲列表（多对多关系）
- `is_active`: 是否激活显示
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 服务层 (Services)

#### SettingsService
提供网站设置的业务逻辑：

- `get_site_settings()`: 获取网站设置（带缓存）
- `create_site_settings(favicon=None)`: 创建网站设置
- `update_site_settings(settings_id, favicon=None)`: 更新网站设置

#### RecommendationService
提供推荐语的业务逻辑：

- `get_active_recommendations()`: 获取所有激活的推荐语（带缓存）
- `get_recommendation_by_id(recommendation_id)`: 根据ID获取推荐语（带缓存）
- `create_recommendation(content, recommended_songs=None)`: 创建推荐语
- `update_recommendation(recommendation_id, content=None, is_active=None, recommended_songs=None)`: 更新推荐语
- `delete_recommendation(recommendation_id)`: 删除推荐语
- `get_all_recommendations()`: 获取所有推荐语（包括未激活的）

### API 层 (Views & Serializers)

#### API 端点

1. **网站设置 API**
   - `GET /api/site-settings/settings/`: 获取网站设置
   - `POST /api/site-settings/settings/`: 创建网站设置
   - `PUT /api/site-settings/settings/`: 更新网站设置

2. **推荐语 API**
   - `GET /api/site-settings/recommendations/`: 获取推荐语列表
   - `POST /api/site-settings/recommendations/`: 创建推荐语
   - `GET /api/site-settings/recommendations/<id>/`: 获取推荐语详情
   - `PUT /api/site-settings/recommendations/<id>/`: 更新推荐语
   - `DELETE /api/site-settings/recommendations/<id>/`: 删除推荐语

#### 查询参数

- `all=true`: 获取所有推荐语（包括未激活的）
- `is_active=true`: 只获取激活的推荐语（默认）

#### 序列化器

**SiteSettingsSerializer**
- 包含 favicon_url 字段（自动生成）
- 支持创建和更新操作

**RecommendationSerializer**
- 包含 recommended_songs_details 字段（自动生成详细信息）
- 支持创建、更新和删除操作
- 动态设置 recommended_songs 的 queryset

### Admin 后台

#### SiteSettingsAdmin
- 限制只能创建一个网站设置实例
- 只读字段：created_at, updated_at
- 列表显示：id, favicon_url, created_at, updated_at

#### RecommendationAdmin
- 批量操作：激活推荐语、停用推荐语
- 横向过滤器：recommended_songs
- 搜索字段：content
- 列表显示：id, content_preview, is_active, song_count, created_at, updated_at
- 只读字段：created_at, updated_at

## 数据库设计

### 表结构

#### site_settings_sitesettings 表
```sql
CREATE TABLE "site_settings_sitesettings" (
    "id" bigint NOT NULL PRIMARY KEY AUTOINCREMENT,
    "favicon" varchar(100) NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);
```

#### site_settings_recommendation 表
```sql
CREATE TABLE "site_settings_recommendation" (
    "id" bigint NOT NULL PRIMARY KEY AUTOINCREMENT,
    "content" text NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL
);
```

#### site_settings_recommendation_recommended_songs 表（多对多关系表）
```sql
CREATE TABLE "site_settings_recommendation_recommended_songs" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "recommendation_id" bigint NOT NULL REFERENCES "site_settings_recommendation" ("id") DEFERRABLE INITIALLY DEFERRED,
    "song_id" integer NOT NULL REFERENCES "song_management_song" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("recommendation_id", "song_id")
);
```

## 缓存策略

### 缓存配置

- **网站设置缓存**: 3600秒（1小时）
- **推荐语缓存**: 1800秒（30分钟）

### 缓存失效

在以下情况下会清除缓存：
- 创建网站设置
- 更新网站设置
- 创建推荐语
- 更新推荐语
- 删除推荐语

## 使用示例

### Python 代码示例

#### 获取网站设置
```python
from site_settings.services import SettingsService

settings = SettingsService.get_site_settings()
if settings:
    print(f"Favicon URL: {settings.favicon_url()}")
```

#### 创建推荐语
```python
from site_settings.services import RecommendationService

recommendation = RecommendationService.create_recommendation(
    content="这是一首非常好听的歌曲！",
    recommended_songs=[1, 2, 3]  # 歌曲 ID 列表
)
```

#### 获取激活的推荐语
```python
from site_settings.services import RecommendationService

recommendations = RecommendationService.get_active_recommendations()
for rec in recommendations:
    print(f"{rec.content}")
    for song in rec.recommended_songs.all():
        print(f"  - {song.song_name}")
```

### API 请求示例

#### 获取网站设置
```bash
GET /api/site-settings/settings/
```

响应：
```json
{
    "code": 0,
    "message": "获取网站设置成功",
    "data": {
        "id": 1,
        "favicon": "/media/settings/favicon.ico",
        "favicon_url": "/media/settings/favicon.ico",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 获取推荐语列表
```bash
GET /api/site-settings/recommendations/?all=true
```

响应：
```json
{
    "code": 0,
    "message": "获取推荐语列表成功",
    "data": [
        {
            "id": 1,
            "content": "这是一首非常好听的歌曲！",
            "recommended_songs": [1, 2, 3],
            "recommended_songs_details": [
                {
                    "id": 1,
                    "song_name": "歌曲1",
                    "singer": "歌手1",
                    "language": "中文"
                }
            ],
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

## 注意事项

1. **网站设置单例模式**：系统只能创建一个网站设置实例，Admin 后台会自动限制重复创建。

2. **缓存依赖**：服务层方法使用了缓存装饰器，在手动修改数据库时需要注意清除缓存。

3. **多对多关系**：推荐语与歌曲的关系是多对多，在创建或更新推荐语时，需要传入歌曲 ID 列表。

4. **外键依赖**：Recommendation 模型依赖于 song_management.Song 模型，确保 song_management 应用已正确配置。

## 扩展建议

1. **多语言支持**：可以考虑为推荐语添加多语言支持。

2. **推荐语分类**：可以添加推荐语分类功能，如"今日推荐"、"热门推荐"等。

3. **定时任务**：可以添加定时任务，自动激活/停用推荐语。

4. **推荐语统计**：可以添加推荐语的点击统计功能，了解用户对推荐语的兴趣。

## 测试

测试文件位于 `test/site_settings/` 目录下：

- `test_settings_service.py`: SettingsService 测试
- `test_recommendation_service.py`: RecommendationService 测试
- `test_views.py`: API 视图测试
- `test_admin.py`: Admin 后台测试

运行测试：
```bash
bash test/run_site_settings_tests.sh
```

## 维护者

- 创建日期：2026-01-12
- 版本：1.0.0
- 基于：REFACTORING_PLAN-2.0.md