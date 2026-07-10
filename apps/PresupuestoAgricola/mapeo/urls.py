from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path('', mapeo.as_view(), name='presupuesto_agricola_mapeo'),

    path('api/tipo_planta/', tipo_planta_list, name='api_tipo_planta'),
    # MAPEO DE PLANTAS POR LOTE
    path('api/mapeo/', MapeoCRUDView.as_view(), name='api_mapeo'),
    path('api/mapeo_todo/', mapeo_todo_api, name='api_mapeo_todo'),
    path("api/mapeo_nuevo/", GuardarMapeoNuevo.as_view(), name="guardar_mapeo_nuevo"),
    # API para campañas
    path('api/campanias/', CampaniasListView.as_view(), name='campanias_list'),

    path('api/fundos_por_usuario/', FundosPorUsuarioCampaniaAPI.as_view(), name='presupuesto_agricola_fundos_usuario'),

    path('api/tipo_planta/', tipo_planta_list, name='api_tipo_planta'),

    path('api/mapeo_resumen_campania/', views.get_mapeo_resumen_campania, name='mapeo_resumen_campania'),
]
