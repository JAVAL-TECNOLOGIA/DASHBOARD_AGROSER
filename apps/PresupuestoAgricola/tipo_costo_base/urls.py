from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoTipoTrabajoView.as_view(), name='presupuesto_agricola_tipo_costo_base'),

    path('tipo-costo/api/', PresupuestoTipoCostoCRUDView.as_view(), name='tipo-costo-list'),
    path('tipo-costo/api/<int:id_tipo_costo>/', PresupuestoTipoCostoCRUDView.as_view(), name='tipo-costo-detail'),
    path('tipo-calculo/api/', PresupuestoTipoCalculoListView.as_view(), name='tipo-calculo-list'),
]