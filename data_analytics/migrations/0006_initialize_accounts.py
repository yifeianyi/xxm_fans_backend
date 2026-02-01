"""
初始化账号配置数据
"""
from django.db import migrations


def create_initial_accounts(apps, schema_editor):
    """创建初始账号配置"""
    Account = apps.get_model('data_analytics', 'Account')

    accounts = [
        {
            'uid': '388828249',
            'name': '咻咻满',
            'platform': 'bilibili',
            'is_active': True
        },
        {
            'uid': '435525530',
            'name': '咻小满',
            'platform': 'bilibili',
            'is_active': True
        }
    ]

    for acc_data in accounts:
        Account.objects.get_or_create(
            uid=acc_data['uid'],
            defaults=acc_data
        )


class Migration(migrations.Migration):
    dependencies = [
        ('data_analytics', '0005_account_followermetrics'),
    ]

    operations = [
        migrations.RunPython(create_initial_accounts),
    ]