# Data Analytics 应用文档

## 应用概述

Data Analytics 是 XXM Fans Home 后端项目的数据分析应用，负责作品数据采集、存储、分析和可视化展示。支持多平台作品数据追踪、实时指标监控和爬虫会话管理。

## 技术架构

- **框架**: Django 5.2.5
- **API**: Django REST Framework 3.15.2
- **架构模式**: 服务层架构（Service Layer Pattern）
- **核心模块**: core（缓存、响应格式、异常处理）
- **数据库**: view_data_db（独立数据库）

## 应用结构

```
data_analytics/
├── __init__.py
├── admin.py
├── apps.py
├── models/
│   ├── __init__.py
│   ├── work_static.py
│   ├── work_metrics_hour.py
│   └── crawl_session.py
├── services/
│   ├── __init__.py
│   └── analytics_service.py
└── api/
    ├── __init__.py
    ├── serializers.py
    └── views.py
```

## 数据模型

### WorkStatic（作品静态信息模型）

**字段**:
- `id`: 主键
- `platform`: 平台（如：bilibili、youtube）
- `work_id`: 作品ID（平台唯一）
- `title`: 作品标题
- `author`: 作者
- `publish_time`: 发布时间
- `cover_url`: 封面URL
- `is_valid`: 投稿是否有效

**索引**:
- `(platform, work_id)` 联合唯一索引
- `publish_time`

**约束**:
- `unique_together`: (platform, work_id)

### WorkMetricsHour（作品小时级指标模型）

**字段**:
- `id`: 主键
- `work`: 关联作品静态信息（外键）
- `timestamp`: 时间戳（小时级）
- `view_count`: 播放量
- `like_count`: 点赞数
- `comment_count`: 评论数
- `share_count`: 分享数
- `collect_count`: 收藏数
- `coin_count`: 投币数

**索引**:
- `(work, timestamp)` 联合索引

**关系**:
- 多对一：WorkStatic

### CrawlSession（爬虫会话模型）

**字段**:
- `id`: 主键
- `source`: 数据源
- `start_time`: 开始时间
- `end_time`: 结束时间
- `status`: 状态（success, failed, running）
- `works_count`: 作品数量
- `error_message`: 错误信息

**索引**:
- `source`
- `start_time`

## 服务层

### AnalyticsService

**方法**:
- `get_work_list(platform=None, is_valid=None, limit=100, offset=0)` - 获取作品列表
- `get_work_detail(platform, work_id)` - 获取作品详情
- `get_work_metrics(platform, work_id, start_time=None, end_time=None)` - 获取作品指标
- `get_work_metrics_summary(platform, work_id, start_time=None, end_time=None)` - 获取作品指标汇总
- `get_crawl_sessions(source=None, limit=50, offset=0)` - 获取爬虫会话列表
- `get_crawl_session_detail(session_id)` - 获取爬虫会话详情
- `get_platform_statistics(platform, days=7)` - 获取平台统计数据
- `get_top_works(platform, metric='view_count', limit=10, days=7)` - 获取热门作品

**缓存策略**:
- `get_work_detail`: 缓存 300 秒
- `get_work_metrics_summary`: 缓存 600 秒
- `get_crawl_session_detail`: 缓存 300 秒

**功能特性**:
- 支持分页
- 支持时间范围筛选
- 支持多指标统计
- 自动计算汇总数据

## API 接口

### 作品相关

#### 作品列表

- **URL**: `/api/data_analytics/works/`
- **方法**: GET
- **参数**:
  - `platform`: 平台筛选
  - `is_valid`: 有效状态筛选
  - `limit`: 返回数量（默认100）
  - `offset`: 偏移量

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 1000,
    "limit": 100,
    "offset": 0,
    "results": [
      {
        "id": 1,
        "platform": "bilibili",
        "work_id": "BV1234567890",
        "title": "测试视频",
        "author": "测试作者",
        "publish_time": "2026-01-01T00:00:00Z",
        "cover_url": "https://example.com/cover.jpg",
        "is_valid": true
      }
    ]
  }
}
```

#### 作品详情

- **URL**: `/api/data_analytics/works/<platform>/<work_id>/`
- **方法**: GET

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "id": 1,
    "platform": "bilibili",
    "work_id": "BV1234567890",
    "title": "测试视频",
    "author": "测试作者",
    "publish_time": "2026-01-01T00:00:00Z",
    "cover_url": "https://example.com/cover.jpg",
    "is_valid": true
  }
}
```

