# 小满虫之家——XXM_Fans_Home

一个基于 Django + Vue.js 技术栈构建的音乐粉丝网站，专注于音乐记录管理、歌曲搜索筛选、排行榜展示和粉丝二创作品分享。

## 🎵 项目特色

- **音乐管理**: 完整的歌曲信息、演唱记录、曲风分类和标签管理系统
- **智能搜索筛选**: 支持多维度歌曲搜索和高级筛选功能
- **实时排行榜**: 多时间维度的热门歌曲排行榜展示
- **粉丝二创平台**: 精选二创作品展示和合集管理
- **盲盒功能**: 随机歌曲推荐和自定义盲盒筛选
- **性能优化**: 图片懒加载、压缩优化和高并发支持

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 4.x + Django REST Framework
- **数据库**: SQLite 
- **缓存**: Redis
- **API**: RESTful API 设计

### 前端技术栈
- **框架**: Vue.js 3
- **UI组件**: Element Plus
- **构建工具**: Vite
- **HTTP客户端**: Axios

### 开发工具
- **性能测试**: Locust + Matplotlib
- **代码质量**: ESLint, Prettier
- **版本控制**: Git

## 📁 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用，包含核心模型和API
│   ├── models.py           # 核心数据模型 (Songs, SongRecord, Style, Tag等)
│   ├── views.py            # API视图和业务逻辑
│   ├── serializers.py      # DRF序列化器
│   └── urls.py             # URL路由配置
├── fansDIY/                 # 粉丝二创作品管理应用
│   ├── models.py           # Collection, Work模型
│   └── views.py            # 二创作品相关API
├── xxm_fans_frontend/       # Vue.js 前端项目
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   └── store/          # 状态管理
│   └── dist/               # 构建输出目录
├── static/                  # 静态文件资源
├── templates/               # Django 模板
├── test/                    # 性能测试相关文件
├── tools/                   # 实用工具脚本
└── xxm_fans_home/           # Django 项目配置
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm

### 安装步骤

1. **克隆项目**
```bash
git clone git@gitee.com:yifeianyi/xxm_fans_home.git
cd xxm_fans_home
```

2. **后端环境设置**
```bash
# 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 导入初始数据（可选）
python tools/import_public_data.py
```

3. **前端环境设置**
```bash
cd xxm_fans_frontend
npm install
```

### 运行项目

1. **启动后端服务**
```bash
python manage.py runserver
```
后端服务将在 http://127.0.0.1:8000 启动

2. **启动前端服务**
```bash
cd xxm_fans_frontend
npm run dev
```
前端服务将在 http://localhost:5173 启动

## 📊 核心功能模块

### 音乐管理系统
- **歌曲信息管理** (Songs): 歌曲基本信息、封面、发布时间等
- **演唱记录管理** (SongRecord): 演唱会记录、视频链接、BV号等
- **曲风分类管理** (Style): 音乐风格分类体系
- **标签管理** (Tag): 多维度标签系统
- **推荐语管理** (Recommendation): 个性化推荐内容

### 粉丝二创平台
- **合集管理** (Collection): 二创作品合集分类
- **作品管理** (Work): 单个二创作品信息管理

### 前端展示功能
- 歌曲列表与高级搜索
- 演唱记录详情展示
- 多维度排行榜（日榜、周榜、月榜）
- 精选二创作品画廊
- 随机歌曲盲盒功能
- 自定义筛选盲盒
- 图片懒加载优化

## 🔧 API接口文档

### 音乐管理相关
- `GET /api/songs/` - 歌曲列表，支持搜索、分页和排序
- `GET /api/songs/{id}/records/` - 特定歌曲的演唱记录
- `GET /api/styles/` - 曲风列表
- `GET /api/tags/` - 标签列表
- `GET /api/top_songs/` - 排行榜数据
- `GET /api/random-song/` - 随机歌曲
- `GET /api/recommendation/` - 推荐语

### 粉丝二创作品相关
- `GET /api/fansDIY/collections/` - 合集列表
- `GET /api/fansDIY/collections/{id}/` - 特定合集详情
- `GET /api/fansDIY/works/` - 作品列表
- `GET /api/fansDIY/works/{id}/` - 特定作品详情

## ⚡ 性能测试

项目内置完整的性能测试套件，基于 Locust 框架。

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
测试完成后生成详细的性能报告和可视化图表，包括QPS、响应时间、错误率等关键指标。

## 🛠️ 实用工具

### 数据管理
- `tools/import_public_data.py` - 导入公开数据
- `tools/export_public_data.py` - 导出公开数据
- `tools/import_songs_from_json.py` - 从JSON导入歌曲数据

### 图片处理
- `tools/download_img.py` - 批量下载图片
- `tools/compress_images.py` - 图片压缩优化
- `tools/update_cover_urls.py` - 更新封面URL

### B站集成
- `tools/bilibili_importer.py` - B站视频信息导入
- `tools/import_song_records.py` - 演唱记录导入

## 🚀 部署指南

### 生产环境配置

1. **环境变量设置**
```bash
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='your-secret-key'
export ALLOWED_HOSTS='your-domain.com'
```

2. **静态文件收集**
```bash
python manage.py collectstatic --noinput
```

3. **数据库配置**
- 生产环境推荐使用 PostgreSQL
- 配置 Redis 缓存服务

4. **Web服务器配置**
- 推荐使用 Nginx + Gunicorn 部署方案
- 配置 HTTPS 证书

## 📝 开发规范

### 代码提交规范
- 每完成一个功能需求后提交 commit
- 编写清晰的功能实现文档
- 在 todolist 中标记完成状态

### 约束条件
- 不能修改 SongRecord 和 Songs 核心模型结构
- 遵循现有的代码风格和架构模式
- 保持 API 接口的向后兼容性

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

⭐ 如果这个项目对你有帮助，请给它一个星标！