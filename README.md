# XXM Fans Home

一个基于 Django + Vue.js 的音乐粉丝网站项目。

## 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用
├── xxm_fans_frontend/       # Vue.js 前端项目
├── static/                  # 静态文件
├── templates/               # Django 模板
├── xxm_fans_home/          # Django 项目配置
├── sqlInit_data/           # 公开数据文件
└── manage.py               # Django 管理脚本
```

## 功能特性

- 音乐记录管理
- 歌曲搜索和筛选
- 排行榜展示
- 图片压缩和优化
- 响应式前端界面

## 安装和配置

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd xxm_fans_home
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 环境配置

复制环境变量示例文件并配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，设置以下变量：

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. 数据库迁移

```bash
python manage.py migrate
```

### 6. 导入公开数据（可选）

项目包含公开的音乐数据，可以导入到数据库中：

```bash
python import_public_data.py
```

### 7. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 8. 运行开发服务器

```bash
python manage.py runserver
```

## 前端开发

### 安装前端依赖

```bash
cd xxm_fans_frontend
npm install
```

### 运行前端开发服务器

```bash
npm run dev
```

## 实用脚本

### 下载图片

```bash
python download_img.py
```

### 压缩图片

```bash
python compress_images.py
```

### 导出公开数据

```bash
python export_public_data.py
```

### 导入公开数据

```bash
python import_public_data.py
```

## 数据管理

### 公开数据

项目中的音乐数据（歌曲、风格、记录等）被视为公开数据，可以安全地包含在代码仓库中。

### 敏感数据

以下数据被视为敏感信息，不会包含在代码仓库中：
- 用户账户信息
- 管理员账户
- 个人设置和偏好

### 数据备份和恢复

如果需要备份或迁移数据：

1. **导出公开数据**：运行 `python export_public_data.py`
2. **导入公开数据**：运行 `python import_public_data.py`

## 部署注意事项

1. 确保 `.env` 文件包含正确的生产环境配置
2. 设置 `DJANGO_DEBUG=False` 用于生产环境
3. 配置适当的 `ALLOWED_HOSTS`
4. 使用安全的 `SECRET_KEY`
5. 在生产环境中创建新的数据库和用户账户

## 许可证

[添加你的许可证信息]
