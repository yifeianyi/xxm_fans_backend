"""
数据库路由配置 - 实现读写分离
"""
import random
from django.conf import settings

class MasterSlaveRouter:
    """
    混合数据库路由
    - songlist 应用：使用 SQLite3（songlist_db），不进行读写分离
    - 其他应用：使用 MySQL 主从，实现读写分离
    """

    def db_for_read(self, model, **hints):
        """读操作路由"""
        # songlist 应用使用 SQLite3
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        # 其他应用使用从库
        return 'slave'

    def db_for_write(self, model, **hints):
        """写操作路由"""
        # songlist 应用使用 SQLite3
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        # 其他应用使用主库
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """允许跨数据库关系"""
        # songlist 应用内部的关系
        if obj1._meta.app_label == 'songlist' and obj2._meta.app_label == 'songlist':
            return True
        # MySQL 主从之间的关系
        db_set = {'default', 'slave'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        # 不允许跨数据库的关系（songlist 和其他应用）
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """控制数据库迁移"""
        # songlist 应用只能迁移到 songlist_db（SQLite3）
        if app_label == 'songlist':
            return db == 'songlist_db'
        # 其他应用只能迁移到 MySQL（default 和 slave）
        return db in ('default', 'slave')


class MultiDbRouter:
    """
    多数据库路由器，将不同应用的数据路由到对应的数据库
    """

    # 数据库映射配置
    DATABASE_MAPPING = {
        'default': ['song_management', 'fansDIY', 'site_settings'],
        'view_data_db': ['data_analytics'],
        'songlist_db': ['songlist'],
    }

    # data_analytics应用中需要路由到view_data_db的模型
    VIEW_DATA_MODELS = ['workstatic', 'workmetricshour', 'crawlsession']

    def db_for_read(self, model, **hints):
        """
        指定模型读操作使用的数据库
        """
        app_label = model._meta.app_label
        model_name = model._meta.model_name.lower()

        # 特殊处理：data_analytics应用的数据分析模型
        if app_label == 'data_analytics' and model_name in self.VIEW_DATA_MODELS:
            return 'view_data_db'

        # 普通路由：根据应用标签路由
        for db_name, apps in self.DATABASE_MAPPING.items():
            if app_label in apps:
                return db_name
        return None

    def db_for_write(self, model, **hints):
        """
        指定模型写操作使用的数据库
        """
        app_label = model._meta.app_label
        model_name = model._meta.model_name.lower()

        # 特殊处理：data_analytics应用的数据分析模型
        if app_label == 'data_analytics' and model_name in self.VIEW_DATA_MODELS:
            return 'view_data_db'

        # 普通路由：根据应用标签路由
        for db_name, apps in self.DATABASE_MAPPING.items():
            if app_label in apps:
                return db_name
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        控制跨数据库的关系
        - 允许同一数据库内的模型建立关系
        - 禁止跨数据库的外键关系
        """
        db_set = {'default', 'view_data_db', 'songlist_db'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        控制模型迁移到哪个数据库
        """
        model_name_lower = model_name.lower() if model_name else None

        # 特殊处理：data_analytics应用的数据分析模型
        if app_label == 'data_analytics' and model_name_lower in self.VIEW_DATA_MODELS:
            return db == 'view_data_db'

        # 普通路由：根据应用标签路由
        if db in self.DATABASE_MAPPING:
            return app_label in self.DATABASE_MAPPING[db]
        return False
