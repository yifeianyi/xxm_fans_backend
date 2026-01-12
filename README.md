# 小满虫之家——XXM_Fans_Home 后端

一个基于 Django 5.2.3 构建的音乐粉丝网站后端系统，提供完整的音乐管理、粉丝二创作品管理以及创新的模板化歌单管理 API。

## 🎯 项目亮点

- **🎵 完整的音乐管理系统**：歌曲信息、演唱记录、曲风分类、标签管理一体化
- **🎨 粉丝二创平台**：精选二创作品展示和合集管理
- **⚡ 模板化歌单系统**：配置驱动的动态模型创建，一行代码添加新歌手
- **🚀 高性能架构**：多数据库路由、RESTful API 设计
- **📈 性能测试**：内置完整的 Locust 性能测试套件

## 🛠️ 技术栈

- **框架**: Django 5.2.3
- **API**: Django REST Framework 3.15.2
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **多数据库**: 支持 default、view_data_db、songlist_db 三个独立数据库
- **缓存**: Redis (可选)
- **其他**: python-dotenv, Pillow, django-cors-headers, requests

## 📂 项目结构

```
xxm_fans_backend/
├── main/                          # Django 主应用
│   ├── models.py                 # 核心数据模型
│   ├── views.py                  # API视图
│   ├── serializers.py            # DRF序列化器
│   ├── db_router.py              # 数据库路由
│   └── management/               # 自定义管理命令
├── fansDIY/                       # 粉丝二创应用
│   ├── models.py                 # Collection, Work模型
│   └── views.py                  # 二创作品API
├── songlist/                      # 模板化歌单应用 ⭐
│   ├── models.py                 # 动态模型创建（配置驱动）
│   ├── views.py                  # 配置驱动API
│   ├── admin.py                  # 动态Admin注册
│   └── management/               # 数据迁移脚本
├── xxm_fans_home/                 # Django项目配置
│   ├── settings.py               # 多数据库配置
│   ├── db_routers.py             # 数据库路由器
│   └── urls.py                   # URL路由
├── static/                        # 静态文件
├── templates/                     # Django模板
├── tools/                         # 实用工具脚本
├── test/                          # 性能测试
├── doc/                           # 项目文档
└── manage.py                      # Django管理脚本
```

## 🎬 快速开始

### 环境要求

- Python 3.8+

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

# 迁移songlist数据库
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

## 💡 核心功能

### 音乐管理系统

- **歌曲信息管理** (Songs): 歌曲基本信息、封面、发布时间
- **演唱记录管理** (SongRecord): 演唱会记录、视频链接、BV号
- **曲风分类管理** (Style): 音乐风格分类体系
- **标签管理** (Tag): 多维度标签系统
- **推荐语管理** (Recommendation): 个性化推荐内容
- **网站设置** (SiteSettings): 全局配置管理
- **数据分析** (WorkStatic, WorkMetricsHour, CrawlSession): 数据分析相关模型

### 粉丝二创平台

- **合集管理** (Collection): 二创作品合集分类
- **作品管理** (Work): 单个二创作品信息

### 🌟 模板化歌单系统（核心创新）

#### 设计理念
通过配置驱动和动态模型创建，实现零代码重复的歌单管理系统。

#### 核心特性
- **一行配置添加歌手**：只需在配置字典中添加一行
- **自动生成一切**：模型、Admin、API全部自动生成
- **独立权限管理**：每个歌手拥有独立的数据库表和权限
- **统一API接口**：通过 `artist` 参数区分不同歌手

#### 配置示例

```python
# songlist/models.py
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
    'newartist': '新歌手',  # 只需添加这一行
}
```

#### 运行迁移

```bash
python manage.py makemigrations songlist
python manage.py migrate songlist --database=songlist_db
```

系统自动创建：
- `NewArtistSong` 模型类
- `NewArtistSiteSetting` 模型类
- `songlist_newartistsong` 数据库表
- `songlist_newartistsitesetting` 数据库表
- Admin后台模块
- 所有API接口

#### API使用

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

## 🔌 API接口

### 音乐管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/songs/` | GET | 歌曲列表（支持搜索、分页、排序） |
| `/api/songs/{id}/records/` | GET | 演唱记录 |
| `/api/styles/` | GET | 曲风列表 |
| `/api/tags/` | GET | 标签列表 |
| `/api/top_songs/` | GET | 排行榜 |
| `/api/random-song/` | GET | 随机歌曲 |
| `/api/recommendation/` | GET | 推荐语 |

### 粉丝二创

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/fansDIY/collections/` | GET | 合集列表 |
| `/api/fansDIY/collections/{id}/` | GET | 合集详情 |
| `/api/fansDIY/works/` | GET | 作品列表 |
| `/api/fansDIY/works/{id}/` | GET | 作品详情 |

### 模板化歌单

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/songlist/songs/?artist=youyou` | GET | 歌曲列表（按歌手） |
| `/api/songlist/languages/?artist=youyou` | GET | 语言列表（按歌手） |
| `/api/songlist/styles/?artist=youyou` | GET | 曲风列表（按歌手） |
| `/api/songlist/random/?artist=youyou` | GET | 随机歌曲（按歌手） |
| `/api/songlist/settings/?artist=youyou` | GET | 网站设置（按歌手） |

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

- **[songlist独立表架构说明.md](doc/songlist独立表架构说明.md)** - 模板化歌单系统完整文档
- **[API文档.md](doc/API文档.md)** - API接口详细文档
- **[ADMIN功能文档.md](doc/ADMIN功能文档.md)** - Admin功能说明
- **[项目结构重构方案.md](doc/项目结构重构方案.md)** - 项目架构设计

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
- 不能修改 SongRecord 和 Songs 核心模型
- 遵循现有代码风格
- 保持 API 向后兼容

### Songlist扩展
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

Admin后台提供：
- 歌曲管理
- 演唱记录管理
- 曲风和标签管理
- 粉丝二创作品管理
- 歌单管理（每个歌手独立模块）
- 网站设置管理

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