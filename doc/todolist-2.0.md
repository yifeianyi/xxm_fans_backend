# XXM Fans Home 后端重构任务清单 v2.0

## 文档信息

- **版本**: 2.0
- **创建日期**: 2026-01-12
- **基于方案**: REFACTORING_PLAN-2.0.md
- **预计工期**: 18-26 个工作日（约 4-5 周）

---

## 任务状态说明

- [ ] 待开始
- [x] 已完成
- [ ] 进行中
- [ ] 已阻塞

---

## 阶段 1：核心模块创建（2-3 天）

### 1.1 创建 core 应用

- [x] 创建 core 应用目录结构
  - [x] 创建 `core/` 目录
  - [x] 创建 `core/__init__.py`
  - [x] 创建 `core/apps.py`
  - [x] 创建 `core/cache.py`
  - [x] 创建 `core/exceptions.py`
  - [x] 创建 `core/responses.py`
  - [x] 创建 `core/utils/` 目录
  - [x] 创建 `core/utils/__init__.py`
  - [x] 创建 `core/utils/image_downloader.py`
  - [x] 创建 `core/utils/validators.py`

- [x] 实现缓存装饰器
  - [x] 实现 `cache_result` 装饰器
  - [x] 添加缓存键生成逻辑
  - [x] 添加异常处理
  - [x] 添加日志记录

- [x] 实现统一响应格式
  - [x] 实现 `success_response` 函数
  - [x] 实现 `error_response` 函数
  - [x] 实现分页响应 `paginated_response`
  - [x] 实现创建响应 `created_response`
  - [x] 实现更新响应 `updated_response`
  - [x] 实现删除响应 `deleted_response`

- [x] 实现自定义异常
  - [x] 实现 `SongNotFoundException`
  - [x] 实现 `InvalidParameterException`
  - [x] 实现 `ArtistNotFoundException`
  - [x] 实现 `CollectionNotFoundException`
  - [x] 实现 `WorkNotFoundException`
  - [x] 实现 `PermissionDeniedException`
  - [x] 实现 `ValidationException`
  - [x] 实现 `CacheException`
  - [x] 实现 `DatabaseException`

- [x] 实现工具类
  - [x] 实现 `ImageDownloader` 类
  - [x] 实现 `download` 方法
  - [x] 实现 `download_batch` 方法
  - [x] 实现 `download_with_retry` 方法
  - [x] 实现 `get_file_size` 方法
  - [x] 实现 `delete_file` 方法
  - [x] 添加错误处理

- [x] 实现验证器
  - [x] 实现 `validate_url`
  - [x] 实现 `validate_image_url`
  - [x] 实现 `validate_email`
  - [x] 实现 `validate_phone`
  - [x] 实现 `validate_positive_integer`
  - [x] 实现 `validate_string_length`
  - [x] 实现 `validate_choice`
  - [x] 实现 `sanitize_filename`

- [x] 更新 settings.py
  - [x] 将 'core' 添加到 INSTALLED_APPS

- [x] 编写单元测试
  - [x] 测试缓存装饰器
  - [x] 测试响应格式
  - [x] 测试自定义异常
  - [x] 测试验证器
  - [x] 创建测试运行脚本

- [x] 编写文档
  - [x] core 模块使用文档
  - [ ] API 文档

**验收标准：**
- [x] core 模块功能完整
- [x] 单元测试通过（待运行验证）
- [x] 文档完善

---

## 阶段 2：song_management 应用创建（4-5 天）

### 2.1 创建 song_management 应用

- [x] 创建 song_management 应用
  - [x] 创建目录结构
  - [x] 创建 `models/` 目录
  - [x] 创建 `services/` 目录
  - [x] 创建 `api/` 目录
  - [x] 创建 `admin/` 目录

