"""
数据库路由配置
用于将 songlist 应用的模型路由到 songlist_db 数据库
"""


class SonglistRouter:
    """
    songlist 应用数据库路由
    将 songlist 应用的所有模型路由到 songlist_db 数据库
    """

    def db_for_read(self, model, **hints):
        """读取操作路由"""
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        return None

    def db_for_write(self, model, **hints):
        """写入操作路由"""
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """允许关系"""
        if obj1._meta.app_label == 'songlist' and obj2._meta.app_label == 'songlist':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """允许迁移"""
        if app_label == 'songlist':
            return db == 'songlist_db'
        return None