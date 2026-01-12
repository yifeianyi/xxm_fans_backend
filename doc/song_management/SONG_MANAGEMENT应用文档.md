# Song Management 应用文档

## 应用概述

Song Management 是 XXM Fans Home 后端项目的核心应用之一，负责歌曲管理、演唱记录、曲风分类、标签管理等功能。

## 技术架构

- **框架**: Django 5.2.5
- **API**: Django REST Framework 3.15.2
- **架构模式**: 服务层架构（Service Layer Pattern）
- **核心模块**: core（缓存、响应格式、异常处理）

## 应用结构

```
song_management/
├── __init__.py
├── apps.py
├── admin.py
├── urls.py
├── models/
│   ├── __init__.py
│   ├── song.py
│   ├── style.py
│   └── tag.py
├── services/
│   ├── __init__.py
│   ├── song_service.py
│   ├── song_record_service.py
│   └── ranking_service.py
└── api/
    ├── __init__.py
    ├── serializers.py
    └── views.py
```

## 数据模型

### Song（歌曲模型）

**字段**:
- `id`: 主键
- `song_name`: 歌曲名称
- `singer`: 歌手
- `last_performed`: 最近演唱时间
- `perform_count`: 演唱次数
- `language`: 语言

**索引**:
- `song_name`
- `singer`
- `language`

**关系**:
- 一对多：SongRecord（演唱记录）
- 多对多：Style（曲风）
- 多对多：Tag（标签）

### SongRecord（演唱记录模型）

**字段**:
- `id`: 主键
- `song`: 关联歌曲（外键）
- `performed_at`: 演唱时间
- `url`: 视频链接
- `notes`: 备注
- `cover_url`: 封面URL

### Style（曲风模型）

**字段**:
- `id`: 主键
- `name`: 曲风名称（唯一）
- `description`: 描述

### Tag（标签模型）

**字段**:
- `id`: 主键
- `name`: 标签名称（唯一）
- `description`: 描述

## 服务层

### SongService

**方法**:
- `get_songs(query, language, styles, tags, ordering)` - 获取歌曲列表，支持筛选和排序
- `get_song_by_id(song_id)` - 根据 ID 获取歌曲
- `get_random_song()` - 获取随机歌曲
- `get_all_languages()` - 获取所有语言
- `get_song_count()` - 获取歌曲总数

**缓存策略**:
- `get_song_by_id`: 缓存 600 秒
- `get_random_song`: 缓存 300 秒

### SongRecordService

**方法**:
- `get_records_by_song(song_id, page, page_size)` - 获取歌曲的演唱记录（分页）
- `get_record_count_by_song(song_id)` - 获取演唱记录数量
- `get_latest_record(song_id)` - 获取最新演唱记录

**缓存策略**:
- `get_records_by_song`: 缓存 600 秒

**功能特性**:
- 自动生成默认封面路径
- 支持分页
- 按时间倒序排列

### RankingService

**方法**:
- `get_top_songs(range_key, limit)` - 获取热门歌曲排行榜
- `get_most_performed_songs(limit)` - 获取演唱次数最多的歌曲
- `get_recently_performed_songs(limit)` - 获取最近演唱的歌曲

**时间范围**:
- `all`: 全部时间
- `1m`: 最近1个月
- `3m`: 最近3个月
- `1y`: 最近1年
- `10d`: 最近10天
- `20d`: 最近20天
- `30d`: 最近30天

**缓存策略**:
- `get_top_songs`: 缓存 300 秒

## API 接口

### 歌曲相关

#### 歌曲列表

- **URL**: `/api/songs/`
- **方法**: GET
- **参数**:
  - `q`: 搜索关键词
  - `language`: 语言筛选
  - `styles`: 曲风筛选（支持多个）
  - `tags`: 标签筛选（支持多个）
  - `ordering`: 排序字段
  - `page`: 页码
  - `limit`: 每页数量

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 50,
    "results": [...]
  }
}
```

#### 歌曲详情

- **URL**: `/api/songs/<song_id>/`
- **方法**: GET

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "id": 1,
    "song_name": "测试歌曲",
    "singer": "测试歌手",
    "language": "中文",
    "styles": ["流行"],
    "tags": ["经典"],
    "last_performed": "2026-01-01",
    "perform_count": 10
  }
}
```

#### 演唱记录列表

