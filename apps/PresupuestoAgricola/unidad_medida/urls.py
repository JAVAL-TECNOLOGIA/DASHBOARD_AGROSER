from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoUnidadMedidaView.as_view(), name='presupuesto_agricola_unidad_medida'),

    # API CRUD para unidad_medida
    path('api/unidad-medida/', PresupuestoUnidadMedidaCRUDView.as_view(), name='presupuesto_agricola_unidad_medida_api'),
    path('api/unidad-medida/<int:id_unidad>/', PresupuestoUnidadMedidaCRUDView.as_view(), name='presupuesto_agricola_unidad_medida_api_detail'),

]