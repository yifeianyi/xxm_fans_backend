# XXM Fans Home API 文档

## 目录

- [音乐管理 API (main)](#音乐管理-api-main)
- [粉丝二创作品 API (fansDIY)](#粉丝二创作品-api-fansdiy)
- [优优歌曲列表 API (youyou)](#优优歌曲列表-api-youyou)
- [冰洁歌曲列表 API (bingjie)](#冰洁歌曲列表-api-bingjie)

---

## 音乐管理 API (main)

### 1. 获取歌曲列表

**接口地址**: `GET /api/songs/`

**功能描述**: 获取歌曲列表，支持搜索、分页和多条件筛选

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| q | string | 否 | 搜索关键词（歌名或歌手） |
| page | int | 否 | 页码，默认为1 |
| limit | int | 否 | 每页数量，默认为50，最大50 |
| ordering | string | 否 | 排序字段：`singer`（歌手）、`last_performed`（最近演唱）、`perform_count`（演唱次数），默认按最近演唱倒序 |
| styles | string | 否 | 曲风筛选，多个曲风用逗号分隔 |
| tags | string | 否 | 标签筛选，多个标签用逗号分隔 |
| language | string | 否 | 语言筛选，多个语言用逗号分隔 |

**响应示例**:

```json
{
  "total": 1250,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "id": 1,
      "song_name": "歌曲名称",
      "singer": "歌手名",
      "language": "中文",
      "perform_count": 15,
      "last_performed": "2025-12-15",
      "styles": ["流行", "抒情"],
      "tags": ["经典", "热门"]
    }
  ]
}
```

---

### 2. 获取歌曲演唱记录

**接口地址**: `GET /api/songs/<song_id>/records/`

**功能描述**: 获取指定歌曲的演唱记录列表

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认为1 |
| page_size | int | 否 | 每页数量，默认为20 |

**响应示例**:

```json
{
  "total": 30,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "song_id": 1,
      "performed_at": "2025-12-15",
      "duration": "3:45",
      "cover_url": "/covers/2025/12/2025-12-15.jpg"
    }
  ]
}
```

---

### 3. 获取曲风列表

**接口地址**: `GET /api/styles/`

**功能描述**: 获取所有曲风名称列表

**请求参数**: 无

**响应示例**:

```json
[
  "流行",
  "抒情",
  "摇滚",
  "民谣",
  "电子"
]
```

---

### 4. 获取标签列表

**接口地址**: `GET /api/tags/`

**功能描述**: 获取所有标签名称列表

**请求参数**: 无

**响应示例**:

```json
[
  "经典",
  "热门",
  "新歌",
  "怀旧",
  "治愈"
]
```

---

### 5. 获取热歌榜

**接口地址**: `GET /api/top_songs/`

**功能描述**: 获取热门歌曲排行榜

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| range | string | 否 | 时间范围：`all`（全部）、`1m`（1个月）、`3m`（3个月）、`1y`（1年）、`10d`（10天）、`20d`（20天）、`30d`（30天），默认为`all` |
| limit | int | 否 | 返回数量，默认为10 |

**响应示例**:

```json
[
  {
    "id": 1,
    "song_name": "歌曲名称",
    "singer": "歌手名",
    "perform_count": 25,
    "last_performed": "2025-12-20"
  }
]
```

---

### 6. 获取随机歌曲

**接口地址**: `GET /api/random-song/`

**功能描述**: 随机返回一首歌曲

**请求参数**: 无

**响应示例**:

```json
{
  "id": 123,
  "song_name": "歌曲名称",
  "singer": "歌手名",
  "styles": ["流行", "抒情"],
  "last_performed": "2025-12-10",
  "perform_count": 8,
  "language": "中文"
}
```

---

### 7. 获取推荐语

**接口地址**: `GET /api/recommendation/`

**功能描述**: 获取当前激活的推荐语及推荐歌曲

**请求参数**: 无

**响应示例**:

```json
{
  "content": "欢迎来到热歌榜！今天推荐几首经典歌曲给大家。",
  "recommended_songs": [
    {
      "id": 1,
      "song_name": "歌曲名称",
      "singer": "歌手名",
      "perform_count": 20
    }
  ]
}
```

---

## 粉丝二创作品 API (fansDIY)

### 1. 获取合集列表

**接口地址**: `GET /api/fansDIY/collections/`

**功能描述**: 获取粉丝二创作品合集列表

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认为1 |
| limit | int | 否 | 每页数量，默认为20 |

**响应示例**:

```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "name": "合集名称",
      "works_count": 25,
      "position": 1,
      "display_order": 1,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-10T00:00:00Z"
    }
  ]
}
```

---

### 2. 获取合集详情

**接口地址**: `GET /api/fansDIY/collections/<collection_id>/`

**功能描述**: 获取指定合集的详细信息

**请求参数**: 无

**响应示例**:

```json
{
  "id": 1,
  "name": "合集名称",
  "works_count": 25,
  "position": 1,
  "display_order": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-10T00:00:00Z"
}
```

---

### 3. 获取作品列表

**接口地址**: `GET /api/fansDIY/works/`

**功能描述**: 获取粉丝二创作品列表

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认为1 |
| limit | int | 否 | 每页数量，默认为20 |
| collection | int | 否 | 合集ID，用于筛选特定合集的作品 |

**响应示例**:

```json
{
  "total": 50,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "title": "作品标题",
      "cover_url": "/covers/work1.jpg",
      "view_url": "https://example.com/video1",
      "author": "作者名",
      "notes": "作品备注",
      "position": 1,
      "display_order": 1,
      "collection": {
        "id": 1,
        "name": "合集名称"
      }
    }
  ]
}
```

---

### 4. 获取作品详情

**接口地址**: `GET /api/fansDIY/works/<work_id>/`

**功能描述**: 获取指定作品的详细信息

**请求参数**: 无

**响应示例**:

```json
{
  "id": 1,
  "title": "作品标题",
  "cover_url": "/covers/work1.jpg",
  "view_url": "https://example.com/video1",
  "author": "作者名",
  "notes": "作品备注",
  "position": 1,
  "display_order": 1,
  "collection": {
    "id": 1,
    "name": "合集名称"
  }
}
```

---

## 优优歌曲列表 API (youyou)

### 1. 获取歌曲列表

**接口地址**: `GET /api/youyou/songs/`

**功能描述**: 获取优优的歌曲列表，支持筛选和搜索

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| language | string | 否 | 语言筛选 |
| style | string | 否 | 曲风筛选 |
| search | string | 否 | 搜索关键词（歌名或歌手） |

**响应示例**:

```json
[
  {
    "id": 1,
    "song_name": "歌曲名称",
    "language": "中文",
    "singer": "歌手名",
    "style": "流行",
    "note": "备注信息"
  }
]
```

---

### 2. 获取语言列表

**接口地址**: `GET /api/youyou/languages/`

**功能描述**: 获取所有可用语言

**请求参数**: 无

**响应示例**:

```json
[
  "中文",
  "日语",
  "英语"
]
```

---

### 3. 获取曲风列表

**接口地址**: `GET /api/youyou/styles/`

**功能描述**: 获取所有曲风

**请求参数**: 无

**响应示例**:

```json
[
  "流行",
  "抒情",
  "摇滚",
  "民谣"
]
```

---

### 4. 获取随机歌曲

**接口地址**: `GET /api/youyou/random-song/`

**功能描述**: 随机返回一首歌曲，支持筛选条件

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| language | string | 否 | 语言筛选 |
| style | string | 否 | 曲风筛选 |
| search | string | 否 | 搜索关键词 |

**响应示例**:

```json
{
  "id": 123,
  "song_name": "歌曲名称",
  "language": "中文",
  "singer": "歌手名",
  "style": "流行",
  "note": "备注信息"
}
```

**错误响应** (404):

```json
{
  "error": "No songs available."
}
```

---

### 5. 获取网站设置

**接口地址**: `GET /api/youyou/site-settings/`

**功能描述**: 获取优优的网站设置信息

**请求参数**: 无

**响应示例**:

```json
[
  {
    "id": 1,
    "position": 1,
    "photoURL": "1.png",
    "other_field": "其他字段值"
  }
]
```

---

### 6. 获取网站图标

**接口地址**: `GET /api/youyou/favicon.ico`

**功能描述**: 获取网站的favicon图标

**请求参数**: 无

**响应**: 重定向到对应的图片文件或返回404

---

## 冰洁歌曲列表 API (bingjie)

### 1. 获取歌曲列表

**接口地址**: `GET /api/bingjie/songs/`

**功能描述**: 获取冰洁的歌曲列表，支持筛选和搜索

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| language | string | 否 | 语言筛选 |
| style | string | 否 | 曲风筛选 |
| search | string | 否 | 搜索关键词（歌名或歌手） |

**响应示例**:

```json
[
  {
    "id": 1,
    "song_name": "歌曲名称",
    "language": "中文",
    "singer": "歌手名",
    "style": "流行",
    "note": "备注信息"
  }
]
```

---

### 2. 获取语言列表

**接口地址**: `GET /api/bingjie/languages/`

**功能描述**: 获取所有可用语言

**请求参数**: 无

**响应示例**:

```json
[
  "中文",
  "日语",
  "英语"
]
```

---

### 3. 获取曲风列表

**接口地址**: `GET /api/bingjie/styles/`

**功能描述**: 获取所有曲风

**请求参数**: 无

**响应示例**:

```json
[
  "流行",
  "抒情",
  "摇滚",
  "民谣"
]
```

---

### 4. 获取随机歌曲

**接口地址**: `GET /api/bingjie/random-song/`

**功能描述**: 随机返回一首歌曲，支持筛选条件

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| language | string | 否 | 语言筛选 |
| style | string | 否 | 曲风筛选 |
| search | string | 否 | 搜索关键词 |

**响应示例**:

```json
{
  "id": 123,
  "song_name": "歌曲名称",
  "language": "中文",
  "singer": "歌手名",
  "style": "流行",
  "note": "备注信息"
}
```

**错误响应** (404):

```json
{
  "error": "No songs available."
}
```

---

### 5. 获取网站设置

**接口地址**: `GET /api/bingjie/site-settings/`

**功能描述**: 获取冰洁的网站设置信息

**请求参数**: 无

**响应示例**:

```json
[
  {
    "id": 1,
    "position": 1,
    "photoURL": "1.png",
    "other_field": "其他字段值"
  }
]
```

---

### 6. 获取网站图标

**接口地址**: `GET /api/bingjie/favicon.ico`

**功能描述**: 获取网站的favicon图标

**请求参数**: 无

**响应**: 重定向到对应的图片文件或返回默认图标

---

## 静态文件访问

### 优优图片访问

**接口地址**: `GET /youyou_SongList_frontend/photos/<path>`

**功能描述**: 访问优优的图片资源

---

### 冰洁图片访问

**接口地址**: `GET /bingjie_SongList_frontend/photos/<path>`

**功能描述**: 访问冰洁的图片资源

---

## 通用说明

### 响应格式

所有API响应均为JSON格式，Content-Type为 `application/json; charset=utf-8`

### 分页参数

- `page`: 页码，从1开始
- `limit` / `page_size`: 每页数量
- 响应中包含 `total`（总数）、`page`（当前页）、`page_size`（每页数量）、`results`（数据列表）

### 缓存策略

部分API使用了Redis缓存以提升性能：
- 曲风列表：缓存1小时
- 标签列表：缓存1小时
- 推荐语：缓存5分钟
- 歌曲列表：缓存10分钟
- 演唱记录：缓存10分钟

### 错误响应

错误响应格式：

```json
{
  "error": "错误描述信息"
}
```

常见HTTP状态码：
- 200: 成功
- 404: 资源不存在
- 500: 服务器内部错误

---

## 更新日志

- 2025-01-10: 初始版本，整理所有API接口