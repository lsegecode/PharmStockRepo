from django.utils.deprecation import MiddlewareMixin
from pharmstock_app.db_router import set_current_db

class DatabaseRoutingMiddleware(MiddlewareMixin):
    """
    Middleware que asigna la base de datos SQL Server según el usuario logueado.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Mapeo de usuarios a bases de datos (en minúsculas para mayor robustez)
            user_database_map = {
                'joperativa': 'eme_rcia',
                'joperativactes': 'eme_ctes',
            }
            
            # Obtener el nombre de usuario en minúsculas
            username_lower = request.user.username.lower()
            
            # Priorizamos el mapeo explícito de base de datos
            db_name = user_database_map.get(username_lower)

            if not db_name:
                # Si no está en el mapa, superuser usa 'default', otros también
                db_name = 'default'
            
            # Guardar en sesión y establecer en thread local
            request.session['database'] = db_name
            set_current_db(db_name)
        else:
            # Usuario no autenticado usa default
            set_current_db('default')
            
        return None