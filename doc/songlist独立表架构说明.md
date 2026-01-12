# Songlist独立表架构说明

## 一、架构设计

### 1.1 设计理念
songlist应用采用"单应用多模型"的架构设计，通过基类继承实现代码复用，同时为每个歌手创建独立的数据库表，便于权限管理。

### 1.2 模型结构

#### 基类设计
```python
class BaseSong(models.Model):
    """歌曲基类"""
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    singer = models.CharField(max_length=100, verbose_name='原唱歌手')
    language = models.CharField(max_length=50, verbose_name='语言')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        abstract = True  # 抽象基类，不会创建数据库表
        ordering = ['song_name']


class BaseSiteSetting(models.Model):
    """网站设置基类"""
    photo_url = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(
        verbose_name='位置',
        choices=[
            (1, '头像图标'),
            (2, '背景图片'),
        ]
    )

    class Meta:
        abstract = True  # 抽象基类，不会创建数据库表
```

#### 独立模型
```python
# 乐游歌手的独立表
class YouyouSong(BaseSong):
    """乐游歌曲表"""
    class Meta:
        verbose_name = '乐游歌曲'
        verbose_name_plural = '乐游歌曲'


class YouyouSiteSetting(BaseSiteSetting):
    """乐游网站设置表"""
    class Meta:
        verbose_name = '乐游网站设置'
        verbose_name_plural = '乐游网站设置'


# 冰洁歌手的独立表
class BingjieSong(BaseSong):
    """冰洁歌曲表"""
    class Meta:
        verbose_name = '冰洁歌曲'
        verbose_name_plural = '冰洁歌曲'


class BingjieSiteSetting(BaseSiteSetting):
    """冰洁网站设置表"""
    class Meta:
        verbose_name = '冰洁网站设置'
        verbose_name_plural = '冰洁网站设置'
```

### 1.3 数据库表结构
```
songlist_db/
├── songlist_youyousong          # 乐游歌曲表（311首）
├── songlist_youyousitesetting   # 乐游网站设置表（2条）
├── songlist_bingjiesong         # 冰洁歌曲表（199首）
└── songlist_bingjiesitesetting  # 冰洁网站设置表（2条）
```

## 二、架构优势

### 2.1 与原来两个独立App的对比

| 方面 | 原来的两个App | 现在的单App多模型 |
|------|--------------|------------------|
| **代码重复** | 高（两份几乎相同的代码） | 低（使用基类继承） |
| **维护成本** | 高（需要同步修改） | 低（修改基类即可） |
| **权限管理** | 可独立设置 | 可独立设置 |
| **API接口** | 需要两套URL | 一套URL，通过参数区分 |
| **数据库表** | 分散在不同app | 统一在songlist应用 |
| **代码结构** | 每个app有完整的文件结构 | 共享views.py、urls.py、admin.py |

### 2.2 核心优势

1. **代码复用**：通过抽象基类实现，减少代码重复
2. **易于维护**：修改基类即可影响所有子模型
3. **权限隔离**：每个歌手的表完全独立，可设置不同权限
4. **扩展性强**：添加新歌手只需创建新的模型类
5. **统一API**：通过`artist`参数区分不同歌手，前端调用简单

## 三、API使用方式

### 3.1 歌曲列表
```
GET /api/songlist/songs/?artist=youyou
GET /api/songlist/songs/?artist=bingjie
GET /api/songlist/songs/  # 不传artist参数返回所有数据
```

### 3.2 语言列表
```
GET /api/songlist/languages/?artist=youyou
GET /api/songlist/languages/?artist=bingjie
```

### 3.3 曲风列表
```
GET /api/songlist/styles/?artist=youyou
GET /api/songlist/styles/?artist=bingjie
```

### 3.4 随机歌曲
```
GET /api/songlist/random/?artist=youyou
GET /api/songlist/random/?artist=bingjie
```

### 3.5 网站设置
```
GET /api/songlist/settings/?artist=youyou
GET /api/songlist/settings/?artist=bingjie
```

## 四、添加新歌手操作指南

### 4.1 步骤一：创建数据模型

在 `songlist/models.py` 中添加新的模型类：

```python
class NewArtistSong(BaseSong):
    """新歌手歌曲表"""
    class Meta:
        verbose_name = '新歌手歌曲'
        verbose_name_plural = '新歌手歌曲'


class NewArtistSiteSetting(BaseSiteSetting):
    """新歌手网站设置表"""
    class Meta:
        verbose_name = '新歌手网站设置'
        verbose_name_plural = '新歌手网站设置'
```

### 4.2 步骤二：更新Admin配置

在 `songlist/admin.py` 中注册新的模型：

```python
@admin.register(NewArtistSong)
class NewArtistSongAdmin(admin.ModelAdmin):
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(NewArtistSiteSetting)
class NewArtistSiteSettingAdmin(admin.ModelAdmin):
    list_display = ['photo_url', 'position']
    list_filter = ['position']
    list_per_page = 50
```

### 4.3 步骤三：更新API视图

在 `songlist/views.py` 中更新各个视图函数，添加新歌手的支持：

