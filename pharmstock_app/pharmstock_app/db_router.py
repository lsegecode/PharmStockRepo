from threading import local

_thread_locals = local()

def get_current_db():
    """Obtiene la base de datos actual del thread local."""
    return getattr(_thread_locals, 'db', 'default')

def set_current_db(db_name):
    """Establece la base de datos para el thread actual."""
    _thread_locals.db = db_name


class AuthRouter:
    """
    Rutea los modelos de autenticación y sesiones a la base 'auth',
    y el resto a la base de datos asignada dinámicamente por usuario.
    """
    route_app_labels = {'auth', 'contenttypes', 'sessions', 'admin'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth'
        # Retorna la base de datos asignada al usuario actual
        return get_current_db()

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth'
        # Retorna la base de datos asignada al usuario actual
        return get_current_db()

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir relaciones entre auth y cualquier otra base
        db_set = {'auth', 'default', 'eme_rcia', 'eme_ctes'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'auth'
        return db == 'default'