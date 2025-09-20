# XXM Fans Home 项目技术文档

## 1. 项目概述

XXM Fans Home 是一个基于 Django + Vue.js 的音乐粉丝网站项目，主要用于管理咻咻满的演唱记录和展示相关数据。项目主要功能包括音乐记录管理、歌曲搜索筛选、排行榜展示、精选二创作品展示以及图片处理等。

## 2. 技术架构

### 2.1 后端技术栈
- **框架**: Django 5.2.3 + Django REST Framework 3.15.2
- **数据库**: SQLite (开发环境)
- **编程语言**: Python 3.x
- **API**: RESTful API
- **缓存**: LocMemCache (开发环境) / Redis (生产环境可选)
- **环境管理**: python-dotenv 1.0.1

### 2.2 前端技术栈
- **框架**: Vue.js 3 + Element Plus
- **构建工具**: Vite 6.3.5
- **UI框架**: Element Plus 2.10.2
- **HTTP客户端**: axios 1.10.0
- **其他组件**: @lucky-canvas/vue 0.1.11
- **路由**: vue-router 4.5.1

### 2.3 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用，包含核心模型和API
├── xxm_fans_frontend/       # Vue.js 前端项目
├── fansDIY/                 # 粉丝二创作品管理应用
├── static/                  # 静态文件
├── templates/               # Django 模板
├── xxm_fans_home/           # Django 项目配置
├── sqlInit_data/            # 公开数据文件
├── doc/                     # 项目文档
├── tools/                   # 实用工具脚本
└── manage.py                # Django 管理脚本
```

## 3. 核心功能模块

### 3.1 音乐管理 (main应用)

#### 3.1.1 模型设计

1. **Songs (歌曲信息)**
   - song_name: 歌曲名
   - singer: 原唱
   - last_performed: 最近一次演唱时间
   - perform_count: 演唱次数
   - language: 语言

2. **SongRecord (演唱记录)**
   - song: 外键关联Songs
   - performed_at: 演唱日期
   - url: 视频链接
   - notes: 备注
   - cover_url: 封面图片地址

3. **Style (曲风分类)**
   - name: 曲风名称

4. **Tag (标签)**
   - name: 标签名称

5. **SongStyle (歌曲与曲风关联)**
   - song: 外键关联Songs
   - style: 外键关联Style

6. **SongTag (歌曲与标签关联)**
   - song: 外键关联Songs
   - tag: 外键关联Tag

7. **Recommendation (推荐语)**
   - content: 推荐语内容
   - recommended_songs: 多对多关联Songs
   - is_active: 是否激活显示

#### 3.1.2 API接口

1. **歌曲列表接口**
   - URL: `/api/songs/`
   - 方法: GET
   - 参数:
     - q: 搜索关键词（歌曲名或歌手）
     - page: 页码
     - limit: 每页数量
     - styles: 曲风筛选
     - tags: 标签筛选
     - language: 语言筛选
     - ordering: 排序字段

2. **歌曲演唱记录接口**
   - URL: `/api/songs/{song_id}/records/`
   - 方法: GET
   - 参数:
     - page: 页码
     - page_size: 每页数量

3. **曲风列表接口**
   - URL: `/api/styles/`
   - 方法: GET

4. **标签列表接口**
   - URL: `/api/tags/`
   - 方法: GET

5. **热歌榜接口**
   - URL: `/api/top_songs/`
   - 方法: GET
   - 参数:
     - range: 时间范围（all, 1m, 3m, 1y）
     - limit: 返回歌曲数量

6. **随机歌曲接口**
   - URL: `/api/random-song/`
   - 方法: GET

7. **推荐语接口**
   - URL: `/api/recommendation/`
   - 方法: GET

### 3.2 粉丝二创作品管理 (fansDIY应用)

#### 3.2.1 模型设计

1. **Collection (合集)**
   - name: 合集名称
   - works_count: 作品数量
   - display_order: 显示顺序
   - position: 位置
   - created_at: 创建时间
   - updated_at: 更新时间

2. **Work (作品)**
   - collection: 外键关联Collection
   - title: 作品标题
   - cover_url: 封面图片地址
   - view_url: 观看链接
   - author: 作者
   - notes: 备注
   - display_order: 显示顺序
   - position: 位置

#### 3.2.2 API接口

1. **合集列表接口**
   - URL: `/api/fansDIY/collections/`
   - 方法: GET
   - 参数:
     - page: 页码
     - limit: 每页数量

2. **合集详情接口**
   - URL: `/api/fansDIY/collections/{collection_id}/`
   - 方法: GET

3. **作品列表接口**
   - URL: `/api/fansDIY/works/`
   - 方法: GET
   - 参数:
     - page: 页码
     - limit: 每页数量
     - collection: 合集ID

4. **作品详情接口**
   - URL: `/api/fansDIY/works/{work_id}/`
   - 方法: GET

## 4. 缓存机制

项目使用Django缓存框架来提高API响应速度，减轻数据库压力。开发环境使用LocMemCache，生产环境可配置Redis。

### 4.1 缓存策略
- **歌曲列表接口**: 缓存10分钟
- **歌曲演唱记录接口**: 缓存10分钟
- **曲风列表接口**: 缓存1小时
- **标签列表接口**: 缓存1小时
- **推荐语接口**: 缓存5分钟

### 4.2 缓存键设计
- 歌曲列表: `song_list_api:{query}:{page_num}:{page_size}:{ordering}:{styles}:{tags}:{languages}`
- 歌曲演唱记录: `song_records:{song_id}:{page_num}:{page_size}`
- 曲风列表: `style_list_simple`
- 标签列表: `tag_list_simple`
- 推荐语: `active_recommendation`

## 5. 前端功能模块

### 5.1 歌曲列表与搜索
- 支持按歌曲名、歌手、曲风、标签、语言进行搜索和筛选
- 支持分页显示
- 支持点击原唱、曲风、语言、标签进行快速筛选
- 支持展开查看演唱记录

### 5.2 热歌榜展示
- 支持按不同时间范围（全部、近1月、近3月、近1年）查看排行榜
- 显示推荐语和推荐歌曲
- 点击歌曲可查看演唱记录

### 5.3 精选二创作品展示
- 按合集展示粉丝创作作品
- 支持按position和display_order排序
- 点击作品可查看视频

### 5.4 盲盒功能
- 普通盲盒：随机返回一首歌曲
- 自定义盲盒：支持按条件筛选后进行抽奖

## 6. 管理后台功能

### 6.1 歌曲管理
- 支持歌曲信息的增删改查
- 支持歌曲合并和拆分
- 支持批量设置语言
- 支持查看演唱记录

### 6.2 演唱记录管理
- 支持从BV号导入演唱记录
- 支持替换封面图片
- 支持查看封面缩略图

### 6.3 曲风和标签管理
- 支持曲风和标签的增删改查
- 支持批量为歌曲添加曲风和标签
- 支持为标签批量标记歌曲

### 6.4 合集和作品管理
- 支持合集和作品的增删改查
- 支持从BV号导入作品到指定合集
- 支持设置position和display_order

### 6.5 推荐语管理
- 支持推荐语内容编辑
- 支持选择推荐歌曲
- 支持激活/禁用推荐语

## 7. 实用工具脚本

### 7.1 数据导入导出
- `import_public_data.py`: 导入公开数据
- `download_img.py`: 下载图片
- `compress_images.py`: 压缩图片

### 7.2 数据维护
- `rebuild_song_stats.py`: 重新计算歌曲统计数据
- `merge_songs.py`: 合并歌曲记录
- `update_cover_urls.py`: 更新封面URL

### 7.3 部署相关
- `rebuild.sh`: 生产环境部署脚本

## 8. 开发环境搭建

### 8.1 后端环境

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

### 8.2 前端环境

1. 安装依赖:
   ```bash
   cd xxm_fans_frontend
   npm install
   ```

2. 运行开发服务器:
   ```bash
   npm run dev
   ```

## 9. 部署注意事项

1. 设置生产环境变量 (`.env`文件)
2. 设置 `DJANGO_DEBUG=False`
3. 配置适当的 `ALLOWED_HOSTS`
4. 使用安全的 `SECRET_KEY`
5. 配置数据库（生产环境建议使用PostgreSQL或MySQL）
6. 配置Redis缓存（生产环境可选，用于提高性能）
   - 安装Redis服务器
   - 在settings.py中配置Redis连接信息
   - 启用Redis缓存配置：
     ```python
     CACHES = {
         "default": {
             "BACKEND": "django_redis.cache.RedisCache",
             "LOCATION": "redis://127.0.0.1:6379/1",
             "OPTIONS": {
                 "CLIENT_CLASS": "django_redis.client.DefaultClient",
             }
         }
     }
     ```
7. 配置静态文件服务
8. 配置Web服务器（Nginx/Apache）和应用服务器（Gunicorn/uWSGI）

## 10. 项目规范

### 10.1 开发规范
- 遵循Django和Vue.js最佳实践
- 接口设计符合RESTful规范
- 前端保持Element Plus UI风格一致
- 每完成一个需求后提交commit
- 编写对应功能实现文档

### 10.2 代码约束
- Django的Songs和SongRecord模型结构不能修改
- 前端必须保持和Element Plus UI风格一致
- 按照todolist中的需求工作
- 实现过程每完成一个需求都在logs中写一份Markdown文档

## 11. 未来改进方向

1. 集成Spotify API自动为歌曲分配曲风
2. 优化精选二创页面图片懒加载
3. 增加更多数据可视化功能
4. 支持用户评论和互动功能
5. 移动端适配优化