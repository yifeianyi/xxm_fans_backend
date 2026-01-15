# XXM Fans Home API 文档

## 基础信息

- **基础URL**: `http://127.0.0.1:8000`
- **响应格式**: JSON
- **字符编码**: UTF-8

## 统一响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 分页响应

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 50,
    "results": [ ... ]
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "操作失败",
  "errors": { ... }
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 歌曲管理 API

### 1. 获取歌曲列表

**接口**: `GET /api/songs/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 50，最大 50 |
| q | string | 否 | 搜索关键词（歌曲名或歌手） |
| language | string | 否 | 语言过滤，多个用逗号分隔 |
| styles | string | 否 | 曲风过滤，多个用逗号分隔 |
| tags | string | 否 | 标签过滤，多个用逗号分隔 |
| ordering | string | 否 | 排序字段（singer, last_performed, perform_count） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取歌曲列表成功",
  "data": {
    "total": 1349,
    "page": 1,
    "page_size": 50,
    "results": [
      {
        "id": 222,
        "song_name": "11",
        "singer": "邓紫棋",
        "language": "国语",
        "last_performed": "2025-10-26",
        "perform_count": 17,
        "styles": ["流行"],
        "tags": [],
        "records": [
          {
            "id": 17878,
            "performed_at": "2025-10-26",
            "url": "https://player.bilibili.com/player.html?bvid=BV1W2smz9Eb2&p=3",
            "notes": null,
            "cover_url": "/covers/2025/10/2025-10-26.jpg",
            "song": 222
          }
        ]
      }
    ]
  }
}
```

---

### 2. 获取歌曲演唱记录

**接口**: `GET /api/songs/{song_id}/records/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| song_id | int | 是 | 歌曲 ID |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20 |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取演唱记录成功",
  "data": {
    "total": 17,
    "page": 1,
    "page_size": 3,
    "results": [
      {
        "id": 17878,
        "performed_at": "2025-10-26",
        "url": "https://player.bilibili.com/player.html?bvid=BV1W2smz9Eb2&p=3",
        "notes": null,
        "cover_url": "/covers/2025/10/2025-10-26.jpg",
        "song": 222
      }
    ]
  }
}
```

---

### 3. 获取曲风列表

**接口**: `GET /api/styles/`

**响应示例**:

```json
{
  "code": 200,
  "message": "获取曲风列表成功",
  "data": ["RAP", "儿歌", "古风", "戏腔", "摇滚", "民族", "流行", "美声"]
}
```

---

### 4. 获取标签列表

**接口**: `GET /api/tags/`

**响应示例**:

```json
{
  "code": 200,
  "message": "获取标签列表成功",
  "data": ["Ban位", "remix", "儿歌", "助眠", "小甜歌", "有清唱", "渣女三部曲", "满绝", "老歌"]
}
```

---

### 5. 获取排行榜

**接口**: `GET /api/top_songs/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| range | string | 否 | 时间范围（all, 1m, 3m, 1y, 10d, 20d, 30d），默认 all |
| limit | int | 否 | 返回数量，默认 10 |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取排行榜成功",
  "data": [
    {
      "id": 222,
      "song_name": "11",
      "singer": "邓紫棋",
      "perform_count": 17,
      "last_performed": "2025-10-26"
    }
  ]
}
```

---

### 6. 获取随机歌曲

**接口**: `GET /api/random-song/`

**响应示例**:

```json
{
  "code": 200,
  "message": "获取随机歌曲成功",
  "data": {
    "id": 448,
    "song_name": "蜀绣",
    "singer": "李宇春",
    "styles": ["流行", "古风"],
    "last_performed": "2023-06-06",
    "perform_count": 10,
    "language": "国语"
  }
}
```

---

## 粉丝二创 API

### 1. 获取合集列表

**接口**: `GET /api/fansDIY/collections/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取合集列表成功",
  "data": {
    "total": 3,
    "page": 1,
    "page_size": 3,
    "results": [
      {
        "id": 3,
        "name": "test3",
        "works_count": 1,
        "position": 0,
        "display_order": 0,
        "created_at": "2026-01-12T21:58:21.750013Z",
        "updated_at": "2026-01-12T21:58:21.750021Z"
      }
    ]
  }
}
```

---

### 2. 获取合集详情

**接口**: `GET /api/fansDIY/collections/{collection_id}/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| collection_id | int | 是 | 合集 ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取合集详情成功",
  "data": {
    "id": 3,
    "name": "test3",
    "works_count": 1,
    "position": 0,
    "display_order": 0,
    "created_at": "2026-01-12T21:58:21.750013Z",
    "updated_at": "2026-01-12T21:58:21.750021Z"
  }
}
```

---

### 3. 获取作品列表

**接口**: `GET /api/fansDIY/works/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| collection | int | 否 | 合集 ID，用于筛选 |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取作品列表成功",
  "data": {
    "total": 1,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "title": "作品标题",
        "cover_url": "https://example.com/cover.jpg",
        "view_url": "https://example.com/work",
        "author": "作者",
        "notes": "备注",
        "position": 0,
        "display_order": 0,
        "collection": {
          "id": 1,
          "name": "合集名称"
        }
      }
    ]
  }
}
```

---

### 4. 获取作品详情

