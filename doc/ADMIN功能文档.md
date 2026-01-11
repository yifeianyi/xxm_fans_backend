# Django Admin 后台管理功能详细文档

## 项目概述
本文档详细列出了XXM Fans Home项目中所有Django Admin后台管理页面的核心功能，用于开发新的前端后台管理系统时参考。

---

## 一、main 应用

### 1.1 歌曲管理 (Songs)

#### 数据模型字段
- **song_name** (CharField) - 歌曲名称，最大200字符
- **singer** (CharField) - 歌手，最大200字符，可为空
- **last_performed** (DateField) - 最近演唱时间，可为空
- **perform_count** (IntegerField) - 演唱次数，默认0
- **language** (CharField) - 语言，最大50字符，可为空

#### 关联数据
- **曲风** - 通过SongStyle多对多关联
- **标签** - 通过SongTag多对多关联
- **演唱记录** - 通过SongRecord一对多关联

#### 核心功能需求
- 列表展示：歌名、歌手、语言、曲风、最近演唱时间、演唱次数
- 筛选：按语言、按最近演唱时间
- 搜索：按歌名、歌手、演唱次数
- 排序：按歌名、最近演唱时间、演唱次数
- 批量操作：
  - 合并歌曲（将多首歌曲合并为一首，转移演唱记录，累加演唱次数）
  - 拆分歌曲（将一首歌曲拆分为多首，按演唱记录拆分）
  - 批量设置语言
  - 批量添加曲风
  - 批量添加标签

---

### 1.2 演唱记录管理 (SongRecord)

#### 数据模型字段
- **song** (ForeignKey) - 关联歌曲
- **performed_at** (DateField) - 演唱日期
- **url** (URLField) - 视频链接，可为空
- **notes** (TextField) - 备注，可为空
- **cover_url** (CharField) - 封面URL，最大300字符，可为空

#### 核心功能需求
- 列表展示：歌曲、演唱日期、视频链接、封面URL、备注
- 筛选：按演唱日期、按歌曲
- 搜索：按歌曲名称、备注
- 批量操作：
  - 从BV号导入演唱记录（自动解析视频信息、处理歌曲冲突、下载封面）
- 封面管理：支持更换封面图

---

### 1.3 曲风管理 (Style)

#### 数据模型字段
- **name** (CharField) - 曲风名称，最大100字符，唯一

#### 核心功能需求
- 列表展示：曲风名称
- 搜索：按曲风名称
- 排序：按名称

---

### 1.4 标签管理 (Tag)

#### 数据模型字段
- **name** (CharField) - 标签名称，最大100字符，唯一

#### 核心功能需求
- 列表展示：标签名称
- 搜索：按标签名称
- 排序：按名称
- 批量操作：为选中的标签批量标记歌曲

---

### 1.5 歌曲曲风关联管理 (SongStyle)

#### 数据模型字段
- **song** (ForeignKey) - 关联歌曲
- **style** (ForeignKey) - 关联曲风

#### 核心功能需求
- 列表展示：歌曲、曲风
- 筛选：按曲风
- 搜索：按歌曲名称、曲风名称
- 批量操作：批量添加歌曲曲风（支持歌曲搜索、多选歌曲）

---

### 1.6 歌曲标签关联管理 (SongTag)

#### 数据模型字段
- **song** (ForeignKey) - 关联歌曲
- **tag** (ForeignKey) - 关联标签

#### 核心功能需求
- 列表展示：歌曲、标签
- 筛选：按标签
- 搜索：按歌曲名称、标签名称
- 批量操作：批量添加歌曲标签（支持歌曲搜索、多选歌曲）

---

### 1.7 推荐语管理 (Recommendation)

#### 数据模型字段
- **content** (TextField) - 推荐语内容
- **recommended_songs** (ManyToManyField) - 推荐的歌曲，可为空
- **is_active** (BooleanField) - 是否激活显示，默认True
- **created_at** (DateTimeField) - 创建时间，自动添加
- **updated_at** (DateTimeField) - 更新时间，自动更新

#### 核心功能需求
- 列表展示：推荐语预览、是否激活、更新时间、推荐歌曲数量
- 筛选：按是否激活、按更新时间
- 搜索：按推荐语内容
- 多选歌曲：支持多选歌曲关联

---

### 1.8 网站设置管理 (SiteSettings)

