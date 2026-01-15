# 小满虫之家——XXM_Fans_Home 后端

一个基于 Django 5.2.3 构建的音乐粉丝网站后端系统，提供两套歌单解决方案：**简易模板化歌单系统**和**丰富多样化粉丝站系统**。

## 🎯 项目亮点

### 🎵 简易模板化歌单系统
- **⚡ 快速部署**：一行配置添加新歌手，零代码重复
- **🔧 动态模型创建**：自动生成模型、Admin、API
- **📦 独立权限管理**：每个歌手拥有独立的数据库表和权限
- **🚀 轻量级设计**：适合快速搭建简单的歌单展示页面
- **📋 基础信息**：歌曲名称、原唱歌手、语言、曲风、备注

### 🌟 丰富多样化粉丝站系统
- **🎨 完整的歌单管理**：歌曲信息、演唱记录、曲风分类、标签管理一体化
- **🎯 粉丝二创平台**：精选二创作品展示和合集管理
- **📈 数据分析系统**：工作统计、小时级指标、爬取会话管理
- **🔍 深度数据交互**：支持搜索、筛选、排序、排行榜等功能
- **📊 丰富的歌单信息**：
  - 歌曲基本信息（名称、原唱、语言、曲风、标签、封面、发布时间）
  - 演唱记录（演唱会记录、视频链接、BV号、封面图）
  - 多维度分类（曲风、标签、语言）
  - 演唱统计（演唱次数、最后演唱时间）
  - 排行榜功能（支持不同时间范围）
  - 随机歌曲（支持筛选条件）

### 🏗️ 技术架构
- **分层架构设计**：models → services → api → admin
- **RESTful API**：统一的响应格式和异常处理
- **多数据库支持**：灵活的数据库路由配置
- **高性能缓存**：Redis缓存支持
- **完整测试套件**：内置 Locust 性能测试

## 🛠️ 技术栈

- **框架**: Django 5.2.3
- **API**: Django REST Framework 3.15.2
- **数据库**: SQLite (开发) / PostgreSQL (生产建议)
- **缓存**: Redis
- **其他**: python-dotenv, Pillow, django-cors-headers, requests

## 📂 项目结构

```
xxm_fans_backend/
├── core/                          # 核心模块 - 提供跨应用共享的功能
│   ├── cache.py                   # 缓存管理
│   ├── exceptions.py              # 异常类定义
│   ├── responses.py               # 统一响应格式
│   └── utils/                     # 工具函数
│
├── 🎵 简易模板化歌单系统
│   └── songlist/                  # 模板化歌单应用 ⭐
│       ├── models.py              # 动态模型创建（配置驱动）
│       ├── views.py               # 配置驱动API
│       └── admin.py               # 动态Admin注册
│
├── 🌟 丰富多样化粉丝站系统
│   ├── song_management/           # 歌曲管理应用 ⭐
│   │   ├── models/                # 数据模型（Song, SongRecord, Style, Tag）
│   │   ├── services/              # 业务逻辑层
│   │   ├── api/                   # API视图和序列化器
│   │   ├── admin/                 # Admin后台配置
│   │   ├── forms.py               # 表单定义
│   │   └── urls.py                # URL配置
│   ├── fansDIY/                   # 粉丝二创应用 ⭐
│   │   ├── models/                # 数据模型（Collection, Work）
│   │   ├── services/              # 业务逻辑层
│   │   ├── api/                   # API视图和序列化器
│   │   ├── admin/                 # Admin后台配置
│   │   ├── forms.py               # 表单定义
│   │   └── urls.py                # URL配置
│   ├── data_analytics/            # 数据分析应用 ⭐
│   │   ├── models/                # 数据模型（WorkStatic, WorkMetricsHour等）
│   │   ├── services/              # 业务逻辑层
│   │   ├── api/                   # API视图和序列化器
│   │   └── admin/                 # Admin后台配置
│   └── site_settings/             # 网站设置应用 ⭐
│       ├── models/                # 数据模型（SiteSettings, Recommendation）
│       ├── services/              # 业务逻辑层
│       ├── api/                   # API视图和序列化器
│       └── admin/                 # Admin后台配置
│
├── static/                        # 静态文件
├── templates/                     # Django模板
│   └── admin/                     # Admin自定义模板
├── xxm_fans_home/                 # Django项目配置
│   ├── settings.py               # 多数据库配置、缓存、日志等
│   ├── urls.py                   # 主URL路由配置
│   └── db_routers.py             # 数据库路由
├── tools/                         # 实用工具脚本
├── test/                          # 性能测试（Locust）
├── doc/                           # 项目文档
├── logs/                          # 日志文件
├── covers/                        # 封面图片
└── manage.py                      # Django管理脚本
```

