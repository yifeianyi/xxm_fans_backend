# Songlist应用重构实现方案

## 一、问题分析

### 1.1 当前问题
- songlist应用设计为模板化的歌单系统，需要支持多个歌手（如bingjie、youyou）
- 当前songlist.sqlite3数据库结构存在问题，无法区分不同歌手的数据
- 原始数据存储在db.sqlite3中，包含两个独立的表：
  - `youyou_SongList_you_songs` (311首歌曲)
  - `bingjie_SongList_bingjie_songs` (199首歌曲)

### 1.2 现有数据结构分析

#### 原始表结构（db.sqlite3）
```sql
-- youyou_SongList_you_songs / bingjie_SongList_bingjie_songs
CREATE TABLE (
    id INTEGER PRIMARY KEY,
    song_name VARCHAR(200) NOT NULL,
    language VARCHAR(50) NOT NULL,
    singer VARCHAR(100) NOT NULL,
    style VARCHAR(50) NOT NULL,
    note TEXT NOT NULL
)
```

#### 当前songlist模型结构
```python
class Song(models.Model):
    song_name = models.CharField(max_length=200)
    singer = models.CharField(max_length=100)  # 歌曲的原唱歌手
    language = models.CharField(max_length=50)
    style = models.CharField(max_length=50)
    note = models.TextField(blank=True)
```

**问题**：当前模型中的`singer`字段表示歌曲的原唱歌手，而不是歌单所属的歌手（如bingjie、youyou），导致无法区分不同歌手的专属歌单。

## 二、重构方案

### 2.1 数据模型重新设计

#### 新增字段
在`Song`模型中添加`artist`字段，用于标识歌单所属的歌手：

```python
class Song(models.Model):
    """统一的歌曲模型 - 支持多歌手歌单"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=100, verbose_name='原唱歌手')
    artist = models.CharField(
        max_length=50,
        choices=[
            ('bingjie', '冰洁'),
            ('youyou', '乐游'),
        ],
        verbose_name='歌单歌手'
    )
    language = models.CharField(max_length=50, verbose_name='语言')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '歌曲'
        verbose_name_plural = '歌曲'
        ordering = ['artist', 'song_name']
        indexes = [
            models.Index(fields=['artist']),
            models.Index(fields=['artist', 'language']),
            models.Index(fields=['artist', 'style']),
        ]

    def __str__(self):
        return f"{self.song_name} ({self.get_artist_display()})"
```

#### SiteSetting模型调整
同样为SiteSetting模型添加`artist`字段：

```python
class SiteSetting(models.Model):
    """网站设置模型 - 支持多歌手网站设置"""
    artist = models.CharField(
        max_length=50,
        choices=[
            ('bingjie', '冰洁'),
            ('youyou', '乐游'),
        ],
        verbose_name='歌单歌手'
    )
    photo_url = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(
        verbose_name='位置',
        choices=[
            (1, '头像图标'),
            (2, '背景图片'),
        ]
    )

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'
        unique_together = [['artist', 'position']]

    def __str__(self):
        return f"{self.get_artist_display()} - {self.get_position_display()}"
```

### 2.2 数据迁移策略

#### 迁移步骤
1. 创建新的数据库迁移文件，添加`artist`字段
2. 编写数据迁移脚本，从db.sqlite3导出数据：
   - 从`youyou_SongList_you_songs`导出数据，设置`artist='youyou'`
   - 从`bingjie_SongList_bingjie_songs`导出数据，设置`artist='bingjie'`
   - 从对应的site_setting表导出设置数据
3. 执行迁移
4. 验证数据完整性

#### 迁移脚本结构
```python
# songlist/management/commands/migrate_from_db.py
from django.core.management.base import BaseCommand
from django.db import connection
from songlist.models import Song, SiteSetting

class Command(BaseCommand):
    help = '从db.sqlite3迁移数据到songlist应用'

    def handle(self, *args, **options):
        # 迁移youyou数据
        self.migrate_artist_data('youyou_SongList_you_songs', 'youyou_SongList_you_site_setting', 'youyou')
        # 迁移bingjie数据
        self.migrate_artist_data('bingjie_SongList_bingjie_songs', 'bingjie_SongList_bingjie_site_setting', 'bingjie')

    def migrate_artist_data(self, songs_table, settings_table, artist):
        # 实现数据迁移逻辑
        pass
```

### 2.3 API接口调整

#### 更新API视图，支持按歌手筛选
```python
def song_list(request):
    """歌曲列表API - 支持按歌手筛选"""
    artist = request.GET.get('artist', '')  # 新增参数
    language = request.GET.get('language', '')
    style = request.GET.get('style', '')
    search = request.GET.get('search', '')

    songs = Song.objects.all()

    # 歌手筛选（新增）
    if artist:
        songs = songs.filter(artist=artist)

    # 其他筛选条件保持不变
    if language:
        songs = songs.filter(language=language)
    if style:
        songs = songs.filter(style=style)
    if search:
        songs = songs.filter(
            Q(song_name__icontains=search) | Q(singer__icontains=search)
        )

    songs = songs.values()
    return JsonResponse(list(songs), safe=False)
```

#### 更新其他API接口
- `language_list`: 支持按歌手筛选语言列表
- `style_list`: 支持按歌手筛选曲风列表
- `random_song`: 支持按歌手筛选随机歌曲
- `site_settings`: 支持按歌手获取网站设置

## 三、实施步骤

### 阶段一：模型调整
1. 修改`songlist/models.py`，添加`artist`字段
2. 创建并执行数据库迁移
3. 更新Admin界面，支持按歌手管理

### 阶段二：数据迁移
1. 编写数据迁移脚本`migrate_from_db.py`
2. 从db.sqlite3导出youyou和bingjie的数据
3. 验证数据迁移的完整性和准确性

### 阶段三：API更新
1. 更新`songlist/api_views.py`，所有接口支持按歌手筛选
2. 测试API接口功能
3. 更新API文档

### 阶段四：测试验证
1. 验证数据完整性（歌曲数量、字段内容）
2. 测试API接口功能
3. 验证前端兼容性

## 四、预期效果

### 4.1 数据结构优化
- 清晰区分不同歌手的专属歌单
- 支持灵活的歌手扩展（未来可添加新歌手）
- 数据查询性能优化（通过索引）

### 4.2 API功能增强
- 支持按歌手筛选歌曲列表
- 支持按歌手获取语言/曲风列表
- 支持按歌手获取随机歌曲
- 支持按歌手获取网站设置

### 4.3 前端适配
- 前端可通过`?artist=youyou`参数获取乐游的歌单
- 前端可通过`?artist=bingjie`参数获取冰洁的歌单
- 保持向后兼容（不传artist参数返回所有数据）

## 五、注意事项

1. **数据备份**：执行迁移前备份现有数据库
2. **字段区分**：明确`singer`（原唱歌手）和`artist`（歌单歌手）的区别
3. **索引优化**：为`artist`字段添加索引，提升查询性能
4. **唯一约束**：SiteSetting模型添加`artist`和`position`的唯一约束
5. **向后兼容**：API接口保持向后兼容，不传artist参数时返回所有数据