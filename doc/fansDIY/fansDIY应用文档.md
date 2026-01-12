# FansDIY 应用文档

## 概述

FansDIY 应用是用于管理粉丝二创作品的模块，包括合集和作品的管理功能。

## 目录结构

```
fansDIY/
├── models/                 # 模型目录
│   ├── __init__.py
│   ├── collection.py      # 合集模型
│   └── work.py           # 作品模型
├── services/              # 服务层目录
│   ├── __init__.py
│   └── diy_service.py    # DIY服务类
├── api/                   # API 目录
│   ├── __init__.py
│   ├── serializers.py     # 序列化器
│   └── views.py          # API 视图
├── admin/                 # Admin 目录
│   ├── __init__.py
│   └── diy_admin.py      # Admin 配置
├── templates/             # 模板目录
├── forms.py              # 表单
├── urls.py               # URL 配置
├── utils.py              # 工具函数
└── views.py              # 视图（旧版，保留兼容性）
```

## 模型

### Collection（合集）

合集模型用于管理粉丝二创作品的分类。

#### 字段

- `id`: 主键
- `name`: 合集名称（CharField, max_length=200）
- `works_count`: 作品数量（IntegerField, 默认0）
- `display_order`: 显示顺序（IntegerField, 默认0）
- `position`: 位置（IntegerField, 默认0）
- `created_at`: 创建时间（DateTimeField, auto_now_add=True）
- `updated_at`: 更新时间（DateTimeField, auto_now=True）

#### 方法

- `update_works_count()`: 更新作品数量

### Work（作品）

作品模型用于管理具体的二创作品。

#### 字段

- `id`: 主键
- `collection`: 所属合集（ForeignKey, 关联到Collection）
- `title`: 作品标题（CharField, max_length=300）
- `cover_url`: 封面图片地址（CharField, max_length=500, 可选）
- `view_url`: 观看链接（URLField, 可选）
- `author`: 作者（CharField, max_length=100）
- `notes`: 备注（TextField, 可选）
- `display_order`: 显示顺序（IntegerField, 默认0）
- `position`: 位置（IntegerField, 默认0）

#### 方法

- `save()`: 保存时自动更新合集的作品数量
- `delete()`: 删除时自动更新合集的作品数量

## 服务层

### DIYService

DIYService 类提供了合集和作品的业务逻辑方法。

#### 合集管理方法

- `get_collections(page=1, page_size=20)`: 获取合集列表（支持分页）
- `get_collection_by_id(collection_id)`: 根据ID获取合集详情
- `create_collection(name, position=0, display_order=0)`: 创建合集
- `update_collection(collection_id, **kwargs)`: 更新合集
- `delete_collection(collection_id)`: 删除合集

#### 作品管理方法

- `get_works(page=1, page_size=20, collection_id=None)`: 获取作品列表（支持分页和筛选）
- `get_work_by_id(work_id)`: 根据ID获取作品详情
- `create_work(collection_id, title, author, **kwargs)`: 创建作品
- `update_work(work_id, **kwargs)`: 更新作品
- `delete_work(work_id)`: 删除作品

## API 接口

### 合集接口

#### 获取合集列表

- **URL**: `/api/fansDIY/collections/`
- **Method**: GET
- **Query Parameters**:
  - `page`: 页码（默认1）
  - `limit`: 每页数量（默认20）
- **Response**: 统一响应格式，包含分页信息和合集列表

#### 获取合集详情

- **URL**: `/api/fansDIY/collections/{collection_id}/`
- **Method**: GET
- **Response**: 统一响应格式，包含合集详情

### 作品接口

#### 获取作品列表

- **URL**: `/api/fansDIY/works/`
- **Method**: GET
- **Query Parameters**:
  - `page`: 页码（默认1）
  - `limit`: 每页数量（默认20）
  - `collection`: 合集ID（可选）
- **Response**: 统一响应格式，包含分页信息和作品列表

#### 获取作品详情

- **URL**: `/api/fansDIY/works/{work_id}/`
- **Method**: GET
- **Response**: 统一响应格式，包含作品详情

## Admin 后台

### CollectionAdmin

合集管理后台，支持：

- 列表显示：名称、作品数量、位置、显示顺序、创建时间、更新时间
- 搜索：按名称搜索
- 过滤：按创建时间、更新时间过滤
- 内联：支持在合集页面直接管理作品

### WorkAdmin

作品管理后台，支持：

- 列表显示：标题、作者、合集、位置、显示顺序、封面预览、观看链接、备注预览
- 搜索：按标题、作者、合集名称、备注搜索
- 过滤：按合集、作者过滤
- 特殊功能：
  - 封面预览
  - 观看链接
  - 备注预览（超过50字符截断）
  - BV导入功能
  - 保存时自动更新合集作品数量

## 使用示例

### 使用服务层

```python
from fansDIY.services import DIYService

# 获取合集列表
collections = DIYService.get_collections(page=1, page_size=20)

# 获取合集详情
collection = DIYService.get_collection_by_id(1)

# 创建合集
new_collection = DIYService.create_collection('新合集', position=1, display_order=1)

# 创建作品
new_work = DIYService.create_work(
    collection_id=1,
    title='新作品',
    author='作者',
    cover_url='/covers/image.jpg',
    view_url='https://example.com'
)
```

### 调用API

```python
import requests

# 获取合集列表
response = requests.get('http://localhost:8000/api/fansDIY/collections/')
data = response.json()

# 获取作品列表
response = requests.get('http://localhost:8000/api/fansDIY/works/?collection=1')
data = response.json()
```

## 注意事项

1. **作品数量自动更新**: 当创建或删除作品时，会自动更新对应合集的作品数量
2. **缓存**: 服务层方法使用了缓存装饰器，默认缓存时间为300秒
3. **异常处理**: 服务层方法会抛出特定异常（CollectionNotFoundException、WorkNotFoundException、DatabaseException）
4. **排序**: 合集和作品默认按 position、display_order 升序排列，合集还按创建时间降序排列

## 扩展性

- 可以通过继承 DIYService 类来扩展功能
- 可以通过自定义 Admin 类来扩展后台功能
- 可以通过自定义序列化器来扩展API数据格式