- **URL**: `/api/songs/<song_id>/records/`
- **方法**: GET
- **参数**:
  - `page`: 页码
  - `page_size`: 每页数量

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 20,
    "page": 1,
    "page_size": 20,
    "results": [...]
  }
}
```

### 曲风和标签

#### 曲风列表

- **URL**: `/api/styles/`
- **方法**: GET

#### 标签列表

- **URL**: `/api/tags/`
- **方法**: GET

#### 语言列表

- **URL**: `/api/languages/`
- **方法**: GET

### 排行榜和随机

#### 热门歌曲

- **URL**: `/api/top-songs/`
- **方法**: GET
- **参数**:
  - `range`: 时间范围（all, 1m, 3m, 1y, 10d, 20d, 30d）
  - `limit`: 返回数量

#### 随机歌曲

- **URL**: `/api/random-song/`
- **方法**: GET

## Admin 后台

### 功能

1. **歌曲管理**
   - 列表展示：ID、歌曲名称、歌手、语言、最近演唱时间、演唱次数
   - 筛选：语言、最近演唱时间
   - 搜索：歌曲名称、歌手
   - 只读字段：演唱次数

2. **演唱记录管理**
   - 列表展示：ID、歌曲、演唱时间、视频链接
   - 筛选：演唱时间
   - 搜索：歌曲名称

3. **曲风管理**
   - 列表展示：ID、曲风名称、描述
   - 搜索：曲风名称

4. **标签管理**
   - 列表展示：ID、标签名称、描述
   - 搜索：标签名称

5. **关联管理**
   - 歌曲曲风关联
   - 歌曲标签关联

## 使用示例

### 获取歌曲列表

```bash
# 获取所有歌曲
GET /api/songs/

# 搜索歌曲
GET /api/songs/?q=测试

# 按语言筛选
GET /api/songs/?language=中文

# 按曲风筛选
GET /api/songs/?styles=流行,摇滚

# 排序
GET /api/songs/?ordering=-perform_count
```

### 获取热门歌曲

```bash
# 获取全部时间热门歌曲
GET /api/top-songs/?range=all&limit=10

# 获取最近30天热门歌曲
GET /api/top-songs/?range=30d&limit=10
```

### 获取随机歌曲

```bash
GET /api/random-song/
```

## 性能优化

### 缓存策略

1. **歌曲详情缓存**: 600 秒（10分钟）
2. **随机歌曲缓存**: 300 秒（5分钟）
3. **热门歌曲缓存**: 300 秒（5分钟）
4. **演唱记录缓存**: 600 秒（10分钟）

### 数据库索引

1. **Song 表**: song_name, singer, language
2. **SongRecord 表**: performed_at
3. **SongStyle 表**: (song, style) 联合索引
4. **SongTag 表**: (song, tag) 联合索引

### 查询优化

1. 使用 `select_related` 和 `prefetch_related` 减少查询次数
2. 使用 `only()` 和 `defer()` 减少数据传输
3. 使用分页避免一次性加载大量数据

## 异常处理

### 自定义异常

1. **SongNotFoundException**: 歌曲不存在（404）
2. **InvalidParameterException**: 参数错误（400）

### 统一响应格式

所有 API 都使用统一的响应格式：

```json
{
  "code": 200,
  "message": "成功",
  "data": {...}
}
```

错误响应：

```json
{
  "code": 404,
  "message": "歌曲 ID 999 不存在",
  "data": null
}
```

## 测试

### 单元测试

- **服务层测试**: SongService, SongRecordService, RankingService
- **视图测试**: 所有 API 端点
- **测试覆盖率**: 目标 >80%

### 运行测试

```bash
# 运行所有测试
python manage.py test test.song_management

# 运行特定测试
python manage.py test test.song_management.test_song_service

# 使用测试脚本
./test/run_song_management_tests.sh
```

## 部署

### 数据库迁移

```bash
# 创建迁移
python manage.py makemigrations song_management

# 执行迁移
python manage.py migrate song_management
```

### URL 配置

在主 URL 配置中添加：

```python
urlpatterns = [
    path('api/songs/', include('song_management.urls')),
]
```

## 注意事项

1. **URL 冲突**: song_management 的 URL 与 main 应用有冲突，需要协调解决
2. **循环依赖**: 模型之间使用字符串引用避免循环依赖
3. **缓存失效**: 修改歌曲数据后需要手动清除相关缓存
4. **分页限制**: 单页最大返回 50 条记录

## 未来改进

1. 添加更多筛选条件
2. 支持批量操作
3. 添加歌曲推荐功能
4. 优化大数据量查询性能
5. 添加歌曲统计功能

## 相关文档

- [REFACTORING_PLAN-2.0.md](./REFACTORING_PLAN-2.0.md) - 重构方案
- [todolist-2.0.md](./todolist-2.0.md) - 任务清单
- [SONG_MANAGEMENT测试报告.md](./SONG_MANAGEMENT测试报告.md) - 测试报告

---

**文档版本**: 1.0
**最后更新**: 2026-01-12