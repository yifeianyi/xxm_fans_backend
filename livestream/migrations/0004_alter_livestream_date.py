from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('livestream', '0003_livestream_room_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livestream',
            name='date',
            field=models.DateField(
                help_text='直播日期，格式：YYYY-MM-DD',
                verbose_name='直播日期',
            ),
        ),
    ]