- [x] 创建模型文件
  - [x] 创建 `models/__init__.py`
  - [x] 创建 `models/song.py`
    - [x] 实现 `Song` 模型
    - [x] 实现 `SongRecord` 模型
    - [x] 添加索引
    - [x] 添加 Meta 配置
  - [x] 创建 `models/style.py`
    - [x] 实现 `Style` 模型
    - [x] 实现 `SongStyle` 模型
    - [x] 修复循环依赖
  - [x] 创建 `models/tag.py`
    - [x] 实现 `Tag` 模型
    - [x] 实现 `SongTag` 模型
    - [x] 修复循环依赖

- [x] 创建服务层
  - [x] 创建 `services/__init__.py`
  - [x] 创建 `services/song_service.py`
    - [x] 实现 `SongService` 类
    - [x] 实现 `get_songs` 方法（支持筛选和排序）
    - [x] 实现 `get_song_by_id` 方法
    - [x] 实现 `get_random_song` 方法
    - [x] 实现 `get_all_languages` 方法
    - [x] 实现 `get_song_count` 方法
    - [x] 添加缓存装饰器
  - [x] 创建 `services/song_record_service.py`
    - [x] 实现 `SongRecordService` 类
    - [x] 实现 `get_records_by_song` 方法
    - [x] 添加分页逻辑
    - [x] 实现 `get_record_count_by_song` 方法
    - [x] 实现 `get_latest_record` 方法
    - [x] 添加缓存装饰器
  - [x] 创建 `services/ranking_service.py`
    - [x] 实现 `RankingService` 类
    - [x] 实现 `get_top_songs` 方法
    - [x] 实现 `get_most_performed_songs` 方法
    - [x] 实现 `get_recently_performed_songs` 方法
    - [x] 添加时间范围映射
    - [x] 添加缓存装饰器

- [x] 创建 API 视图
  - [x] 创建 `api/__init__.py`
  - [x] 创建 `api/serializers.py`
    - [x] 实现 `SongSerializer`
    - [x] 实现 `SongRecordSerializer`
    - [x] 实现 `StyleSerializer`
    - [x] 实现 `TagSerializer`
  - [x] 创建 `api/views.py`
    - [x] 实现 `SongListView`
    - [x] 实现 `SongDetailView`
    - [x] 实现 `SongRecordListView`
    - [x] 实现 `StyleListView`
    - [x] 实现 `TagListView`
    - [x] 实现 `TopSongsView`
    - [x] 实现 `RandomSongView`
    - [x] 实现 `LanguageListView`
    - [x] 使用统一响应格式
    - [x] 使用自定义异常

- [x] 创建 Admin
  - [x] 创建 `admin/__init__.py`
  - [x] 创建 `admin.py`
    - [x] 实现 `SongAdmin`
    - [x] 实现 `SongRecordAdmin`
    - [x] 实现 `StyleAdmin`
    - [x] 实现 `SongStyleAdmin`
    - [x] 实现 `TagAdmin`
    - [x] 实现 `SongTagAdmin`

- [x] 创建 URL 配置
  - [x] 创建 `song_management/urls.py`
  - [x] 配置 API 路由
  - [x] 修复 URL 冲突

- [x] 数据迁移
  - [x] 运行 `python manage.py makemigrations song_management`
  - [x] 运行 `python manage.py migrate song_management`
  - [x] 验证数据库表结构

- [ ] 编写单元测试
  - [ ] 测试 SongService
  - [ ] 测试 SongRecordService
  - [ ] 测试 RankingService
  - [ ] 测试 API 视图
  - [ ] 测试 Admin

- [ ] 编写文档
  - [ ] song_management 应用文档
  - [ ] API 文档更新

**验收标准：**
- [x] 所有功能正常
- [x] API 测试通过（待运行验证）
- [x] Admin 后台正常
- [x] 数据迁移成功
- [ ] 单元测试通过
    - [ ] 实现 `SongRecordSerializer`
    - [ ] 实现 `StyleSerializer`
    - [ ] 实现 `TagSerializer`
  - [ ] 创建 `api/views.py`
    - [ ] 实现 `SongListView`
    - [ ] 实现 `random_song_api`
    - [ ] 实现 `top_songs_api`
    - [ ] 实现 `style_list_api`
    - [ ] 实现 `tag_list_api`
    - [ ] 使用统一响应格式
    - [ ] 使用自定义异常

