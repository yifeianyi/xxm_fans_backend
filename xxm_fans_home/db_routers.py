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
