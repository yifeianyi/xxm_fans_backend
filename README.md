# XXM Fans Home

一个基于 Django + Vue.js 的音乐粉丝网站项目。

## 项目结构

```
xxm_fans_home/
├── main/                    # Django 主应用
├── xxm_fans_frontend/       # Vue.js 前端项目
├── fansDIY/                 # 粉丝二创作品管理应用
├── static/                  # 静态文件
├── templates/               # Django 模板
├── xxm_fans_home/          # Django 项目配置
├── sqlInit_data/           # 公开数据文件
├── test/                   # 性能测试相关文件
├── tools/                  # 实用工具脚本
└── manage.py               # Django 管理脚本
```

## 功能特性

- 音乐记录管理
- 歌曲搜索和筛选
- 排行榜展示
- 粉丝二创作品展示
- 图片压缩和优化
- 响应式前端界面

## 安装和配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd xxm_fans_home
```

### 2. 设置后端环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置文件
cp env.example .env
# 编辑 .env 文件设置环境变量

# 数据库迁移
python manage.py migrate

# 导入初始数据（可选）
python import_public_data.py
```

### 3. 设置前端环境

```bash
cd xxm_fans_frontend
npm install
```

## 运行项目

### 运行后端开发服务器

```bash
python manage.py runserver
```

### 运行前端开发服务器

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