class AuthRouter:
    """
    Rutea los modelos de autenticación y sesiones a la base 'auth',
    y el resto a la base 'default' (SQL Server).
    """
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._state.db in ('auth', 'default')
            and obj2._state.db in ('auth', 'default')
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'auth'
        return db == 'default'
