from django.contrib import admin
from django.urls import path
from stock import views as stock_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', stock_views.home, name='home'),

    # Ventana 1
    path('farm-central/', stock_views.farm_central_view, name='farm_central'),
    path('farm-central/row/<str:codigo>/', stock_views.farm_central_update_row, name='farm_central_update_row'),
    path('farm-central/save-all/', stock_views.farm_central_save_all, name='farm_central_save_all'),
    path('farm-central/only/<str:col>/', stock_views.farm_central_onecol_view, name='farm_central_onecol'),

    # Ventana 2
    path('maletin/', stock_views.maletin_view, name='maletin'),
    path('maletin/row/<str:codigo>/<str:funcion>/', stock_views.maletin_update_row, name='maletin_update_row'),
    path('maletin/save-all/', stock_views.maletin_save_all, name='maletin_save_all'),
    path('maletin/only/<str:col>/', stock_views.maletin_onecol_view, name='maletin_onecol'),

]
