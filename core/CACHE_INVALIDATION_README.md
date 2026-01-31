# 缓存自动清理功能说明

## 概述

当后端数据发生修改时（创建、更新、删除），系统会自动精细化清理相关的Redis缓存，确保前端始终获取最新的数据。缓存清理采用精细化策略，只清理真正受影响的缓存键，而不是清理整个应用的缓存。

## 精细化缓存清理策略

### 核心原则
- **最小影响**：只清理真正受影响的缓存键
- **精准匹配**：使用具体的缓存键模式进行清理
- **性能优化**：减少不必要的缓存删除操作

## 支持的缓存清理模式

### 1. song_management（歌曲管理）

#### SongRecord（演唱记录）
- **触发操作**：创建、更新、删除演唱记录
- **清理的缓存**：
  - `song_records:{song_id}` - 该歌曲的记录缓存
  - `top_songs` - 排行榜缓存
  - `random_song` - 随机歌曲缓存
- **原因**：演唱记录变化会影响歌曲统计、排行榜和随机选择

#### Song（歌曲）
- **触发操作**：创建、更新、删除歌曲
- **清理的缓存**：
  - `song_detail:{song_id}` - 该歌曲的详情缓存
  - `top_songs` - 排行榜缓存（更新时）
  - `random_song` - 随机歌曲缓存（更新时）
- **原因**：歌曲基本信息变化需要刷新详情页

#### SongStyle（歌曲-曲风关联）
- **触发操作**：创建、删除歌曲-曲风关联
- **清理的缓存**：
  - `song_detail:{song_id}` - 该歌曲的详情缓存
  - `top_songs` - 排行榜缓存
- **原因**：曲风变化可能影响筛选和排行榜

#### SongTag（歌曲-标签关联）
- **触发操作**：创建、删除歌曲-标签关联
- **清理的缓存**：
  - `song_detail:{song_id}` - 该歌曲的详情缓存
  - `top_songs` - 排行榜缓存
- **原因**：标签变化可能影响筛选和排行榜

#### OriginalWork（原创作品）
- **触发操作**：创建、更新、删除原创作品
- **清理的缓存**：
  - `original_works_list` - 原创作品列表缓存
- **原因**：原创作品列表需要实时更新

### 2. fansDIY（粉丝二创）

#### Collection（合集）
- **触发操作**：创建、更新、删除合集
- **清理的缓存**：
  - `collection_detail:{collection_id}` - 该合集的详情缓存
  - `get_collections` - 合集列表缓存
  - `get_works:collection_id={collection_id}` - 该合集下的作品列表缓存
- **原因**：合集信息变化会影响相关页面

#### Work（作品）
- **触发操作**：创建、更新、删除作品
- **清理的缓存**：
  - `get_work_by_id:{work_id}` - 该作品的详情缓存
  - `get_collections` - 合集列表缓存（作品数量可能变化）
  - `get_works:collection_id={collection_id}` - 该合集下的作品列表缓存
  - `get_works:` - 所有作品列表缓存
- **原因**：作品变化会影响合集列表和作品列表

### 3. site_settings（网站设置）

#### Recommendation（推荐语）
- **触发操作**：创建、更新、删除推荐语
- **清理的缓存**：
  - `get_recommendation` - 推荐语缓存
- **原因**：推荐语需要实时更新

#### SiteSettings（网站设置）
- **触发操作**：创建、更新、删除网站设置
- **清理的缓存**：
  - `get_site_settings` - 网站设置缓存
- **原因**：网站设置需要实时更新

#### Milestone（里程碑）
- **触发操作**：创建、更新、删除里程碑
- **清理的缓存**：
  - `get_milestones` - 里程碑列表缓存
  - `get_milestone:{milestone_id}` - 该里程碑的详情缓存
- **原因**：里程碑信息变化需要刷新

### 4. data_analytics（数据分析）

#### WorkStatic（作品统计数据）
- **触发操作**：创建、更新、删除作品统计数据
- **清理的缓存**：
  - `work_detail:{work_id}` - 该作品的详情缓存
- **原因**：统计数据变化需要刷新作品详情

#### WorkMetricsHour（作品小时级指标）
- **触发操作**：创建、更新、删除作品指标数据
- **清理的缓存**：
  - `work_metrics_summary:{work_id}` - 该作品的指标汇总缓存
- **原因**：指标数据变化需要刷新指标汇总

#### CrawlSession（爬取会话）
- **触发操作**：创建、更新、删除爬取会话
- **清理的缓存**：
  - `crawl_session_detail:{session_id}` - 该爬取会话的详情缓存
- **原因**：会话信息变化需要刷新详情

## 手动清理缓存

### 使用管理命令