### 架构说明

**分层架构设计**：
- **models/**: 数据模型层，使用Django ORM
- **services/**: 业务逻辑层，封装复杂操作
- **api/**: API接口层，使用Django REST Framework
- **admin/**: Django Admin后台管理界面

**统一响应格式**：
- 成功响应：`{ code, message, data }`
- 分页响应：`{ code, message, data: { total, page, page_size, results } }`
- 错误响应：`{ code, message, errors }`

**自定义异常**：
- SongNotFoundException、InvalidParameterException
- ArtistNotFoundException、CollectionNotFoundException
- WorkNotFoundException、PermissionDeniedException等

## 🎬 快速开始

### 环境要求

- Python 3.8+
- Redis (可选，用于缓存)

### 安装步骤

#### 1. 克隆项目

```bash
git clone git@gitee.com:yifeianyi/xxm_fans_home.git
cd xxm_fans_home/xxm_fans_backend
```

#### 2. 创建虚拟环境

```bash
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 数据库迁移

```bash
# 迁移默认数据库
python manage.py migrate

# 迁移songlist数据库（如果有）
python manage.py migrate --database=songlist_db
```

#### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

#### 6. 导入初始数据（可选）

```bash
python tools/import_public_data.py
```

### 运行项目

```bash
python manage.py runserver
```

访问: http://127.0.0.1:8000

## 💡 适用场景

### 🎵 简易模板化歌单系统适用场景

**适合**：
- 需要快速搭建简单的歌单展示页面
- 歌手/乐队数量较多且频繁变化
- 只需要基础的歌曲信息展示
- 不需要演唱记录、粉丝二创等复杂功能
- 需要快速迭代和原型开发

**歌单信息丰富度**：⭐⭐
- 歌曲基本信息（名称、原唱、语言、曲风、备注）
- 基础的歌单管理
- 简单的筛选和搜索

**特点**：
- 零代码重复，一行配置添加新歌手
- 自动生成模型、Admin、API
- 独立的数据库表，便于数据隔离
- 轻量级，部署快速

### 🌟 丰富多样化粉丝站系统适用场景

**适合**：
- 需要完整的粉丝站功能
- 需要丰富的歌单信息和管理功能
- 需要演唱记录、粉丝二创作品管理
- 需要数据统计和分析功能
- 需要排行榜、随机歌曲等高级功能
- 需要批量操作和管理功能

**歌单信息丰富度**：⭐⭐⭐⭐⭐
- 完整的歌曲基本信息（名称、原唱、语言、曲风、标签、封面、发布时间）
- 演唱记录（演唱会记录、视频链接、BV号、封面图）
- 多维度分类（曲风、标签、语言）
- 演唱统计（演唱次数、最后演唱时间）
- 排行榜功能（支持不同时间范围）
- 随机歌曲（支持筛选条件）
- 高级搜索、筛选、排序功能
- 批量操作（合并、拆分、批量标记等）

**特点**：
- 完整的数据模型和关联关系
- 丰富的Admin功能
- 强大的搜索、筛选、排序功能
- 支持数据统计和分析
- 适用于需要深度数据管理和粉丝互动的场景

### 🔄 两套歌单系统对比

| 特性 | 简易模板化歌单系统 | 丰富多样化粉丝站系统 |
|------|-------------------|---------------------|
| 歌单信息丰富度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 开发速度 | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ |
| 扩展性 | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ |
| 数据关联 | 简单 | 复杂 |
| 演唱记录 | ❌ | ✅ |
| 粉丝二创 | ❌ | ✅ |
| 数据分析 | ❌ | ✅ |
| 排行榜 | ❌ | ✅ |
| 随机歌曲 | ✅（基础） | ✅（高级筛选） |
| Admin功能 | 基础 | 丰富 |
| 适用场景 | 快速原型、简单歌单 | 完整粉丝站、深度数据管理 |

## 💡 核心功能

### 🎵 模块一：简易模板化歌单系统

**设计理念**：
通过配置驱动和动态模型创建，实现零代码重复的简易歌单管理系统。适用于需要快速添加新歌手/乐队、只需基础歌曲信息展示的场景。

**核心特性**：
- **一行配置添加歌手**：只需在配置字典中添加一行
- **自动生成一切**：模型、Admin、API全部自动生成
- **独立权限管理**：每个歌手拥有独立的数据库表和权限
- **统一API接口**：通过 `artist` 参数区分不同歌手
- **轻量级设计**：适合简单的歌单展示需求

**歌单信息**：
- 歌曲基本信息（歌曲名称、原唱歌手、语言、曲风、备注）
- 基础的歌单管理
- 简单的随机歌曲功能

**配置示例**：

```python
# songlist/models.py
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
    'newartist': '新歌手',  # 只需添加这一行
}
```

**添加新歌手步骤**：

1. 修改配置
```python
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
    'newartist': '新歌手',
}
```

2. 创建迁移
```bash
python manage.py makemigrations songlist
```

3. 执行迁移
```bash
python manage.py migrate songlist --database=songlist_db
```

系统自动创建：
- `NewArtistSong` 模型类
- `NewArtistSiteSetting` 模型类
- `songlist_newartistsong` 数据库表
- `songlist_newartistsitesetting` 数据库表
- Admin后台模块
- 所有API接口

**API使用**：

```bash
# 获取乐游歌曲
GET /api/songlist/songs/?artist=youyou

# 获取冰洁歌曲
GET /api/songlist/songs/?artist=bingjie

# 获取新歌手歌曲
GET /api/songlist/songs/?artist=newartist

# 获取乐游语言列表
GET /api/songlist/languages/?artist=youyou

# 获取乐游随机歌曲
GET /api/songlist/random/?artist=youyou
```

详细文档: [songlist独立表架构说明.md](doc/songlist独立表架构说明.md)

---

### 🌟 模块二：丰富多样化粉丝站系统

**设计理念**：
基于大量歌手/乐队的数据信息，提供完整的歌单管理、粉丝二创作品管理和数据分析功能。适用于需要深度数据交互、丰富歌单信息和粉丝互动的场景。

**核心功能**：

#### 1. 丰富的歌单管理系统 (song_management)

**歌单信息丰富度**：⭐⭐⭐⭐⭐

- **歌曲信息管理** (Song):
  - 歌曲基本信息（名称、原唱歌手、语言、封面、发布时间）
  - 多维度分类（曲风、标签）
  - 演唱统计（演唱次数、最后演唱时间）

- **演唱记录管理** (SongRecord):
  - 演唱会记录（时间、地点）
  - 视频链接（B站、YouTube等）
  - BV号支持
  - 封面图管理

- **曲风分类管理** (Style):
  - 音乐风格分类体系
  - 批量标记歌曲

- **标签管理** (Tag):
  - 多维度标签系统
  - 批量标记歌曲

**Admin功能**:
- 合并歌曲
- 拆分歌曲
- 批量标记语言
- 批量添加曲风/标签
- 查看演唱记录（可折叠显示）
- BV号导入（按钮形式，位于"增加 演唱记录"左侧）

**批量标记功能优化**:
- 曲风和标签的批量标记功能已改为按钮形式，位于change_list页面工具栏中
- 左右分栏布局：待选歌曲框和已选歌曲框
- 实时搜索功能：在待选框中可直接搜索目标歌曲
- 多种操作方式：添加、移除、全选、清空、双击操作
- 实时计数：显示待选和已选歌曲数量

**核心API功能**:

| 功能 | 说明 |
|------|------|
| 歌曲列表 | 支持搜索、分页、排序、曲风过滤、标签过滤 |
| 演唱记录 | 支持分页查看 |
| 排行榜 | 支持不同时间范围的热歌榜 |
| 随机歌曲 | 支持筛选条件的随机歌曲（高级筛选） |
| 曲风/标签列表 | 返回简单名称数组，便于前端使用 |

#### 2. 粉丝二创平台 (fansDIY)

- **合集管理** (Collection): 二创作品合集分类
- **作品管理** (Work): 单个二创作品信息

**Admin功能**:
- BV号导入
- 封面管理
- 批量标记

#### 3. 数据分析系统 (data_analytics)

- **工作统计** (WorkStatic): 数据统计分析
- **小时级指标** (WorkMetricsHour): 详细指标追踪
- **爬取会话** (CrawlSession): 爬取任务管理

#### 4. 网站设置 (site_settings)

- **网站设置** (SiteSettings): 全局配置管理
- **推荐语管理** (Recommendation): 个性化推荐内容

**与简易模板化歌单系统的对比**：

| 功能 | 简易模板化歌单系统 | 丰富多样化粉丝站系统 |
|------|-------------------|---------------------|
| 歌曲基本信息 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 演唱记录 | ❌ | ✅ |
| 封面图片管理 | ❌ | ✅ |
| 曲风/标签分类 | 基础 | 完整 |
| 演唱统计 | ❌ | ✅ |
| 排行榜 | ❌ | ✅ |
| 随机歌曲 | 基础 | 高级筛选 |
| 搜索/筛选 | 基础 | 高级 |
| 批量操作 | ❌ | ✅ |
| 粉丝二创 | ❌ | ✅ |
| 数据分析 | ❌ | ✅ |

## 🔌 API接口

### 🎵 简易模板化歌单系统 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/songlist/songs/?artist=youyou` | GET | 歌曲列表（按歌手） |
| `/api/songlist/languages/?artist=youyou` | GET | 语言列表（按歌手） |
| `/api/songlist/styles/?artist=youyou` | GET | 曲风列表（按歌手） |
| `/api/songlist/random/?artist=youyou` | GET | 随机歌曲（按歌手） |
| `/api/songlist/settings/?artist=youyou` | GET | 网站设置（按歌手） |

**使用示例**：

```bash
# 获取乐游歌曲
GET /api/songlist/songs/?artist=youyou

# 获取冰洁歌曲
GET /api/songlist/songs/?artist=bingjie

# 获取乐游随机歌曲
GET /api/songlist/random/?artist=youyou
```

---

### 🌟 丰富多样化粉丝站系统 API

#### 音乐管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/songs/` | GET | 歌曲列表（支持搜索、分页、排序、曲风过滤、标签过滤） |
| `/api/songs/<id>/records/` | GET | 演唱记录（支持分页） |
| `/api/styles/` | GET | 曲风列表（返回名称数组） |
| `/api/tags/` | GET | 标签列表（返回名称数组） |
| `/api/top_songs/` | GET | 排行榜（支持时间范围） |
| `/api/random-song/` | GET | 随机歌曲 |

#### 粉丝二创

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/fansDIY/collections/` | GET | 合集列表 |
| `/api/fansDIY/collections/<id>/` | GET | 合集详情 |
| `/api/fansDIY/works/` | GET | 作品列表 |
| `/api/fansDIY/works/<id>/` | GET | 作品详情 |

#### 数据分析

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/data-analytics/` | GET | 数据分析接口 |

#### 网站设置

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/site-settings/` | GET | 网站设置接口 |

**特点**：
- 所有接口支持分页、搜索、排序
- 统一的响应格式
- 完善的异常处理
- 支持多种过滤条件

## ⚡ 性能测试

### 运行测试

```bash
cd test

# Windows
run_performance_test.bat

# Linux/Mac
./run_performance_test.sh
```

### 测试配置

- 并发用户数: 100
- 启动速率: 10 users/second
- 测试时长: 10分钟
- 目标地址: 可配置

### 测试报告

测试完成后生成：
- QPS图表
- 响应时间图表
- 错误率分析
- 详细统计报告

## 🛠️ 工具脚本

### 数据管理

```bash
# 导入公开数据
python tools/import_public_data.py

# 导出公开数据
python tools/export_public_data.py

# 从JSON导入歌曲
python tools/import_songs_from_json.py

# 合并歌曲
python tools/merge_songs.py
```

### 图片处理

```bash
# 下载图片
python tools/download_img.py

# 压缩图片
python tools/compress_images.py

# 更新封面URL
python tools/update_cover_urls.py

# 下载封面
python tools/download_covers.py
```

### B站集成

```bash
# B站视频导入
python tools/bilibili_importer.py

# 演唱记录导入
python tools/import_song_records.py
```

### Songlist专用

```bash
# 迁移到独立表
python manage.py migrate_to_separate_tables
```

## 📚 项目文档

### 🎵 简易模板化歌单系统文档
- **[songlist独立表架构说明.md](doc/songlist独立表架构说明.md)** - 模板化歌单系统完整文档

### 🌟 丰富多样化粉丝站系统文档
- **[song_management应用文档.md](doc/song_management/)** - 歌曲管理应用文档
- **[fansDIY应用文档.md](doc/fansDIY/)** - 粉丝二创应用文档
- **[data_analytics应用文档.md](doc/Data_analyics/)** - 数据分析应用文档
- **[site_settings应用文档.md](doc/site_settings/)** - 网站设置应用文档

### 🏗️ 架构与规范文档
- **[API文档.md](doc/API文档.md)** - API接口详细文档
- **[ADMIN功能文档.md](doc/ADMIN功能文档.md)** - Admin功能说明
- **[项目结构重构方案.md](doc/项目结构重构方案.md)** - 项目架构设计
- **[CORE模块使用文档.md](doc/core/CORE模块使用文档.md)** - 核心模块文档

### 📋 项目管理
- **[todolist.md](doc/todolist.md)** - 项目待办事项
- **[REFACTORING_PLAN-2.0.md](doc/REFACTORING_PLAN-2.0.md)** - 重构计划

## 🚀 部署

### 环境变量

```bash
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_ALLOWED_HOSTS='your-domain.com'
```

### 收集静态文件

```bash
python manage.py collectstatic --noinput
```

### 数据库迁移

```bash
python manage.py migrate
python manage.py migrate --database=songlist_db
```

### Web服务器

推荐使用 Nginx + Gunicorn：

```bash
gunicorn xxm_fans_home.wsgi:application --bind 0.0.0.0:8000
```

## 📝 开发规范

### 提交规范
- 每完成一个功能提交一次 commit
- 编写清晰的功能文档
- 更新 todolist 状态

### 约束条件
- 不能修改 SongRecord 和 Song 核心模型结构
- 遵循现有代码风格
- 保持 API 向后兼容

### 模块选择指南

**何时使用简易模板化歌单系统（songlist）**：
- 需要快速搭建简单的歌单展示页面
- 歌手/乐队数量较多且频繁变化
- 只需要基础的歌曲信息展示（名称、原唱、语言、曲风、备注）
- 不需要演唱记录、粉丝二创等复杂功能
- 需要快速迭代和原型开发

**何时使用丰富多样化粉丝站系统（song_management + fansDIY + data_analytics）**：
- 需要完整的粉丝站功能
- 需要丰富的歌单信息和管理功能
- 需要演唱记录、粉丝二创作品管理
- 需要数据统计和分析功能
- 需要排行榜、随机歌曲等高级功能
- 需要批量操作和管理功能

### Songlist扩展（简易模板化歌单系统）
添加新歌手只需三步：

1. 修改配置
```python
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
    'newartist': '新歌手',
}
```

2. 创建迁移
```bash
python manage.py makemigrations songlist
```

3. 执行迁移
```bash
python manage.py migrate songlist --database=songlist_db
```

完成！所有模型、Admin、API自动生成。

## 🔐 Admin后台

访问 http://127.0.0.1:8000/admin 使用超级用户账号登录。

### 🎵 简易模板化歌单系统管理

- **歌单管理**：每个歌手独立模块
  - 歌曲列表管理
  - 网站设置管理
  - 独立的权限控制

### 🌟 丰富多样化粉丝站系统管理

- **歌曲管理**：
  - 合并歌曲
  - 拆分歌曲
  - 批量标记语言
  - 批量添加曲风/标签
  - 查看演唱记录（可折叠显示）

- **演唱记录管理**：
  - BV号导入（按钮形式，位于"增加 演唱记录"左侧）
  - 封面管理
  - 视频链接管理

- **曲风和标签管理**：
  - 批量标记歌曲
  - 左右分栏布局
  - 实时搜索功能

- **粉丝二创作品管理**：
  - 合集管理
  - 作品管理
  - BV号导入
  - 封面管理

- **网站设置管理**：
  - 全局配置
  - 推荐语管理

### Admin功能优化

**批量标记功能**：
- 曲风和标签的批量标记功能已改为按钮形式，位于change_list页面工具栏中
- 左右分栏布局：待选歌曲框和已选歌曲框
- 实时搜索功能：在待选框中可直接搜索目标歌曲
- 多种操作方式：添加、移除、全选、清空、双击操作
- 实时计数：显示待选和已选歌曲数量

**BV号导入**：
- 按钮形式，位于"增加 演唱记录"左侧
- 支持从B站导入视频信息
- 自动获取封面和视频链接

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

---

⭐ 如果这个项目对你有帮助，请给它一个星标！