#### 作品指标列表

- **URL**: `/api/data_analytics/works/<platform>/<work_id>/metrics/`
- **方法**: GET
- **参数**:
  - `start_time`: 开始时间
  - `end_time`: 结束时间

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": [
    {
      "id": 1,
      "work": 1,
      "timestamp": "2026-01-01T00:00:00Z",
      "view_count": 1000,
      "like_count": 100,
      "comment_count": 50,
      "share_count": 20,
      "collect_count": 30,
      "coin_count": 40
    }
  ]
}
```

#### 作品指标汇总

- **URL**: `/api/data_analytics/works/<platform>/<work_id>/metrics/summary/`
- **方法**: GET
- **参数**:
  - `start_time`: 开始时间
  - `end_time`: 结束时间

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total_views": 10000,
    "total_likes": 1000,
    "total_comments": 500,
    "total_shares": 200,
    "total_collects": 300,
    "total_coins": 400,
    "avg_daily_views": 1000,
    "growth_rate": 10.5
  }
}
```

### 平台统计

#### 平台统计数据

- **URL**: `/api/data_analytics/platform/<platform>/statistics/`
- **方法**: GET
- **参数**:
  - `days`: 统计天数（默认7天）

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "platform": "bilibili",
    "total_works": 100,
    "total_views": 1000000,
    "total_likes": 100000,
    "total_comments": 50000,
    "avg_views_per_work": 10000,
    "top_work": {
      "work_id": "BV1234567890",
      "title": "热门视频",
      "view_count": 100000
    }
  }
}
```

#### 热门作品

- **URL**: `/api/data_analytics/platform/<platform>/top-works/`
- **方法**: GET
- **参数**:
  - `metric`: 指标类型（view_count, like_count, comment_count）
  - `limit`: 返回数量（默认10）
  - `days`: 统计天数（默认7天）

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": [
    {
      "work_id": "BV1234567890",
      "title": "热门视频1",
      "author": "作者1",
      "view_count": 100000,
      "like_count": 10000,
      "comment_count": 5000
    }
  ]
}
```

### 爬虫会话

#### 爬虫会话列表

- **URL**: `/api/data_analytics/sessions/`
- **方法**: GET
- **参数**:
  - `source`: 数据源筛选
  - `limit`: 返回数量（默认50）
  - `offset`: 偏移量

**响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "results": [
      {
        "id": 1,
        "source": "bilibili",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T01:00:00Z",
        "status": "success",
        "works_count": 100,
        "error_message": null
      }
    ]
  }
}
```

## Admin 后台

### 功能

1. **作品静态信息管理**
   - 列表展示：ID、平台、作品ID、标题、作者、发布时间、有效状态
   - 筛选：平台、有效状态、发布时间
   - 搜索：作品ID、标题、作者
   - 只读字段：发布时间

2. **作品指标管理**
   - 列表展示：ID、作品、时间戳、播放量、点赞数、评论数、分享数、收藏数、投币数
   - 筛选：作品、时间戳
   - 只读字段：所有指标

3. **爬虫会话管理**
   - 列表展示：ID、数据源、开始时间、结束时间、状态、作品数量、错误信息
   - 筛选：数据源、状态、开始时间
   - 只读字段：所有字段

## 使用示例

### 获取作品列表

```bash
# 获取所有作品
GET /api/data_analytics/works/

# 按平台筛选
GET /api/data_analytics/works/?platform=bilibili

# 只获取有效作品
GET /api/data_analytics/works/?is_valid=true

