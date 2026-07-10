from django.urls import path

from .views import *

urlpatterns = [
    path('', produccion_uva.as_view(), name='presupuesto_agricola_produccion_uva'),
    path('api/list_produva/', list_produva, name='api_list_produva'),
    path('produccionuva1_presupuesto_dl/', presupuesto_dl.as_view(), name='presupuesto_agricola_presupuesto_dl'),

    path('api/fundos_por_usuario/', ProdFundosPorUsuarioCampaniaAPI.as_view(),name='presupuesto_agricola_fundos_usuario'),
    path("api/produccion_nuevo/", GuardarProduccionNuevo.as_view(), name="guardar_mapeo_nuevo"),
    path("api/produccion_campania/", get_produccion_campania, name="get_produccion_campania"),


]
