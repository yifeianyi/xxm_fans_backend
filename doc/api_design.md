# XXM Fans Home API 设计文档

## 1. 歌曲列表接口

### 接口地址
GET /api/songs/

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| q | string | 否 | 搜索关键词（歌曲名或歌手） |
| page | integer | 否 | 页码，默认为1 |
| limit | integer | 否 | 每页数量，默认为50 |
| styles | string | 否 | 曲风筛选，多个曲风用逗号分隔 |
| ordering | string | 否 | 排序字段，支持：singer, last_performed, perform_count |

### 响应数据
```json
{
  "total": 100,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "id": 1,
      "song_name": "歌曲名",
      "singer": "歌手",
      "last_performed": "2023-01-01",
      "perform_count": 5,
      "language": "语言",
      "styles": ["曲风1", "曲风2"]
    }
  ]
}
```

## 2. 歌曲演唱记录接口

### 接口地址
GET /api/songs/{song_id}/records/

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 页码，默认为1 |
| page_size | integer | 否 | 每页数量，默认为20 |

### 响应数据
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "song": 1,
      "performed_at": "2023-01-01",
      "url": "https://example.com/video",
      "notes": "备注",
      "cover_url": "/covers/2023/01/2023-01-01.jpg"
    }
  ]
}
```

## 3. 曲风列表接口

### 接口地址
GET /api/styles/

### 响应数据
```json
[
  {
    "id": 1,
    "name": "曲风1"
  },
  {
    "id": 2,
    "name": "曲风2"
  }
]
```

## 4. 热歌榜接口

### 接口地址
GET /api/top_songs/

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| range | string | 否 | 时间范围，支持：all, 1m, 3m, 1y，默认为all |
| limit | integer | 否 | 返回歌曲数量，默认为10 |

### 响应数据
```json
[
  {
    "id": 1,
    "song_name": "歌曲名",
    "singer": "歌手",
    "perform_count": 5,
    "last_performed": "2023-01-01"
  }
]
```

## 5. 设备类型检测接口

### 接口地址
GET /api/is_mobile/

### 响应数据
```json
{
  "is_mobile": true
}
```

## 6. 合集相关接口

### 6.1 获取合集列表接口

#### 接口地址
GET /api/footprint/collections/

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 页码，默认为1 |
| limit | integer | 否 | 每页数量，默认为20 |

#### 响应数据
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "name": "合集名称",
      "works_count": 10,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### 6.2 获取合集详情接口

#### 接口地址
GET /api/footprint/collections/{collection_id}/

#### 响应数据
```json
{
  "id": 1,
  "name": "合集名称",
  "works_count": 10,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 6.3 获取作品列表接口

#### 接口地址
GET /api/footprint/works/

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | integer | 否 | 页码，默认为1 |
| limit | integer | 否 | 每页数量，默认为20 |
| collection | integer | 否 | 合集ID，用于筛选特定合集的作品 |

#### 响应数据
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "title": "作品标题",
      "cover_url": "https://example.com/cover.jpg",
      "view_url": "https://example.com/video",
      "author": "作者",
      "notes": "备注",
      "collection": {
        "id": 1,
        "name": "合集名称"
      }
    }
  ]
}
```

### 6.4 获取作品详情接口

#### 接口地址
GET /api/footprint/works/{work_id}/

#### 响应数据
```json
{
  "id": 1,
  "title": "作品标题",
  "cover_url": "https://example.com/cover.jpg",
  "view_url": "https://example.com/video",
  "author": "作者",
  "notes": "备注",
  "collection": {
    "id": 1,
    "name": "合集名称"
  }
}
```