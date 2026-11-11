from django.utils.deprecation import MiddlewareMixin
from pharmstock_app.db_router import set_current_db

class DatabaseRoutingMiddleware(MiddlewareMixin):
    """
    Middleware que asigna la base de datos SQL Server según el usuario logueado.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # Mapeo de usuarios a bases de datos
            user_database_map = {
                'JOperativa': 'eme_rcia',
                'JOperativaCtes': 'eme_ctes',
            }
            
            # Si es superuser, usar la base default
            if request.user.is_superuser:
                db_name = 'default'
            else:
                # Asignar la base de datos según el usuario
                db_name = user_database_map.get(
                    request.user.username, 
                    'default'
                )
            
            # Guardar en sesión y establecer en thread local
            request.session['database'] = db_name
            set_current_db(db_name)
        else:
            # Usuario no autenticado usa default
            set_current_db('default')
            
        return None