```python
# song_list函数
def song_list(request):
    artist = request.GET.get('artist', '')

    if artist == 'youyou':
        songs = YouyouSong.objects.all()
    elif artist == 'bingjie':
        songs = BingjieSong.objects.all()
    elif artist == 'newartist':  # 新增
        songs = NewArtistSong.objects.all()  # 新增
    else:
        # 合并所有歌手的数据
        # ... 省略

    # 应用筛选条件
    # ...

# language_list、style_list、random_song、site_settings、favicon函数
# 都需要按照相同的方式添加新歌手的支持
```

### 4.4 步骤四：创建数据库迁移

```bash
python3 manage.py makemigrations songlist
python3 manage.py migrate songlist --database=songlist_db
```

### 4.5 步骤五：导入数据

创建数据迁移脚本或手动导入数据：

**方式一：创建迁移脚本**

```python
# songlist/management/commands/migrate_newartist.py
from django.core.management.base import BaseCommand
from songlist.models import NewArtistSong, NewArtistSiteSetting

class Command(BaseCommand):
    help = '导入新歌手数据'

    def handle(self, *args, **options):
        # 从原始数据源导入歌曲
        # NewArtistSong.objects.create(
        #     song_name='歌曲名',
        #     singer='原唱歌手',
        #     language='语言',
        #     style='曲风',
        #     note='备注'
        # )

        # 导入网站设置
        # NewArtistSiteSetting.objects.create(
        #     photo_url='图片URL',
        #     position=1
        # )

        self.stdout.write(self.style.SUCCESS('新歌手数据导入完成'))
```

**方式二：通过Admin后台手动添加**

1. 登录admin后台
2. 找到"新歌手歌曲"模块
3. 点击"增加"按钮
4. 手动添加歌曲信息
5. 同样方式添加网站设置

### 4.6 步骤六：设置权限（可选）

如果需要为新歌手设置独立的管理员权限：

```bash
# 创建新歌手的管理员账号
python3 manage.py createsuperuser --username newartist_admin --email newartist@example.com

# 设置密码
python3 manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='newartist_admin'); u.set_password('password123'); u.save()"

# 分配权限
# 方法1：通过Admin后台分配
# 1. 登录admin后台
# 2. 进入"用户"管理
# 3. 编辑newartist_admin用户
# 4. 在"权限"部分，只勾选"新歌手歌曲"和"新歌手网站设置"的权限

# 方法2：通过代码分配
python3 manage.py shell << 'EOF'
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from songlist.models import NewArtistSong, NewArtistSiteSetting

user = User.objects.get(username='newartist_admin')

# 获取新歌手模型的权限
song_ct = ContentType.objects.get_for_model(NewArtistSong)
setting_ct = ContentType.objects.get_for_model(NewArtistSiteSetting)

song_perms = Permission.objects.filter(content_type=song_ct)
setting_perms = Permission.objects.filter(content_type=setting_ct)

# 分配权限
for perm in song_perms:
    user.user_permissions.add(perm)

for perm in setting_perms:
    user.user_permissions.add(perm)

print('权限分配完成')
EOF
```

### 4.7 步骤七：测试验证

```bash
# 测试API接口
curl "http://127.0.0.1:8000/api/songlist/songs/?artist=newartist"

# 验证数据
python3 manage.py shell << 'EOF'
from songlist.models import NewArtistSong, NewArtistSiteSetting
print('新歌手歌曲数:', NewArtistSong.objects.count())
print('新歌手设置数:', NewArtistSiteSetting.objects.count())
EOF
```

## 五、注意事项

1. **命名规范**：新歌手的模型类名建议使用 `歌手名Song` 和 `歌手名SiteSetting` 格式
2. **artist参数**：API中的artist参数值应与歌手标识一致（小写）
3. **权限隔离**：确保新歌手的管理员只能访问自己的数据
4. **数据迁移**：如果有原始数据，建议编写迁移脚本批量导入
5. **测试验证**：添加新歌手后，务必测试所有API接口是否正常工作

## 六、完整示例：添加歌手"xiaoming"

```python
# 1. models.py
class XiaomingSong(BaseSong):
    class Meta:
        verbose_name = '小明歌曲'
        verbose_name_plural = '小明歌曲'


class XiaomingSiteSetting(BaseSiteSetting):
    class Meta:
        verbose_name = '小明网站设置'
        verbose_name_plural = '小明网站设置'

# 2. admin.py
@admin.register(XiaomingSong)
class XiaomingSongAdmin(admin.ModelAdmin):
    list_display = ['song_name', 'singer', 'language', 'style']
    list_filter = ['language', 'style']
    search_fields = ['song_name', 'singer']
    list_per_page = 50


@admin.register(XiaomingSiteSetting)
class XiaomingSiteSettingAdmin(admin.ModelAdmin):
    list_display = ['photo_url', 'position']
    list_filter = ['position']
    list_per_page = 50

# 3. views.py (在song_list函数中添加)
elif artist == 'xiaoming':
    songs = XiaomingSong.objects.all()

# 其他函数同理...

# 4. 创建迁移
python3 manage.py makemigrations songlist
python3 manage.py migrate songlist --database=songlist_db

# 5. 使用API
GET /api/songlist/songs/?artist=xiaoming
```

通过以上步骤，可以轻松地为songlist应用添加新的歌手，同时保持代码的整洁和权限的独立性。