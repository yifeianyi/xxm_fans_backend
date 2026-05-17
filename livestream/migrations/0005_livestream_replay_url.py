from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('livestream', '0004_alter_livestream_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='livestream',
            name='replay_url',
            field=models.CharField(
                blank=True,
                default='',
                help_text='完整回放地址，如：https://www.bilibili.com/video/BVxxxx/?p=3',
                max_length=500,
                verbose_name='直播回放地址',
            ),
        ),
    ]