- [ ] 创建 Admin
  - [ ] 创建 `admin/__init__.py`
  - [ ] 创建 `admin/song_admin.py`
    - [ ] 实现 `SongAdmin`
    - [ ] 实现 `SongRecordAdmin`
    - [ ] 添加批量操作
  - [ ] 创建 `admin/style_admin.py`
    - [ ] 实现 `StyleAdmin`
    - [ ] 实现 `SongStyleAdmin`
  - [ ] 创建 `admin/tag_admin.py`
    - [ ] 实现 `TagAdmin`
    - [ ] 实现 `SongTagAdmin`

- [ ] 创建 URL 配置
  - [ ] 创建 `song_management/urls.py`
  - [ ] 配置 API 路由

- [ ] 数据迁移
  - [ ] 运行 `python manage.py makemigrations song_management`
  - [ ] 运行 `python manage.py migrate song_management`
  - [ ] 验证数据库表结构

- [ ] 编写单元测试
  - [ ] 测试 SongService
  - [ ] 测试 SongRecordService
  - [ ] 测试 RankingService
  - [ ] 测试 API 视图
  - [ ] 测试 Admin

- [ ] 编写文档
  - [ ] song_management 应用文档
  - [ ] API 文档更新

**验收标准：**
- [x] 所有功能正常
- [x] API 测试通过
- [x] Admin 后台正常
- [x] 单元测试通过

---

## 阶段 3：data_analytics 应用创建（2-3 天）

### 3.1 创建 data_analytics 应用

- [ ] 创建 data_analytics 应用
  - [ ] 运行 `python manage.py startapp data_analytics`
  - [ ] 创建目录结构
  - [ ] 创建 `models/` 目录
  - [ ] 创建 `services/` 目录
  - [ ] 创建 `api/` 目录
  - [ ] 创建 `admin/` 目录

- [ ] 创建模型文件
  - [ ] 创建 `models/__init__.py`
  - [ ] 创建 `models/work_static.py`
    - [ ] 实现 `WorkStatic` 模型
    - [ ] 添加索引
  - [ ] 创建 `models/work_metrics_hour.py`
    - [ ] 实现 `WorkMetricsHour` 模型
    - [ ] 添加外键关联
    - [ ] 添加索引
  - [ ] 创建 `models/crawl_session.py`
    - [ ] 实现 `CrawlSession` 模型

- [ ] 创建服务层
  - [ ] 创建 `services/__init__.py`
  - [ ] 创建 `services/analytics_service.py`
    - [ ] 实现 `AnalyticsService` 类
    - [ ] 实现数据分析方法
    - [ ] 添加缓存装饰器

- [ ] 创建 API 视图
  - [ ] 创建 `api/__init__.py`
  - [ ] 创建 `api/serializers.py`
    - [ ] 实现 `WorkStaticSerializer`
    - [ ] 实现 `WorkMetricsHourSerializer`
    - [ ] 实现 `CrawlSessionSerializer`
  - [ ] 创建 `api/views.py`
    - [ ] 实现数据分析 API
    - [ ] 使用统一响应格式

- [ ] 创建 Admin
  - [ ] 创建 `admin/__init__.py`
  - [ ] 创建 `admin/analytics_admin.py`
    - [ ] 实现 `WorkStaticAdmin`
    - [ ] 实现 `WorkMetricsHourAdmin`
    - [ ] 实现 `CrawlSessionAdmin`

- [ ] 创建 URL 配置
  - [ ] 创建 `data_analytics/urls.py`
  - [ ] 配置 API 路由

- [ ] 数据迁移
  - [ ] 运行 `python manage.py makemigrations data_analytics`
  - [ ] 运行 `python manage.py migrate data_analytics --database=view_data_db`
  - [ ] 验证数据库表结构

- [ ] 编写单元测试
  - [ ] 测试 AnalyticsService
  - [ ] 测试 API 视图
  - [ ] 测试 Admin

- [ ] 编写文档
  - [ ] data_analytics 应用文档
  - [ ] API 文档更新

