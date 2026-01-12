# Core 模块使用文档

## 概述

Core 模块提供跨应用共享的核心功能，包括缓存装饰器、统一响应格式、自定义异常和工具类。

## 目录

- [缓存模块](#缓存模块)
- [响应模块](#响应模块)
- [异常模块](#异常模块)
- [工具模块](#工具模块)

---

## 缓存模块

### cache_result 装饰器

统一处理缓存逻辑，自动处理缓存键生成、缓存读写和异常处理。

#### 基本用法

```python
from core.cache import cache_result

@cache_result(timeout=600, key_prefix="songs_list")
def get_songs():
    # 业务逻辑
    return Songs.objects.all()
```

#### 参数说明

- `timeout`: 缓存超时时间（秒），默认 600 秒（10 分钟）
- `key_prefix`: 缓存键前缀，用于区分不同的缓存

#### 高级用法

```python
from core.cache import cache_result

# 带参数的缓存
@cache_result(timeout=300, key_prefix="user_data")
def get_user_data(user_id):
    return User.objects.get(id=user_id)

# 自定义缓存时间
@cache_result(timeout=3600)  # 1 小时
def get_static_config():
    return Config.objects.first()
```

### clear_cache_pattern

清除匹配模式的缓存。

```python
from core.cache import clear_cache_pattern

# 清除所有以 "songs_list" 开头的缓存
clear_cache_pattern("songs_list")
```

---

## 响应模块

### success_response

成功响应。

```python
from core.responses import success_response

# 基本用法
return success_response(data={"id": 1, "name": "test"})

# 自定义消息
return success_response(data=[1, 2, 3], message="获取成功")

# 自定义响应码
return success_response(data=result, code=200)
```

### error_response

错误响应。

```python
from core.responses import error_response

# 基本用法
return error_response(message="参数错误", code=400)

# 带详细错误信息
return error_response(
    message="验证失败",
    code=422,
    errors={"name": ["该字段不能为空"]}
)
```

### paginated_response

分页响应。

```python
from core.responses import paginated_response

return paginated_response(
    data=[{"id": 1}, {"id": 2}],
    total=100,
    page=1,
    page_size=20
)
```

### created_response

创建成功响应（HTTP 201）。

```python
from core.responses import created_response

return created_response(data={"id": 1, "name": "test"})
```

### updated_response

更新成功响应。

```python
from core.responses import updated_response

return updated_response(data={"id": 1, "name": "updated"})
```

### deleted_response

删除成功响应。

```python
from core.responses import deleted_response

return deleted_response()
```

---

## 异常模块

### 基础异常

```python
from core.exceptions import (
    SongNotFoundException,
    InvalidParameterException,
    ArtistNotFoundException,
    CollectionNotFoundException,
    WorkNotFoundException,
    PermissionDeniedException,
    ValidationException,
    CacheException,
    DatabaseException
)

# 抛出异常
raise SongNotFoundException()
raise InvalidParameterException("参数无效")
```

### 自定义异常

```python
from core.exceptions import BaseAPIException

class MyCustomException(BaseAPIException):
    status_code = 400
    default_detail = "自定义错误消息"
    default_code = "custom_error"
```

---

## 工具模块

### ImageDownloader

统一的图片下载器。

#### 基本用法

```python
from core.utils import ImageDownloader

# 创建下载器
downloader = ImageDownloader()

# 下载单个图片
path = downloader.download("https://example.com/image.jpg")
if path:
    print(f"下载成功: {path}")
```

#### 批量下载

```python
from core.utils import ImageDownloader

downloader = ImageDownloader()

# 批量下载
urls = [
    'https://example.com/image1.jpg',
    {'url': 'https://example.com/image2.jpg', 'filename': 'custom.jpg'}
]
paths = downloader.download_batch(urls, show_progress=True)
```

#### 带重试的下载

```python
from core.utils import ImageDownloader

downloader = ImageDownloader()

# 带重试的下载
path = downloader.download_with_retry(
    "https://example.com/image.jpg",
    max_retries=3,
    retry_delay=1
)
```

#### 其他功能

```python
from core.utils import ImageDownloader

downloader = ImageDownloader()

# 获取文件大小
size = downloader.get_file_size("image.jpg")

# 删除文件
success = downloader.delete_file("image.jpg")
```

### 验证器

```python
from core.utils import validate_url, validate_image_url, validate_email

# 验证 URL
if validate_url("https://example.com"):
    print("URL 格式正确")

# 验证图片 URL
if validate_image_url("https://example.com/image.jpg"):
    print("图片 URL 格式正确")

# 验证邮箱
if validate_email("user@example.com"):
    print("邮箱格式正确")

# 验证手机号
from core.utils import validate_phone
if validate_phone("13800138000"):
    print("手机号格式正确")

# 验证字符串长度
from core.utils import validate_string_length
if validate_string_length("test", min_length=2, max_length=10):
    print("字符串长度符合要求")

# 清理文件名
from core.utils import sanitize_filename
safe_name = sanitize_filename("file/name?.txt")
# 返回: "filename.txt"
```

---

## 完整示例

### 在视图中使用

```python
from rest_framework.decorators import api_view
from core.cache import cache_result
from core.responses import success_response, error_response, paginated_response
from core.exceptions import SongNotFoundException
from core.utils import validate_image_url
from .models import Song
from .serializers import SongSerializer


@api_view(['GET'])
def song_list(request):
    """歌曲列表 API"""
    try:
        # 使用缓存装饰器
        songs = get_songs_cached()

        serializer = SongSerializer(songs, many=True)
        return success_response(data=serializer.data)

    except Exception as e:
        return error_response(message=str(e), code=500)


@cache_result(timeout=600, key_prefix="songs_list")
def get_songs_cached():
    """带缓存的歌曲列表"""
    return Song.objects.all()


@api_view(['GET'])
def song_detail(request, song_id):
    """歌曲详情 API"""
    try:
        song = Song.objects.get(id=song_id)
        serializer = SongSerializer(song)
        return success_response(data=serializer.data)
    except Song.DoesNotExist:
        raise SongNotFoundException()


@api_view(['POST'])
def upload_cover(request):
    """上传封面 API"""
    url = request.data.get('url')

    # 验证 URL
    if not validate_image_url(url):
        return error_response(message="无效的图片 URL", code=400)

    # 下载图片
    from core.utils import ImageDownloader
    downloader = ImageDownloader()
    path = downloader.download(url)

    if path:
        return success_response(data={"cover_path": path}, message="上传成功")
    else:
        return error_response(message="下载失败", code=500)
```

### 在服务层使用

```python
from core.cache import cache_result
from core.exceptions import SongNotFoundException
from .models import Song


class SongService:
    """歌曲服务"""

    @staticmethod
    @cache_result(timeout=600, key_prefix="song_detail")
    def get_song_by_id(song_id):
        """根据 ID 获取歌曲"""
        try:
            return Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            raise SongNotFoundException()

    @staticmethod
    @cache_result(timeout=300, key_prefix="top_songs")
    def get_top_songs(limit=10):
        """获取热门歌曲"""
        return Song.objects.order_by('-play_count')[:limit]
```

---

## 最佳实践

1. **缓存使用**
   - 为频繁访问但不常变化的数据添加缓存
   - 合理设置缓存超时时间
   - 使用有意义的缓存键前缀

2. **响应格式**
   - 始终使用统一的响应格式
   - 提供清晰的错误消息
   - 包含必要的错误详情

3. **异常处理**
   - 使用自定义异常类
   - 提供有意义的错误消息
   - 在适当的地方捕获和处理异常

4. **工具类**
   - 复用现有的工具类
   - 避免重复造轮子
   - 添加必要的错误处理

---

## 注意事项

1. **缓存限制**
   - LocMemCache 不支持模式匹配
   - 如需模式匹配，请使用 Redis 等缓存后端

2. **文件下载**
   - 确保有足够的磁盘空间
   - 处理网络超时和错误
   - 验证下载的文件

3. **异常处理**
   - 不要捕获所有异常
   - 记录异常日志
   - 提供友好的错误消息

---

**文档版本**: 1.0
**最后更新**: 2026-01-12