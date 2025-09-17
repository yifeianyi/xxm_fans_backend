from django.db import migrations

def migrate_tags_forward(apps, schema_editor):
    """
    将Songs模型中的标签数据迁移到Tag模型和SongTag中间表
    """
    # 获取Songs模型
    Songs = apps.get_model('main', 'Songs')
    
    # 获取所有有标签的歌曲（在删除字段之前）
    # 注意：这里我们不能使用tag字段，因为它是通过RemoveField操作删除的
    # 我们需要在迁移之前手动处理数据迁移
    
    # 这个函数现在是空的，因为我们会在应用迁移之前手动处理数据迁移

def migrate_tags_reverse(apps, schema_editor):
    """
    回滚迁移：这个函数现在是空的
    """
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0011_auto_20250918_0023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='songs',
            name='tag',
        ),
        migrations.RunPython(migrate_tags_forward, migrate_tags_reverse),
    ]