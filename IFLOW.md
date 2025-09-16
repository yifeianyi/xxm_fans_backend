# iFlow 上下文说明 (IFLOW.md)

## 项目概述

这是一个名为 "XXM Fans Home" 的音乐粉丝网站项目，采用前后端分离的架构：

*   **后端**: 基于 Python 的 Django 框架。
*   **前端**: 基于 JavaScript 的 Vue.js 框架 (使用 Vite 构建)。
*   **数据库**: 默认使用 SQLite。
*   **主要功能**:
    *   管理音乐歌单、演唱记录和曲风。
    *   提供歌曲搜索、筛选和排行榜功能。
    *   展示演唱历史和相关视频信息。
    *   响应式 Web 界面，适配移动端。

## 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用，包含核心模型和API
├── footprint/               # Django 应用，用于足迹功能
├── xxm_fans_frontend/       # Vue.js 前端项目源码
├── static/                  # Django 静态文件目录
├── templates/               # Django 模板目录
├── xxm_fans_home/          # Django 项目配置目录
├── tools/                   # 一些实用的脚本工具
├── manage.py               # Django 管理脚本
├── requirements.txt        # Python 后端依赖
└── README.md               # 项目说明文件
```

## 后端 (Django)

### 主要模型 (Models)
位于 `main/models.py`:
*   `Songs`: 存储歌单信息（歌曲名、歌手、演唱次数等）。
*   `SongRecord`: 存储每次演唱的记录（关联歌曲、演唱日期、视频链接、备注等）。
*   `Style`: 存储曲风类型。
*   `SongStyle`: 歌曲与曲风的多对多关联表。
*   `ViewBaseMess` 和 `ViewRealTimeInformation`: 用于存储和展示相关视频信息。

### API 接口 (Views & URLs)
*   **API 视图** 位于 `main/views.py`，主要使用 Django REST Framework 实现。
    *   `SongListView`: 获取歌曲列表，支持搜索、分页和排序。
    *   `SongRecordListView`: 获取特定歌曲的演唱记录列表。
    *   `StyleListView`: 获取所有曲风列表。
    *   `top_songs_api`: 获取热门歌曲排行榜。
    *   `random_song_api`: 随机返回一首歌曲。
*   **API 路由** 定义在 `main/urls.py`。

### 配置与依赖
*   **设置**: `xxm_fans_home/settings.py` 包含数据库、静态文件、缓存 (Redis) 和 REST Framework 的配置。
*   **依赖**: `requirements.txt` 列出了所有 Python 依赖项。

### 实用脚本
项目根目录下有多个 Python 脚本用于数据导入、图片处理等任务，例如 `import_public_data.py`, `download_img.py`, `compress_images.py`。

## 前端 (Vue.js)

### 构建与依赖
*   **依赖管理**: 使用 `npm` 管理依赖，配置在 `xxm_fans_frontend/package.json`。
*   **构建工具**: 使用 `Vite` 进行开发和构建。
    *   `npm run dev`: 启动开发服务器。
    *   `npm run build`: 构建生产版本。
    *   `npm run preview`: 预览构建后的应用。

### 主要页面与路由
*   **路由配置**: `xxm_fans_frontend/src/router/index.js` 定义了前端路由。
    *   `/songs`: 歌曲列表和排行榜 (由 `SongTabs` 组件实现)。
    *   `/footprint`: 足迹页面。
*   **核心组件**:
    *   `SongTabs.vue`: 歌曲列表和排行榜标签页。
    *   `SongList.vue`: 歌曲列表展示。
    *   `TopChart.vue`: 排行榜展示。
    *   `RecordList.vue`: 特定歌曲的演唱记录列表。
    *   `WorkTimeline.vue` 和 `WorkCollectionList.vue`: 足迹页面相关组件。
    *   `NavBar.vue`: 导航栏。

### UI 框架
*   使用 `Element Plus` 和 `Vant` 组件库构建界面。

## 开发与运行

### 后端开发h
1.  **启动虚拟环境**: Linux:`source venv/bin/activate` ,Windows: `venv\Scripts\activate`
2.  **安装依赖**: `pip install -r requirements.txt`
3.  **数据库迁移**: `python manage.py migrate`
4.  **运行服务器**: `python manage.py runserver`

### 前端开发
1.  **进入前端目录**: `cd xxm_fans_frontend`
2.  **安装依赖**: `npm install`
3.  **运行开发服务器**: `npm run dev`

### 配置
项目使用 `.env` 文件管理环境变量（如 `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`），需要从 `env.example` 复制并配置。