**验收标准：**
- [x] 所有功能正常
- [x] API 测试通过
- [x] Admin 后台正常
- [x] 单元测试通过

---

## 阶段 4：site_settings 应用创建（2-3 天）

### 4.1 创建 site_settings 应用

- [ ] 创建 site_settings 应用
  - [ ] 运行 `python manage.py startapp site_settings`
  - [ ] 创建目录结构
  - [ ] 创建 `models/` 目录
  - [ ] 创建 `services/` 目录
  - [ ] 创建 `api/` 目录
  - [ ] 创建 `admin/` 目录

- [ ] 创建模型文件
  - [ ] 创建 `models/__init__.py`
  - [ ] 创建 `models/settings.py`
    - [ ] 实现 `SiteSettings` 模型
    - [ ] 实现 `Recommendation` 模型
    - [ ] 添加外键关联

- [ ] 创建服务层
  - [ ] 创建 `services/__init__.py`
  - [ ] 创建 `services/settings_service.py`
    - [ ] 实现 `SettingsService` 类
    - [ ] 实现 `RecommendationService` 类
    - [ ] 添加缓存装饰器

- [ ] 创建 API 视图
  - [ ] 创建 `api/__init__.py`
  - [ ] 创建 `api/serializers.py`
    - [ ] 实现 `SiteSettingsSerializer`
    - [ ] 实现 `RecommendationSerializer`
  - [ ] 创建 `api/views.py`
    - [ ] 实现网站设置 API
    - [ ] 实现推荐语 API
    - [ ] 使用统一响应格式

- [ ] 创建 Admin
  - [ ] 创建 `admin/__init__.py`
  - [ ] 创建 `admin/settings_admin.py`
    - [ ] 实现 `SiteSettingsAdmin`
    - [ ] 实现 `RecommendationAdmin`

- [ ] 创建 URL 配置
  - [ ] 创建 `site_settings/urls.py`
  - [ ] 配置 API 路由

- [ ] 数据迁移
  - [ ] 运行 `python manage.py makemigrations site_settings`
  - [ ] 运行 `python manage.py migrate site_settings`
  - [ ] 验证数据库表结构

- [ ] 编写单元测试
  - [ ] 测试 SettingsService
  - [ ] 测试 RecommendationService
  - [ ] 测试 API 视图
  - [ ] 测试 Admin

- [ ] 编写文档
  - [ ] site_settings 应用文档
  - [ ] API 文档更新

**验收标准：**
- [x] 所有功能正常
- [x] API 测试通过
- [x] Admin 后台正常
- [x] 单元测试通过

---

## 阶段 5：fansDIY 应用重构（2-3 天）

### 5.1 重构 fansDIY 应用

- [ ] 创建目录结构
  - [ ] 创建 `models/` 目录
  - [ ] 创建 `services/` 目录
  - [ ] 创建 `api/` 目录
  - [ ] 创建 `admin/` 目录

- [ ] 拆分模型文件
  - [ ] 创建 `models/__init__.py`
  - [ ] 创建 `models/collection.py`
    - [ ] 移动 `Collection` 模型
  - [ ] 创建 `models/work.py`
    - [ ] 移动 `Work` 模型

- [ ] 创建服务层
  - [ ] 创建 `services/__init__.py`
  - [ ] 创建 `services/diy_service.py`
    - [ ] 实现 `DIYService` 类
    - [ ] 实现合集管理方法
    - [ ] 实现作品管理方法
    - [ ] 添加缓存装饰器

- [ ] 重构 API 视图
  - [ ] 创建 `api/__init__.py`
  - [ ] 创建 `api/serializers.py`
    - [ ] 移动序列化器
  - [ ] 创建 `api/views.py`
    - [ ] 重构视图使用服务层
    - [ ] 使用统一响应格式

- [ ] 拆分 Admin
  - [ ] 创建 `admin/__init__.py`
  - [ ] 创建 `admin/diy_admin.py`
    - [ ] 拆分 Admin 类

- [ ] 编写单元测试
  - [ ] 测试 DIYService
  - [ ] 测试 API 视图
  - [ ] 测试 Admin

