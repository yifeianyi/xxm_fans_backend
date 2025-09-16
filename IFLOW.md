# iFlow 上下文文档 (IFLOW.md)

## 项目概述

这是一个名为 "XXM Fans Home" 的音乐粉丝网站项目，使用 Django (Python) 作为后端框架，Vue.js 作为前端框架构建。

### 主要技术栈
- **后端**: Django, Django REST Framework, SQLite (默认数据库), Redis (缓存)
- **前端**: Vue.js 3 (Composition API), Vite, Element Plus, Vant (移动端组件库)
- **部署/构建**: pip (Python 依赖管理), npm (前端依赖管理), Vite (前端构建工具)

### 项目架构
项目采用前后端分离的架构：
- `main/`: Django 主应用，包含核心模型 (Models)、视图 (Views/APIs)、URL 路由。
- `footprint/`: 另一个 Django 应用，可能用于记录足迹或其他功能。
- `xxm_fans_frontend/`: Vue.js 前端项目，包含所有前端源代码和构建配置。
- `static/` 和 `templates/`: Django 用于服务静态文件和模板的目录。
- `xxm_fans_home/`: Django 项目配置目录。

核心功能围绕音乐 (`Songs`)、演唱记录 (`SongRecord`) 和曲风 (`Style`) 管理展开，提供 API 接口供前端调用，并通过 Vue.js 前端展示数据，包括歌单、排行榜、歌曲搜索等。

## 构建与运行

### 后端 (Django)

1.  **环境准备**:
    *   确保安装了 Python 3.x 和 pip。
    *   (推荐) 创建并激活 Python 虚拟环境：`python -m venv venv` 然后 `source venv/bin/activate` (Linux/Mac) 或 `venv\Scripts\activate` (Windows)。
2.  **安装依赖**:
    *   在项目根目录下运行：`pip install -r requirements.txt`
3.  **环境配置**:
    *   复制 `env.example` 为 `.env` 文件并进行配置 (例如设置 `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`)。
4.  **数据库迁移**:
    *   运行：`python manage.py migrate`
5.  **运行开发服务器**:
    *   运行：`python manage.py runserver`
    *   默认地址: `http://127.0.0.1:8000/`

### 前端 (Vue.js)

1.  **环境准备**:
    *   确保安装了 Node.js 和 npm。
2.  **安装依赖**:
    *   进入 `xxm_fans_frontend` 目录：`cd xxm_fans_frontend`
    *   运行：`npm install`
3.  **运行开发服务器**:
    *   在 `xxm_fans_frontend` 目录下运行：`npm run dev`
    *   默认地址: `http://localhost:5173/`
4.  **构建生产版本**:
    *   在 `xxm_fans_frontend` 目录下运行：`npm run build`
    *   构建产物将位于 `xxm_fans_frontend/dist/` 目录。

### 实用脚本

项目根目录下包含一些用于数据管理和图片处理的 Python 脚本，例如：
- `import_public_data.py`: 导入公开数据。
- `download_img.py`: 下载图片。
- `compress_images.py`: 压缩图片。
根据 `README.md` 中的说明执行这些脚本。

## 开发约定

### 后端 (Django)

- **模型 (Models)**: 模型定义在 `main/models.py` 和 `footprint/models.py` 中。遵循 Django ORM 的惯例。
- **API (Views)**: API 视图使用 Django REST Framework 的 `@api_view` 装饰器定义在 `main/views.py` 中，返回 JSON 格式数据。
- **URL 路由**: URL 配置在 `main/urls.py` 和 `xxm_fans_home/urls.py` 中。
- **缓存**: 使用 Redis 作为缓存后端，通过 `django.core.cache` 模块在视图中实现缓存。
- **静态文件和模板**: 静态文件放在 `static/` 目录，模板文件放在 `templates/` 目录。

### 前端 (Vue.js)

- **框架**: 使用 Vue 3 Composition API。
- **UI 库**: 桌面端使用 Element Plus，移动端使用 Vant。
- **路由**: 使用 `vue-router` 进行页面路由管理，配置在 `xxm_fans_frontend/src/router/index.js`。
- **构建工具**: 使用 Vite 进行开发服务器启动和生产构建。
- **目录结构**: 组件位于 `xxm_fans_frontend/src/components/`，页面视图位于 `xxm_fans_frontend/src/views/`。