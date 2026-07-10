from django.urls import path

from .views import *

urlpatterns = [

    path('', PresupuestoAgricolaView.as_view(), name='presupuesto_agricola_presupuesto_in'),

    path('api/', PresupuestoCRUDView.as_view(), name='api_presupuesto'),
    path('api/<int:id_presupuesto>/', PresupuestoCRUDView.as_view(),
         name='api_presupuesto_detalle'),

    path('lotes-asignados/api/', LotesAsignadosAPI.as_view(), name='lotes-asignados-api'),
    path('parametro-costo/api/', ParametroCostoAPI.as_view(), name='parametro-costo-api'),

    path('detalle/api/<int:id_presupuesto>/', PresupuestoDetalleAPI.as_view(),
         name='presupuesto_detalle_api'),
    # path('config-ttrab/api/<int:id_config>/', ConfigTipoTrabajoAPI.as_view(), name='config-ttrab-api'),
    path('config-ttrab/api/<int:id_config>/', ConfigTipoTrabajoAPI.as_view()),

    path('ingenieros/', listar_ingenieros, name='listar_ingenieros'),

]