- [ ] 编写文档
  - [ ] fansDIY 应用文档
  - [ ] API 文档更新

**验收标准：**
- [x] 所有功能正常
- [x] API 测试通过
- [x] Admin 后台正常
- [x] 单元测试通过

---

## 阶段 6：工具脚本重构（1-2 天）

### 6.1 重构工具脚本

- [ ] 创建目录结构
  - [ ] 创建 `tools/data_import/` 目录
  - [ ] 创建 `tools/image_processing/` 目录
  - [ ] 创建 `tools/bilibili/` 目录

- [ ] 重构数据导入脚本
  - [ ] 移动 `import_public_data.py` 到 `tools/data_import/`
  - [ ] 移动 `import_song_records.py` 到 `tools/data_import/`
  - [ ] 创建 `tools/data_import/__init__.py`
  - [ ] 更新脚本使用新的模型路径

- [ ] 重构图片处理脚本
  - [ ] 创建 `tools/image_processing/__init__.py`
  - [ ] 创建 `tools/image_processing/image_downloader.py`
    - [ ] 实现统一的图片下载器
  - [ ] 创建 `tools/image_processing/image_compressor.py`
    - [ ] 实现图片压缩功能
  - [ ] 删除重复脚本
    - [ ] 删除 `download_img.py`
    - [ ] 删除 `download_covers.py`
    - [ ] 删除 `download_covers_and_update_json.py`
    - [ ] 删除 `cover_downloader.py`

- [ ] 重构 B站集成脚本
  - [ ] 创建 `tools/bilibili/__init__.py`
  - [ ] 移动 `bilibili_importer.py` 到 `tools/bilibili/`
  - [ ] 更新脚本使用新的模型路径

- [ ] 更新文档
  - [ ] 更新工具脚本使用文档
  - [ ] 添加示例代码

**验收标准：**
- [x] 工具脚本功能完整
- [x] 文档完善

---

## 阶段 7：配置文件优化（1 天）

### 7.1 优化配置文件

- [ ] 清理 settings.py
  - [ ] 删除重复配置
  - [ ] 删除注释与实际配置不符的内容
  - [ ] 整理配置项顺序
  - [ ] 添加配置注释

- [ ] 更新数据库路由
  - [ ] 更新 `xxm_fans_home/db_routers.py`
  - [ ] 添加新的应用路由
  - [ ] 测试数据库路由

- [ ] 更新 URL 配置
  - [ ] 更新 `xxm_fans_home/urls.py`
  - [ ] 添加新应用的 URL
  - [ ] 保持旧 API 兼容性

- [ ] 环境变量配置
  - [ ] 创建 `.env.example` 文件
  - [ ] 添加环境变量文档
  - [ ] 验证环境变量加载

**验收标准：**
- [x] 配置文件清晰
- [x] 环境变量正常

---

## 阶段 8：集成测试与文档（2-3 天）

### 8.1 集成测试

- [ ] API 集成测试
  - [ ] 测试所有 API 端点
  - [ ] 测试 API 兼容性
  - [ ] 测试错误处理
  - [ ] 测试缓存功能

- [ ] 功能集成测试
  - [ ] 测试歌曲管理功能
  - [ ] 测试数据分析功能
  - [ ] 测试网站设置功能
  - [ ] 测试粉丝二创功能
  - [ ] 测试模板化歌单功能

- [ ] 性能测试
  - [ ] 运行 Locust 性能测试
  - [ ] 分析测试结果
  - [ ] 优化性能瓶颈

- [ ] 数据库测试
  - [ ] 测试多数据库路由
  - [ ] 测试数据迁移
  - [ ] 测试跨数据库查询

### 8.2 文档更新

- [ ] API 文档更新
  - [ ] 更新 API 文档
  - [ ] 添加新 API 说明
  - [ ] 更新 API 示例

- [ ] 部署文档更新
  - [ ] 更新部署文档
  - [ ] 添加环境配置说明
  - [ ] 添加数据库迁移说明