#### 数据模型字段
- **favicon** (ImageField) - 网站图标，可为空
- **created_at** (DateTimeField) - 创建时间，自动添加
- **updated_at** (DateTimeField) - 更新时间，自动更新

#### 核心功能需求
- 列表展示：网站图标预览、更新时间
- 图片上传：支持上传网站图标，自动转换为favicon.ico格式（32x32像素）

---

### 1.9 作品静态信息管理 (WorkStatic)

#### 数据模型字段
- **platform** (CharField) - 平台，最大50字符
- **work_id** (CharField) - 作品ID，最大100字符
- **title** (CharField) - 标题，最大500字符
- **author** (CharField) - 作者，最大200字符
- **publish_time** (DateTimeField) - 发布时间
- **cover_url** (URLField) - 封面URL，最大500字符，可为空
- **is_valid** (BooleanField) - 投稿是否有效，默认True

#### 核心功能需求
- 列表展示：标题、作者、平台、作品ID、发布时间
- 筛选：按平台、按发布时间
- 搜索：按标题、作者、作品ID
- 排序：按发布时间倒序

---

### 1.10 作品小时指标管理 (WorkMetricsHour)

#### 数据模型字段
- **platform** (CharField) - 平台，最大50字符
- **work_id** (CharField) - 作品ID，最大100字符
- **crawl_time** (DateTimeField) - 爬取时间
- **view_count** (IntegerField) - 播放数，默认0
- **like_count** (IntegerField) - 点赞数，默认0
- **coin_count** (IntegerField) - 投币数，默认0
- **favorite_count** (IntegerField) - 收藏数，默认0
- **danmaku_count** (IntegerField) - 弹幕数，默认0
- **comment_count** (IntegerField) - 评论数，默认0
- **session_id** (IntegerField) - 会话ID
- **ingest_time** (DateTimeField) - 入库时间，自动添加

#### 核心功能需求
- 列表展示：作品ID、平台、爬取时间、播放数、点赞数、投币数、收藏数、弹幕数、评论数
- 筛选：按平台、按爬取时间、按会话ID
- 搜索：按作品ID
- 排序：按爬取时间倒序

---

### 1.11 爬取会话管理 (CrawlSession)

#### 数据模型字段
- **source** (CharField) - 数据源，最大50字符
- **node_id** (CharField) - 节点ID，最大100字符
- **start_time** (DateTimeField) - 开始时间
- **end_time** (DateTimeField) - 结束时间，可为空
- **total_work_count** (IntegerField) - 总作品数，默认0
- **success_count** (IntegerField) - 成功数，默认0
- **fail_count** (IntegerField) - 失败数，默认0
- **note** (TextField) - 备注，可为空

#### 核心功能需求
- 列表展示：数据源、节点ID、开始时间、结束时间、总作品数、成功数、失败数
- 筛选：按数据源、按开始时间
- 搜索：按数据源、节点ID
- 排序：按开始时间倒序

---

## 二、fansDIY 应用

### 2.1 二创合集管理 (Collection)

#### 数据模型字段
- **name** (CharField) - 合集名称，最大200字符
- **works_count** (IntegerField) - 作品数量，默认0
- **display_order** (IntegerField) - 显示顺序，默认0
- **position** (IntegerField) - 位置，默认0
- **created_at** (DateTimeField) - 创建时间，自动添加
- **updated_at** (DateTimeField) - 更新时间，自动更新

#### 关联数据
- **作品** - 通过Work一对多关联

#### 核心功能需求
- 列表展示：合集名称、作品数量、位置、显示顺序、创建时间、更新时间
- 筛选：按创建时间、按更新时间
- 搜索：按合集名称
- 自动更新：保存/删除作品时自动更新作品数量
- 内联编辑：支持在合集页面直接编辑作品

---

### 2.2 作品记录管理 (Work)

#### 数据模型字段
- **collection** (ForeignKey) - 所属合集
- **title** (CharField) - 作品标题，最大300字符
- **cover_url** (CharField) - 封面图片地址，最大500字符，可为空
- **view_url** (URLField) - 观看链接，可为空
- **author** (CharField) - 作者，最大100字符
- **notes** (TextField) - 备注，可为空
- **display_order** (IntegerField) - 显示顺序，默认0
- **position** (IntegerField) - 位置，默认0