```bash
# 清理所有缓存
python manage.py clear_cache

# 清理匹配指定模式的缓存
python manage.py clear_cache song_detail:1      # 清理 song_detail:1 缓存
python manage.py clear_cache top_songs          # 清理所有 top_songs 缓存
python manage.py clear_cache original_works_list # 清理原创作品列表缓存
python manage.py clear_cache get_works:         # 清理所有作品列表缓存
```

### 在代码中手动清理

```python
from core.cache import clear_cache_pattern, clear_all_cache

# 清理匹配特定模式的缓存
clear_cache_pattern('song_detail:1')           # 清理 song_detail:1 缓存
clear_cache_pattern('top_songs')               # 清理所有 top_songs 缓存
clear_cache_pattern('original_works_list')     # 清理原创作品列表缓存

# 清理所有缓存
clear_all_cache()
```

## 工作原理

### 信号处理器

系统使用 Django 的信号机制（`post_save` 和 `post_delete`）来监听模型的变化。当模型被创建、更新或删除时，对应的信号处理器会自动执行并精准清理相关缓存。

### 缓存清理流程

1. **模型变化**：用户通过 Admin 界面或 API 修改数据
2. **信号触发**：Django 触发 `post_save` 或 `post_delete` 信号
3. **缓存清理**：信号处理器调用 `clear_cache_pattern()` 函数
4. **Redis 清理**：系统使用 Redis 的 `KEYS` 命令查找匹配的缓存键，并使用 `DEL` 命令删除

### 缓存键生成规则

缓存键使用以下格式：
```
{key_prefix}:{参数列表}
```

例如：
- `song_detail:1` - ID 为 1 的歌曲详情
- `song_records:1:1:20` - ID 为 1 的歌曲，第 1 页，每页 20 条记录
- `top_songs:all:10` - 全部时间排行榜，前 10 首

### 支持的缓存后端

- **Redis**（推荐）：完全支持，使用 `KEYS` 命令进行模式匹配
- **LocMemCache**：支持，通过遍历内部缓存字典实现

## 测试缓存清理功能

使用测试脚本验证缓存清理是否正常工作：

```bash
python manage.py shell < tools/test_cache_invalidation.py
```

或在 Django shell 中运行：

```python
>>> exec(open('tools/test_cache_invalidation.py').read())
```

## 精细化清理的优势

### 与应用级清理的对比

| 特性 | 应用级清理 | 精细化清理 |
|------|-----------|-----------|
| 清理范围 | 整个应用的所有缓存 | 只清理受影响的缓存 |
| 性能影响 | 较大，可能清理不必要的缓存 | 较小，精准清理 |
| 缓存命中率 | 较低，可能清理其他用户的缓存 | 较高，保留其他用户缓存 |
| 并发性能 | 可能影响多个用户 | 只影响相关用户 |

### 示例对比

假设修改了 ID 为 1 的歌曲的演唱记录：

**应用级清理（旧方案）**：
```
清理的缓存：
- song_detail:* (所有歌曲详情)
- song_records:* (所有歌曲记录)
- songs_list:* (所有歌曲列表)
- random_song:* (所有随机歌曲)
- top_songs:* (所有排行榜)
```

**精细化清理（新方案）**：
```
清理的缓存：
- song_records:1 (歌曲1的记录)
- top_songs:* (排行榜)
- random_song:* (随机歌曲)
```

## 注意事项

1. **Redis 性能**：`KEYS` 命令在生产环境中可能会影响性能，如果缓存键数量很大，建议使用 Redis 的 `SCAN` 命令替代。

2. **缓存键命名**：确保所有使用 `@cache_result` 装饰器的函数都使用 `key_prefix` 参数，以便正确识别和清理缓存。

3. **开发环境**：开发环境通常使用 LocMemCache，缓存清理功能同样适用。

4. **生产环境**：生产环境建议使用 Redis，确保 Redis 服务正常运行。

5. **并发访问**：精细化清理保留了其他用户的缓存，提高了并发性能。

## 扩展

### 添加新的缓存清理规则

如果需要为新的操作添加精细化缓存清理：

```python
# 在 signals.py 中添加
from core.cache import clear_cache_pattern

@receiver(post_save, sender=YourModel)
def clear_cache_on_your_model_save(sender, instance, created, **kwargs):
    """
    当模型被创建或更新时，精细化清理缓存
    """
    # 清理该对象的详情缓存
    clear_cache_pattern(f'your_prefix:{instance.id}')
    # 清理相关的列表缓存
    clear_cache_pattern('your_list_prefix')
```

## 相关文件

- `core/cache.py` - 缓存模块，包含缓存装饰器和清理函数
- `song_management/models/signals.py` - 歌曲管理信号处理器
- `fansDIY/models/signals.py` - 粉丝二创信号处理器
- `site_settings/models/signals.py` - 网站设置信号处理器
- `data_analytics/models/signals.py` - 数据分析信号处理器
- `core/management/commands/clear_cache.py` - 手动清理缓存的管理命令
- `tools/test_cache_invalidation.py` - 缓存清理测试脚本