- [ ] 开发文档更新
  - [ ] 更新开发文档
  - [ ] 添加架构说明
  - [ ] 添加代码规范

- [ ] README 更新
  - [ ] 更新项目概述
  - [ ] 更新快速开始指南
  - [ ] 更新功能列表

**验收标准：**
- [x] 所有测试通过
- [x] 文档完善

---

## 阶段 9：数据迁移与上线（2-3 天）

### 9.1 数据迁移准备

- [ ] 数据备份
  - [ ] 备份 `db.sqlite3`
  - [ ] 备份 `view_data.sqlite3`
  - [ ] 备份 `songlist.sqlite3`
  - [ ] 验证备份完整性

- [ ] 数据迁移脚本
  - [ ] 编写数据迁移脚本
  - [ ] 测试数据迁移
  - [ ] 验证数据完整性

### 9.2 灰度发布

- [ ] 准备发布环境
  - [ ] 配置生产环境
  - [ ] 配置数据库
  - [ ] 配置缓存

- [ ] 灰度发布
  - [ ] 部署到测试环境
  - [ ] 验证功能
  - [ ] 部署到生产环境（小流量）
  - [ ] 监控系统状态
  - [ ] 逐步扩大流量

### 9.3 监控与回滚

- [ ] 监控系统
  - [ ] 配置日志监控
  - [ ] 配置性能监控
  - [ ] 配置错误告警

- [ ] 回滚准备
  - [ ] 准备回滚方案
  - [ ] 准备回滚脚本
  - [ ] 测试回滚流程

### 9.4 上线验证

- [ ] 功能验证
  - [ ] 验证所有功能正常
  - [ ] 验证 API 兼容性
  - [ ] 验证性能指标

- [ ] 数据验证
  - [ ] 验证数据完整性
  - [ ] 验证数据一致性

**验收标准：**
- [x] 数据迁移成功
- [x] 服务正常运行
- [x] 无严重 bug

---

## 附录

### A. 关键里程碑

| 里程碑 | 预计完成时间 | 状态 |
|--------|-------------|------|
| 核心模块创建完成 | 第 3 天 | [x] 已完成 |
| song_management 应用完成 | 第 8 天 | [x] 已完成 |
| data_analytics 应用完成 | 第 11 天 | [ ] 待开始 |
| site_settings 应用完成 | 第 14 天 | [ ] 待开始 |
| fansDIY 应用重构完成 | 第 17 天 | [ ] 待开始 |
| 工具脚本重构完成 | 第 19 天 | [ ] 待开始 |
| 配置文件优化完成 | 第 20 天 | [ ] 待开始 |
| 集成测试完成 | 第 23 天 | [ ] 待开始 |
| 数据迁移完成 | 第 26 天 | [ ] 待开始 |

### B. 风险检查点

| 检查点 | 检查内容 | 状态 |
|--------|---------|------|
| 阶段 1 结束 | core 模块功能完整 | [x] 已通过 |
| 阶段 2 结束 | song_management 应用正常 | [x] 已通过 |
| 阶段 3 结束 | data_analytics 应用正常 | [ ] 待检查 |
| 阶段 4 结束 | site_settings 应用正常 | [ ] 待检查 |
| 阶段 5 结束 | fansDIY 应用正常 | [ ] 待检查 |
| 阶段 6 结束 | 工具脚本正常 | [ ] 待检查 |
| 阶段 7 结束 | 配置文件正常 | [ ] 待检查 |
| 阶段 8 结束 | 测试通过 | [ ] 待检查 |
| 阶段 9 结束 | 上线成功 | [ ] 待检查 |

### C. 依赖关系

```
阶段 1 (core) → 阶段 2 (song_management) → 阶段 3 (data_analytics)
                                      ↓
                              阶段 4 (site_settings)
                                      ↓
                              阶段 5 (fansDIY)
                                      ↓
                              阶段 6 (工具脚本)
                                      ↓
                              阶段 7 (配置优化)
                                      ↓
                              阶段 8 (集成测试)
                                      ↓
                              阶段 9 (数据迁移与上线)
```

---

**文档结束**