# 分页
GET /api/data_analytics/works/?limit=20&offset=0
```

### 获取作品指标

```bash
# 获取作品所有指标
GET /api/data_analytics/works/bilibili/BV1234567890/metrics/

# 获取指定时间范围内的指标
GET /api/data_analytics/works/bilibili/BV1234567890/metrics/?start_time=2026-01-01&end_time=2026-01-07
```

### 获取平台统计

```bash
# 获取最近7天统计数据
GET /api/data_analytics/platform/bilibili/statistics/

# 获取最近30天统计数据
GET /api/data_analytics/platform/bilibili/statistics/?days=30
```

### 获取热门作品

```bash
# 获取播放量最高的作品
GET /api/data_analytics/platform/bilibili/top-works/?metric=view_count&limit=10

# 获取点赞数最高的作品
GET /api/data_analytics/platform/bilibili/top-works/?metric=like_count&limit=10
```

## 性能优化

### 缓存策略

1. **作品详情缓存**: 300 秒（5分钟）
2. **指标汇总缓存**: 600 秒（10分钟）
3. **爬虫会话详情缓存**: 300 秒（5分钟）

### 数据库索引

1. **WorkStatic 表**:
   - `(platform, work_id)` 联合唯一索引
   - `publish_time` 索引

2. **WorkMetricsHour 表**:
   - `(work, timestamp)` 联合索引

3. **CrawlSession 表**:
   - `source` 索引
   - `start_time` 索引

### 查询优化

1. 使用 `select_related` 减少查询次数
2. 使用 `only()` 减少数据传输
3. 使用分页避免一次性加载大量数据
4. 使用聚合函数计算汇总数据

## 异常处理

### 自定义异常

1. **WorkNotFoundException**: 作品不存在（404）
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
  "message": "作品不存在",
  "data": null
}
```

## 测试

### 单元测试

- **服务层测试**: AnalyticsService（13个测试用例）
- **视图测试**: 所有 API 端点（9个测试用例）
- **Admin测试**: Admin配置（21个测试用例）
- **测试覆盖率**: 100%

### 运行测试

```bash
# 运行所有测试
python manage.py test test.data_analytics

# 运行特定测试
python manage.py test test.data_analytics.test_analytics_service

# 使用测试脚本
./test/run_data_analytics_tests.sh
```

## 部署

### 数据库迁移

```bash
# 创建迁移
python manage.py makemigrations data_analytics

# 执行迁移到 view_data_db
python manage.py migrate data_analytics --database=view_data_db
```

### URL 配置

在主 URL 配置中添加：

```python
urlpatterns = [
    path('api/data_analytics/', include('data_analytics.urls')),
]
```

### 数据库路由配置

确保在 `xxm_fans_home/db_routers.py` 中配置了正确的路由：

```python
DATABASE_MAPPING = {
    'default': ['main', 'fansDIY', 'song_management'],
    'view_data_db': ['main', 'data_analytics'],
    'songlist_db': ['songlist'],
}
```

## 注意事项

1. **独立数据库**: data_analytics 使用独立的 view_data_db 数据库
2. **循环依赖**: 模型之间使用字符串引用避免循环依赖
3. **缓存失效**: 修改作品数据后需要手动清除相关缓存
4. **分页限制**: 单页最大返回 100 条记录
5. **时间格式**: 所有时间字段使用 ISO 8601 格式

## 未来改进

1. 支持更多平台（抖音、快手等）
2. 添加实时数据推送功能
3. 支持自定义指标计算
4. 添加数据导出功能
5. 优化大数据量查询性能
6. 添加数据可视化图表

## 相关文档

- [REFACTORING_PLAN-2.0.md](./REFACTORING_PLAN-2.0.md) - 重构方案
- [todolist-2.0.md](./todolist-2.0.md) - 任务清单
- [DATA_ANALYTICS阶段3测试报告.md](./DATA_ANALYTICS阶段3测试报告.md) - 测试报告

---

**文档版本**: 1.0
**最后更新**: 2026-01-13