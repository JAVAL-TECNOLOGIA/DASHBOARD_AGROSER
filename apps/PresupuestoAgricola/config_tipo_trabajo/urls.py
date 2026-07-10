from django.urls import path

from .views import *

urlpatterns = [
    path('', config_tipo_trabajo.as_view(), name='presupuesto_agricola_config_tipo_trabajo'),
    path('api/config-tipo-trabajo/', ConfigTipoTrabajoCRUDView.as_view(), name='presupuesto_agricola_config_tipo_trabajo_api'),
    path('api/config-tipo-trabajo/delete/<str:id_config_ttrab>/', deleteConfigTipoTrabajo,
         name='presupuesto_agricola_config_tipo_trabajo_api_delete'),
    path('api/config-tipo-trabajo/<str:id_config_ttrab>/', ConfigTipoTrabajoCRUDView.as_view(),
         name='presupuesto_agricola_config_tipo_trabajo_api_detail'),
]
