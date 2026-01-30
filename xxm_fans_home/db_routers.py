"""
数据库路由配置
用于将 songlist 应用的模型路由到 songlist_db 数据库
将 data_analytics 应用的模型路由到 view_data_db 数据库
"""


class MultiDBRouter:
    """
    多应用数据库路由
    - songlist 应用使用 songlist_db 数据库
    - data_analytics 应用使用 view_data_db 数据库
    - 其他应用使用 default 数据库
    """

    APP_DB_MAPPING = {
        'songlist': 'songlist_db',
        'data_analytics': 'view_data_db',
    }

    def db_for_read(self, model, **hints):
        """读取操作路由"""
        app_label = model._meta.app_label
        return self.APP_DB_MAPPING.get(app_label)

    def db_for_write(self, model, **hints):
        """写入操作路由"""
        app_label = model._meta.app_label
        return self.APP_DB_MAPPING.get(app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """允许关系"""
        app_label1 = obj1._meta.app_label
        app_label2 = obj2._meta.app_label

        # 同一应用内的关系允许
        if app_label1 == app_label2:
            return True

        # 如果两个应用使用同一个数据库，允许关系
        db1 = self.APP_DB_MAPPING.get(app_label1, 'default')
        db2 = self.APP_DB_MAPPING.get(app_label2, 'default')
        if db1 == db2:
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """允许迁移"""
        target_db = self.APP_DB_MAPPING.get(app_label, 'default')
        return db == target_db


# 保留原有的 SonglistRouter 以兼容旧代码
class SonglistRouter(MultiDBRouter):
    """
    songlist 应用数据库路由（兼容旧版本）
    将 songlist 应用的所有模型路由到 songlist_db 数据库
    """