**接口**: `GET /api/fansDIY/works/{work_id}/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| work_id | int | 是 | 作品 ID |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取作品详情成功",
  "data": {
    "id": 1,
    "title": "作品标题",
    "cover_url": "https://example.com/cover.jpg",
    "view_url": "https://example.com/work",
    "author": "作者",
    "notes": "备注",
    "position": 0,
    "display_order": 0,
    "collection": {
      "id": 1,
      "name": "合集名称"
    }
  }
}
```

---

## 网站设置 API

### 1. 获取推荐内容

**接口**: `GET /api/recommendation/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| all | boolean | 否 | 是否返回所有推荐，默认 false |
| is_active | boolean | 否 | 是否只返回激活的推荐 |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取推荐语列表成功",
  "data": [
    {
      "id": 1,
      "content": "站长墙裂推荐（欢迎多点点）！！！",
      "recommended_songs": [849, 585, 645, 1165],
      "recommended_songs_details": [
        {
          "id": 849,
          "song_name": "宠坏",
          "singer": "小潘潘",
          "language": "国语"
        },
        {
          "id": 585,
          "song_name": "梦一场",
          "singer": "那英",
          "language": "国语"
        },
        {
          "id": 645,
          "song_name": "爱河",
          "singer": "ZaZaZsu咂咂苏",
          "language": "国语"
        },
        {
          "id": 1165,
          "song_name": "过客",
          "singer": "周思涵",
          "language": "国语"
        }
      ],
      "is_active": true,
      "created_at": "2026-01-14T06:43:26.183678+08:00",
      "updated_at": "2026-01-14T06:43:26.183708+08:00"
    }
  ]
}
```

---

### 2. 获取网站设置

**接口**: `GET /api/site-settings/settings/`

**响应示例**:

```json
{
  "code": 200,
  "message": "获取网站设置成功",
  "data": {
    "id": 1,
    "favicon": "/static/favicon.ico",
    "created_at": "2026-01-14T06:43:26.183678+08:00",
    "updated_at": "2026-01-14T06:43:26.183708+08:00"
  }
}
```

---

## 数据分析 API

### 1. 获取作品列表

**接口**: `GET /api/data-analytics/works/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 否 | 平台过滤 |
| is_valid | boolean | 否 | 是否有效 |
| limit | int | 否 | 返回数量，默认 100 |
| offset | int | 否 | 偏移量，默认 0 |

**响应示例**:

```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "platform": "bilibili",
      "work_id": "BV1234567890",
      "title": "作品标题",
      "publish_time": "2026-01-14T06:43:26.183678+08:00",
      "is_valid": true
    }
  ]
}
```

---

### 2. 获取作品指标汇总

**接口**: `GET /api/data-analytics/works/{platform}/{work_id}/metrics/summary/`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| platform | string | 是 | 平台 |
| work_id | string | 是 | 作品 ID |
| start_time | string | 否 | 开始时间 |
| end_time | string | 否 | 结束时间 |

**响应示例**:

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "view_count": 10000,
    "like_count": 500,
    "comment_count": 100,
    "share_count": 50
  }
}
```

---

## 歌单 API（模板化）

### 1. 获取歌手歌曲列表

**接口**: `GET /api/songlist/songs/?artist={artist}`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artist | string | 是 | 歌手标识（youyou, bingjie等） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "song_name": "歌曲名称",
      "singer": "歌手",
      "language": "国语",
      "styles": ["流行"],
      "tags": []
    }
  ]
}
```

---

### 2. 获取歌手语言列表

**接口**: `GET /api/songlist/languages/?artist={artist}`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artist | string | 是 | 歌手标识（youyou, bingjie等） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": ["国语", "英语", "日语"]
}
```

---

### 3. 获取歌手曲风列表

**接口**: `GET /api/songlist/styles/?artist={artist}`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artist | string | 是 | 歌手标识（youyou, bingjie等） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": ["流行", "古风", "摇滚"]
}
```

---

### 4. 获取歌手随机歌曲

**接口**: `GET /api/songlist/random/?artist={artist}`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artist | string | 是 | 歌手标识（youyou, bingjie等） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 1,
    "song_name": "歌曲名称",
    "singer": "歌手",
    "language": "国语",
    "styles": ["流行"]
  }
}
```

---

### 5. 获取歌手网站设置

**接口**: `GET /api/songlist/settings/?artist={artist}`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| artist | string | 是 | 歌手标识（youyou, bingjie等） |

**响应示例**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "site_name": "网站名称",
    "description": "网站描述",
    "favicon": "/static/favicon.ico"
  }
}
```

---

## 错误处理

### 404 错误示例

```json
{
  "code": 404,
  "message": "合集不存在: 99999"
}
```

### 参数错误示例

```json
{
  "code": 400,
  "message": "参数无效",
  "errors": {
    "song_id": ["该字段是必填项"]
  }
}
```

---

## 注意事项

1. 所有时间格式均为 ISO 8601 格式
2. 分页从 1 开始
3. 列表接口默认返回 50 条记录（部分接口为 20 条）
4. 封面 URL 默认格式：`/covers/{year}/{month}/{date}.jpg`
5. B站视频链接格式：`https://player.bilibili.com/player.html?bvid={bvid}&p={p}`

---

## 更新日志

- 2026-01-14: 统一响应格式，添加异常处理中间件
- 2026-01-14: 修复 Redis 缓存配置错误
- 2026-01-14: 添加推荐接口路由 `/api/recommendation/`