#### 核心功能需求
- 列表展示：作品标题、作者、所属合集、位置、显示顺序、封面预览、观看链接、备注预览
- 筛选：按合集、按作者
- 搜索：按标题、作者、合集名称、备注
- 批量操作：从BV号导入作品（自动创建合集、提取作品信息）
- 自动更新：保存/删除时自动更新合集的作品数量

---

## 三、bingjie_SongList 应用

### 3.1 歌曲管理 (bingjie_Songs)

#### 数据模型字段
- **song_name** (CharField) - 歌曲名称，最大200字符
- **language** (CharField) - 语言，最大50字符
- **singer** (CharField) - 歌手，最大100字符
- **style** (CharField) - 曲风，最大50字符
- **note** (TextField) - 备注，可为空

#### 核心功能需求
- 列表展示：歌曲名称、歌手、语言、曲风
- 筛选：按语言、按曲风
- 搜索：按歌曲名称、歌手

---

### 3.2 网站设置管理 (bingjie_site_setting)

#### 数据模型字段
- **photoURL** (CharField) - 图片URL，最大500字符
- **position** (IntegerField) - 位置（1: head_icon, 2: background）

#### 核心功能需求
- 列表展示：位置、图片预览
- 筛选：按位置
- 图片上传：支持上传图片，自动保存到前端photos目录和public目录，文件名使用position值命名

---

## 四、youyou_SongList 应用

### 4.1 歌曲管理 (you_Songs)

#### 数据模型字段
- **song_name** (CharField) - 歌曲名称，最大200字符
- **language** (CharField) - 语言，最大50字符
- **singer** (CharField) - 歌手，最大100字符
- **style** (CharField) - 曲风，最大50字符
- **note** (TextField) - 备注，可为空

#### 核心功能需求
- 列表展示：歌曲名称、语言、歌手、曲风
- 筛选：按语言、按曲风
- 搜索：按歌曲名称、歌手

---

### 4.2 网站设置管理 (you_site_setting)

#### 数据模型字段
- **photoURL** (CharField) - 图片URL，最大500字符
- **position** (IntegerField) - 位置（1: head_icon, 2: background）

#### 核心功能需求
- 列表展示：位置、图片预览
- 筛选：按位置
- 图片上传：支持上传图片，自动保存到前端photos目录和public目录，文件名使用position值命名

---

## 五、核心业务功能

### 5.1 BV导入功能
- 从B站BV号导入演唱记录和作品
- 自动解析视频信息和分P信息
- 支持歌曲冲突处理
- 自动下载封面图
- 自动创建歌曲（如果不存在）

### 5.2 批量操作
- 批量合并歌曲（转移演唱记录、累加演唱次数）
- 批量拆分歌曲（按演唱记录拆分）
- 批量设置语言
- 批量添加曲风/标签
- 批量标记歌曲

### 5.3 数据联动
- 作品数量自动更新
- 演唱次数自动计算
- 关联数据自动维护

### 5.4 图片处理
- 图片预览功能
- 自动生成缩略图
- 自动转换favicon格式（32x32像素）
- 自动保存到指定目录

---

## 六、数据库配置

项目配置了数据库路由 (`main.db_router.ViewDataDbRouter`):
- 默认使用 `db.sqlite3` 数据库
- 视图数据使用 `view_data.sqlite3` 数据库

---

## 总结

XXM Fans Home项目的Django Admin后台管理系统包含：

**应用模块（4个）**:
- main - 核心音乐管理、数据分析
- fansDIY - 粉丝二创作品管理
- bingjie_SongList - 冰洁歌单管理
- youyou_SongList - 优优歌单管理

**数据模型（17个）**:
- Songs - 歌曲
- SongRecord - 演唱记录
- Style - 曲风
- Tag - 标签
- SongStyle - 歌曲曲风关联
- SongTag - 歌曲标签关联
- Recommendation - 推荐语
- SiteSettings - 网站设置
- WorkStatic - 作品静态信息
- WorkMetricsHour - 作品小时指标
- CrawlSession - 爬取会话
- Collection - 二创合集
- Work - 作品记录
- bingjie_Songs - 冰洁歌曲
- bingjie_site_setting - 冰洁网站设置
- you_Songs - 优优歌曲
- you_site_setting - 优优网站设置

**核心功能**:
- BV导入、批量操作、数据联动、图片处理、搜索筛选、权限管理