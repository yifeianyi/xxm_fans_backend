# 项目概述

这是一个名为"XXM Fans Home"的音乐粉丝网站项目，采用Django + Vue.js技术栈构建。项目主要功能包括音乐记录管理、歌曲搜索筛选、排行榜展示以及图片处理等。

## 技术架构

- **后端**: Django (Python)
- **前端**: Vue.js 3
- **数据库**: SQLite (开发环境)
- **API**: Django REST Framework
- **前端构建工具**: Vite
- **UI框架**: Element Plus, Vant

## 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用，包含核心模型和API
├── xxm_fans_frontend/       # Vue.js 前端项目
├── static/                  # 静态文件
├── templates/               # Django 模板
├── xxm_fans_home/          # Django 项目配置
├── sqlInit_data/           # 公开数据文件
└── manage.py               # Django 管理脚本
```

## 核心功能模块

1. **音乐管理**:
   - 歌曲信息管理 (Songs)
   - 演唱记录管理 (SongRecord)
   - 曲风分类管理 (Style)
   - 歌曲与曲风关联 (SongStyle)

2. **前端展示**:
   - 歌曲列表与搜索
   - 演唱记录详情
   - 排行榜展示
   - 响应式设计支持移动端

## 开发环境搭建

### 后端环境

1. 创建并激活虚拟环境:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   # source venv/bin/activate
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 环境配置:
   ```bash
   cp env.example .env
   # 编辑 .env 文件设置环境变量
   ```

4. 数据库迁移:
   ```bash
   python manage.py migrate
   ```

5. 运行开发服务器:
   ```bash
   python manage.py runserver
   ```

### 前端环境

1. 安装依赖:
   ```bash
   cd xxm_fans_frontend
   npm install
   ```

2. 运行开发服务器:
   ```bash
   npm run dev
   ```

## 实用脚本

- `download_img.py`: 下载图片
- `compress_images.py`: 压缩图片
- `import_public_data.py`: 导入公开数据
- `export_public_data.py`: 导出公开数据

## API接口

主要REST API接口包括:
- `/api/songs/`: 歌曲列表，支持搜索、分页和排序
- `/api/song-records/<song_id>/`: 特定歌曲的演唱记录
- `/api/styles/`: 曲风列表
- `/api/top-songs/`: 排行榜数据
- `/api/random-song/`: 随机歌曲

## 部署注意事项

1. 设置生产环境变量 (`.env`文件)
2. 设置 `DJANGO_DEBUG=False`
3. 配置适当的 `ALLOWED_HOSTS`
4. 使用安全的 `SECRET_KEY`