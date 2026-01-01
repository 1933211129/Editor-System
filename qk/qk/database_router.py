class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'qikan' and model._meta.model_name == 'mail':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'qikan' and model._meta.model_name == 'mail':
            return 'default'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # 禁止对 Mail 模型进行迁移
        if app_label == 'qikan' and model_name == 'mail':
            return False
        return True 