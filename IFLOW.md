# 项目概述

这是一个名为"XXM Fans Home"的音乐粉丝网站项目，采用Django + Vue.js技术栈构建。项目主要功能包括音乐记录管理、歌曲搜索筛选、排行榜展示、精选二创作品展示、盲盒功能以及图片处理等。

## 技术架构

- **后端**: Django (Python) + Django REST Framework
- **前端**: Vue.js 3 + Element Plus
- **数据库**: SQLite (开发环境)
- **API**: Django REST Framework
- **前端构建工具**: Vite
- **UI框架**: Element Plus
- **性能测试**: Locust + Matplotlib

## 项目结构

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
├── test/                    # 性能测试相关文件
├── logs/                    # 日志文件
└── manage.py                # Django 管理脚本
```

## 核心功能模块

### 音乐管理 (main应用)
1. **歌曲信息管理** (Songs)
2. **演唱记录管理** (SongRecord)
3. **曲风分类管理** (Style)
4. **标签管理** (Tag)
5. **歌曲与曲风关联** (SongStyle)
6. **歌曲与标签关联** (SongTag)
7. **推荐语管理** (Recommendation)

### 粉丝二创作品管理 (fansDIY应用)
1. **合集管理** (Collection)
2. **作品管理** (Work)

### 前端展示
1. **歌曲列表与搜索**
2. **演唱记录详情**
3. **排行榜展示**
4. **精选二创作品展示**
5. **盲盒功能（随机歌曲）**
6. **自定义盲盒（筛选条件随机歌曲）**
7. **图片懒加载优化**

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

## 性能测试

项目包含完整的性能测试套件，用于评估系统在高并发情况下的表现。

### 测试组件

1. **Locustfile.py** - 主要测试脚本，模拟用户行为
2. **locust.conf** - Locust配置文件
3. **visualize_locust.py** - 测试结果可视化脚本
4. **generate_report.py** - 详细报告生成器
5. **run_performance_test.sh/bat** - 一键执行脚本

### 运行性能测试

#### 方法一：使用一键脚本（推荐）

```bash
# Linux/Mac
cd test
./run_performance_test.sh

# Windows
cd test
run_performance_test.bat
```

#### 方法二：手动运行

```bash
# 进入test目录
cd test

# 运行性能测试
locust -f Locustfile.py --config locust.conf

# 生成可视化图表
python visualize_locust.py

# 生成详细报告
python generate_report.py
```

### 测试配置说明

默认配置：
- 并发用户数：100
- 用户启动速率：10 users/second
- 运行时长：10分钟
- 目标地址：https://www.xxm8777.cn

可以通过修改 `locust.conf` 文件来调整这些参数。

### 测试场景

测试脚本模拟了以下用户行为：
1. 浏览歌曲列表（带分页和搜索）
2. 查看歌曲演唱记录
3. 浏览热歌榜（不同时间范围）
4. 浏览粉丝二创作品合集
5. 查看合集详情和作品列表
6. 访问随机歌曲
7. 获取曲风和标签信息

### 结果分析

测试完成后会生成以下文件：
- `load_test_results_stats.csv` - 详细统计信息
- `load_test_results_failures.csv` - 失败请求详情
- `qps.png` - QPS图表
- `response_time.png` - 响应时间图表
- `failures.png` - 失败数图表
- `charts/` 目录下包含更多详细图表

## 实用脚本

- `download_img.py`: 下载图片
- `compress_images.py`: 压缩图片
- `import_public_data.py`: 导入公开数据
- `export_public_data.py`: 导出公开数据
- `update_cover_urls.py`: 更新封面URL
- `update_cover_urls_bulk.py`: 批量更新封面URL

## API接口

主要REST API接口包括:

### 音乐管理相关
- `/api/songs/`: 歌曲列表，支持搜索、分页和排序
- `/api/songs/<song_id>/records/`: 特定歌曲的演唱记录
- `/api/styles/`: 曲风列表
- `/api/tags/`: 标签列表
- `/api/top_songs/`: 排行榜数据
- `/api/random-song/`: 随机歌曲
- `/api/recommendation/`: 推荐语

### 粉丝二创作品相关
- `/api/fansDIY/collections/`: 合集列表
- `/api/fansDIY/collections/<collection_id>/`: 特定合集详情
- `/api/fansDIY/works/`: 作品列表
- `/api/fansDIY/works/<work_id>/`: 特定作品详情

## 部署注意事项

### 环境变量

确保在生产环境中正确设置以下环境变量：
- `DJANGO_DEBUG`：设置为 `False`
- `DJANGO_SECRET_KEY`：设置安全的密钥
- `ALLOWED_HOSTS`：设置允许的域名
- 数据库连接信息

### 静态文件

部署前需要收集静态文件：

```bash
python manage.py collectstatic
```

### 安全设置

1. 确保 `DEBUG = False` 在生产环境中
2. 设置合适的 `ALLOWED_HOSTS`
3. 使用安全的 `SECRET_KEY`
4. 配置 HTTPS