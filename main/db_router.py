class ViewDataDbRouter:
    """
    数据库路由器，用于将数据分析相关模型路由到 view_data_db 数据库
    """
    
    view_data_apps = ['main']
    view_data_models = ['workstatic', 'workmetricshour', 'crawlsession']
    
    def db_for_read(self, model, **hints):
        """
        指定数据分析相关模型的读操作使用 view_data_db 数据库
        """
        if (model._meta.app_label in self.view_data_apps and 
            model._meta.model_name.lower() in self.view_data_models):
            return 'view_data_db'
        return None
    
    def db_for_write(self, model, **hints):
        """
        指定数据分析相关模型的写操作使用 view_data_db 数据库
        """
        if (model._meta.app_label in self.view_data_apps and 
            model._meta.model_name.lower() in self.view_data_models):
            return 'view_data_db'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        允许数据分析相关模型之间的关系
        """
        view_data_set = {'view_data_db'}
        if obj1._state.db in view_data_set and obj2._state.db in view_data_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        确保数据分析相关模型只在 view_data_db 数据库中迁移
        """
        if app_label in self.view_data_apps and model_name and model_name.lower() in self.view_data_models:
            return db == 'view_data_db'
        elif db == 'view_data_db':
            return False
        return None